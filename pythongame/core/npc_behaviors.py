from typing import Type, Dict

from pythongame.core.common import *
from pythongame.core.damage_interactions import deal_npc_damage, DamageType
from pythongame.core.enemy_target_selection import EnemyTarget, get_target
from pythongame.core.game_data import CONSUMABLES, get_item_data_by_type
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity, QuestId, Quest
from pythongame.core.item_effects import try_add_item_to_inventory
from pythongame.core.math import is_x_and_y_within_distance, get_perpendicular_directions
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.pathfinding.npc_pathfinding import NpcPathfinder
from pythongame.core.sound_player import play_sound
from pythongame.scenes_game.game_ui_view import GameUiView


class AbstractNpcMind:

    def __init__(self, _global_path_finder: GlobalPathFinder):
        pass

    def control_npc(self,
                    game_state: GameState,
                    npc: NonPlayerCharacter,
                    player_entity: WorldEntity,
                    is_player_invisible: bool,
                    time_passed: Millis):
        pass


class MeleeEnemyNpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder, attack_interval: Millis, damage_amount: int,
                 chance_to_stray_from_path: float, update_path_interval: Millis):
        super().__init__(global_path_finder)
        self._base_attack_interval = attack_interval
        self._attack_interval = None
        self.randomize_attack_interval()
        self._time_since_attack = self._attack_interval
        self._update_path_interval = update_path_interval
        self._time_since_updated_path = self._update_path_interval
        self.pathfinder = NpcPathfinder(global_path_finder)
        self.next_waypoint = None
        self._reevaluate_next_waypoint_direction_interval = 1000
        self._time_since_reevaluated = self._reevaluate_next_waypoint_direction_interval
        self.damage_amount = damage_amount
        self.chance_to_stray_from_path = chance_to_stray_from_path
        self._is_in_melee_with_target = False

    def randomize_attack_interval(self):
        self._attack_interval = self._base_attack_interval + random.randint(-250, 250)

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):
        self._time_since_attack += time_passed
        self._time_since_updated_path += time_passed
        self._time_since_reevaluated += time_passed

        enemy_entity = npc.world_entity
        target: EnemyTarget = get_target(enemy_entity, game_state)

        if self._time_since_updated_path > self._update_path_interval:
            self._time_since_updated_path = 0
            if not is_player_invisible:
                self.pathfinder.update_path_towards_target(enemy_entity, game_state, target.entity)

        new_next_waypoint = self.pathfinder.get_next_waypoint_along_path(enemy_entity)

        should_update_waypoint = self.next_waypoint != new_next_waypoint
        if self._time_since_reevaluated > self._reevaluate_next_waypoint_direction_interval:
            self._time_since_reevaluated = 0
            should_update_waypoint = True

        if should_update_waypoint:
            self.next_waypoint = new_next_waypoint
            if self.next_waypoint:
                direction = self.pathfinder.get_dir_towards_considering_collisions(
                    game_state, enemy_entity, self.next_waypoint)
                if random.random() < self.chance_to_stray_from_path and direction:
                    direction = random.choice(get_perpendicular_directions(direction))
                _move_in_dir(enemy_entity, direction)
            else:
                enemy_entity.set_not_moving()

        if self._time_since_attack > self._attack_interval:
            if not is_player_invisible:
                enemy_position = enemy_entity.get_center_position()
                target_center_pos = target.entity.get_center_position()
                if is_x_and_y_within_distance(enemy_position, target_center_pos, 80):
                    self._time_since_attack = 0
                    self.randomize_attack_interval()
                    deal_npc_damage(self.damage_amount, DamageType.PHYSICAL, game_state, enemy_entity, npc, target)


def _move_in_dir(enemy_entity, direction):
    if direction:
        enemy_entity.set_moving_in_dir(direction)
    else:
        enemy_entity.set_not_moving()


class AbstractNpcAction:

    # perform action, and optionally return a message to be displayed
    def on_select(self, game_state: GameState) -> Optional[str]:
        pass

    # is called when the option is selected/hovered in the dialog
    def on_hover(self, game_state: GameState, ui_view: GameUiView):
        pass

    # is called when the option stops being selected/hovered in the dialog
    def on_blur(self, game_state: GameState, ui_view: GameUiView):
        pass


class SellConsumableNpcAction(AbstractNpcAction):
    def __init__(self, cost: int, consumable_type: ConsumableType, name: str):
        self.cost = cost
        self.consumable_type = consumable_type
        self.name = name

    def on_select(self, game_state: GameState):
        player_state = game_state.player_state
        can_afford = player_state.money >= self.cost
        has_space = player_state.consumable_inventory.has_space_for_more()
        if not can_afford:
            play_sound(SoundId.WARNING)
            return "Not enough gold!"
        if not has_space:
            play_sound(SoundId.WARNING)
            return "Not enough space!"
        player_state.modify_money(-self.cost)
        player_state.consumable_inventory.add_consumable(self.consumable_type)
        play_sound(SoundId.EVENT_PURCHASED_SOMETHING)
        return "Bought " + self.name


class SellItemNpcAction(AbstractNpcAction):
    def __init__(self, cost: int, item_id: ItemId, name: str):
        self.cost = cost
        self.item_id = item_id
        self.name = name
        self.item_id = item_id

    def on_select(self, game_state: GameState):
        player_state = game_state.player_state
        can_afford = player_state.money >= self.cost
        if not can_afford:
            play_sound(SoundId.WARNING)
            return "Not enough gold!"

        did_add_item = try_add_item_to_inventory(game_state, self.item_id)
        if not did_add_item:
            play_sound(SoundId.WARNING)
            return "Not enough space!"

        player_state.modify_money(- self.cost)
        play_sound(SoundId.EVENT_PURCHASED_SOMETHING)
        return "Bought " + self.name


class BuyItemNpcAction(AbstractNpcAction):

    def __init__(self, item_id: ItemId, price: int, name: str):
        self.item_id = item_id
        self.price = price
        self.name = name

    def on_select(self, game_state: GameState) -> Optional[str]:
        player_has_it = game_state.player_state.item_inventory.has_item_in_inventory(self.item_id)
        if player_has_it:
            game_state.player_state.item_inventory.lose_item_from_inventory(self.item_id)
            game_state.player_state.modify_money(self.price)
            play_sound(SoundId.EVENT_SOLD_SOMETHING)
            return "Sold " + self.name
        else:
            play_sound(SoundId.WARNING)
            return "You don't have that!"

    def on_hover(self, game_state: GameState, ui_view: GameUiView):
        ui_view.set_inventory_highlight(self.item_id)

    def on_blur(self, game_state: GameState, ui_view: GameUiView):
        ui_view.remove_inventory_highlight()


_npc_mind_constructors: Dict[NpcType, Type[AbstractNpcMind]] = {}

_npc_dialog_data: Dict[NpcType, Callable[[GameState], DialogData]] = {}

_quests: Dict[QuestId, Quest] = {}


def register_quest(quest_id: QuestId, quest: Quest):
    _quests[quest_id] = quest


def get_quest(quest_id: QuestId):
    return _quests[quest_id]


def register_npc_behavior(npc_type: NpcType, mind_constructor: Type[AbstractNpcMind]):
    _npc_mind_constructors[npc_type] = mind_constructor


def create_npc_mind(npc_type: NpcType, global_path_finder: GlobalPathFinder):
    constructor = _npc_mind_constructors[npc_type]
    return constructor(global_path_finder)


def register_npc_dialog_data(npc_type: NpcType, data: DialogData):
    _npc_dialog_data[npc_type] = (lambda _: data)


def register_conditional_npc_dialog_data(npc_type: NpcType, get_data: Callable[[GameState], DialogData]):
    _npc_dialog_data[npc_type] = get_data


def select_npc_action(npc_type: NpcType, option_index: int, game_state: GameState) -> Optional[str]:
    data = _npc_dialog_data[npc_type](game_state)
    action = data.options[option_index].action
    if not action:
        return None
    optional_message = action.on_select(game_state)
    return optional_message


def hover_npc_action(npc_type: NpcType, option_index: int, game_state: GameState, ui_view: GameUiView):
    data = _npc_dialog_data[npc_type](game_state)
    action = data.options[option_index].action
    if action:
        action.on_hover(game_state, ui_view)


def blur_npc_action(npc_type: NpcType, option_index: int, game_state: GameState, ui_view: GameUiView):
    data = _npc_dialog_data[npc_type](game_state)
    action = data.options[option_index].action
    if action:
        action.on_blur(game_state, ui_view)


def has_npc_dialog(npc_type: NpcType) -> bool:
    return npc_type in _npc_dialog_data


def get_dialog_data(npc_type: NpcType, game_state: GameState) -> DialogData:
    return _npc_dialog_data[npc_type](game_state)


def buy_consumable_option(consumable_type: ConsumableType, cost: int):
    data = CONSUMABLES[consumable_type]
    name_formatter = "{:<25}"
    buy_prompt = "> "
    cost_formatter = "[{} gold]"
    return DialogOptionData(buy_prompt + name_formatter.format(data.name) + cost_formatter.format(cost),
                            "buy",
                            SellConsumableNpcAction(cost, consumable_type, data.name.lower()),
                            data.icon_sprite,
                            data.name,
                            data.description)


def buy_item_option(item_id: ItemId, cost: int):
    item_type = item_type_from_id(item_id)
    data = get_item_data_by_type(item_type)
    name_formatter = "{:<25}"
    buy_prompt = "> "
    cost_formatter = "[{} gold]"
    item_name = data.name
    icon_sprite = data.icon_sprite
    description_lines = data.custom_description_lines
    return DialogOptionData(buy_prompt + name_formatter.format(item_name) + cost_formatter.format(cost),
                            "buy",
                            SellItemNpcAction(cost, item_id, item_name.lower()),
                            icon_sprite,
                            item_name,
                            ", ".join(description_lines))


def sell_item_option(item_id: ItemId, price: int, detail_body: str):
    item_type = item_type_from_id(item_id)
    name_formatter = "{:<13}"
    cost_formatter = "[{} gold]"
    sell_prompt = "> "
    data = get_item_data_by_type(item_type)
    item_name = data.name
    icon_sprite = data.icon_sprite
    return DialogOptionData(sell_prompt + name_formatter.format(item_name) + cost_formatter.format(price), "sell",
                            BuyItemNpcAction(item_id, price, item_name.lower()),
                            icon_sprite, item_name, detail_body)
