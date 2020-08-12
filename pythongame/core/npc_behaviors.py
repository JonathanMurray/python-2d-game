from typing import Type, Dict

from pythongame.core.common import *
from pythongame.core.damage_interactions import deal_npc_damage, DamageType
from pythongame.core.enemy_target_selection import EnemyTarget, get_target
from pythongame.core.game_data import CONSUMABLES
from pythongame.core.game_data import NON_PLAYER_CHARACTERS
from pythongame.core.game_state import GameState, NonPlayerCharacter, Projectile
from pythongame.core.hero_upgrades import reset_talents
from pythongame.core.item_data import create_item_description
from pythongame.core.item_data import get_item_data_by_type
from pythongame.core.math import get_perpendicular_directions, get_position_from_center_position, \
    translate_in_direction, get_directions_to_position
from pythongame.core.math import is_x_and_y_within_distance
from pythongame.core.math import random_direction, sum_of_vectors, \
    rect_from_corners
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.pathfinding.npc_pathfinding import NpcPathfinder
from pythongame.core.quests import QuestId, Quest
from pythongame.core.sound_player import play_sound
from pythongame.core.visual_effects import VisualCircle
from pythongame.core.world_entity import WorldEntity
from pythongame.scenes.scenes_game.game_ui_view import GameUiView


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
        if npc.stun_status.is_stunned():
            return
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


def _move_in_dir(enemy_entity: WorldEntity, direction: Direction):
    if direction:
        enemy_entity.set_moving_in_dir(direction)
    else:
        enemy_entity.set_not_moving()


# TRAIT = a reusable part of an enemy's behaviour

class EnemyTrait:
    def update(self, npc: NonPlayerCharacter, game_state: GameState, time_passed: Millis):
        raise Exception("Must be overridden by sub-class!")


class EnemySummonTrait(EnemyTrait):
    def __init__(self, max_summons: int, summon_npc_types: List[NpcType], summon_cd_interval: Tuple[Millis, Millis],
                 create_npc: Callable[[NpcType, Tuple[int, int]], NonPlayerCharacter]):
        self._max_summons = max_summons
        self._summon_npc_types = summon_npc_types
        self._summon_cd_interval = summon_cd_interval
        self._time_since_summoning = 0
        self._summoning_cooldown = self._random_summoning_cooldown()
        self._alive_summons = []
        self._create_npc = create_npc  # We inject this method as we cannot depend on entity_creation.py from here

    def update(self, npc: NonPlayerCharacter, game_state: GameState, time_passed: Millis):
        self._time_since_summoning += time_passed
        if self._time_since_summoning > self._summoning_cooldown:
            necro_center_pos = npc.world_entity.get_center_position()
            self._time_since_summoning = 0
            self._alive_summons = [summon for summon in self._alive_summons
                                   if summon in game_state.game_world.non_player_characters]
            if len(self._alive_summons) < self._max_summons:
                relative_pos_from_summoner = (random.randint(-150, 150), random.randint(-150, 150))
                summon_center_pos = sum_of_vectors(necro_center_pos, relative_pos_from_summoner)
                summon_type = random.choice(self._summon_npc_types)
                summon_size = NON_PLAYER_CHARACTERS[summon_type].size
                summon_pos = game_state.game_world.get_within_world(
                    get_position_from_center_position(summon_center_pos, summon_size), summon_size)
                summon_enemy = self._create_npc(summon_type, summon_pos)
                is_wall_blocking = game_state.game_world.walls_state.does_rect_intersect_with_wall(
                    rect_from_corners(necro_center_pos, summon_center_pos))
                is_position_blocked = game_state.game_world.would_entity_collide_if_new_pos(summon_enemy.world_entity,
                                                                                            summon_pos)
                if not is_wall_blocking and not is_position_blocked:
                    self._summoning_cooldown = self._random_summoning_cooldown()
                    game_state.game_world.add_non_player_character(summon_enemy)
                    self._alive_summons.append(summon_enemy)
                    game_state.game_world.visual_effects.append(
                        VisualCircle((80, 150, 100), necro_center_pos, 40, 70, Millis(120), 3))
                    game_state.game_world.visual_effects.append(
                        VisualCircle((80, 150, 100), summon_center_pos, 40, 70, Millis(120), 3))
                    play_sound(SoundId.ENEMY_NECROMANCER_SUMMON)
                else:
                    # Failed to summon, so try again without waiting full duration
                    self._summoning_cooldown = 500
            else:
                self._summoning_cooldown = self._random_summoning_cooldown()

    def _random_summoning_cooldown(self):
        return random.randint(self._summon_cd_interval[0], self._summon_cd_interval[1])


class EnemyRandomWalkTrait(EnemyTrait):
    def __init__(self, interval: Millis):
        self._timer = PeriodicTimer(interval)

    def update(self, npc: NonPlayerCharacter, game_state: GameState, time_passed: Millis):
        if self._timer.update_and_check_if_ready(time_passed):
            if random.random() < 0.2:
                direction = random_direction()
                npc.world_entity.set_moving_in_dir(direction)
            else:
                npc.world_entity.set_not_moving()


class EnemyShootProjectileTrait(EnemyTrait):
    def __init__(self, create_projectile: Callable[[Tuple[int, int], Direction], Projectile],
                 projectile_size: Tuple[int, int], cooldown_interval: Tuple[Millis, Millis],
                 chance_to_shoot_other_direction: float, sound_id: SoundId):
        self._create_projectile = create_projectile
        self._projectile_size = projectile_size
        self._cooldown_interval = cooldown_interval
        self._chance_to_shoot_other_direction = chance_to_shoot_other_direction
        self._sound_id = sound_id
        self._time_since_attack = 0
        self._update_attack_interval()

    def update(self, npc: NonPlayerCharacter, game_state: GameState, time_passed: Millis):
        self._time_since_attack += time_passed
        if self._time_since_attack > self._attack_interval:
            self._time_since_attack = 0
            self._update_attack_interval()
            directions_to_player = get_directions_to_position(npc.world_entity,
                                                              game_state.game_world.player_entity.get_position())
            new_direction = directions_to_player[0]
            if random.random() < self._chance_to_shoot_other_direction and directions_to_player[1] is not None:
                new_direction = directions_to_player[1]
            npc.world_entity.direction = new_direction
            npc.world_entity.set_not_moving()
            center_position = npc.world_entity.get_center_position()
            distance_from_enemy = 35
            projectile_pos = translate_in_direction(
                get_position_from_center_position(center_position, self._projectile_size),
                npc.world_entity.direction, distance_from_enemy)
            projectile = self._create_projectile(projectile_pos, npc.world_entity.direction)
            game_state.game_world.projectile_entities.append(projectile)
            play_sound(self._sound_id)

    def _update_attack_interval(self):
        self._attack_interval = random.randint(self._cooldown_interval[0], self._cooldown_interval[1])


class AbstractNpcAction:

    # perform action, and optionally return a message to be displayed
    def on_select(self, game_engine: Any) -> Optional[str]:
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

    def on_select(self, game_engine: Any):
        player_state = game_engine.game_state.player_state
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

    def on_select(self, game_engine: Any):
        game_state = game_engine.game_state
        player_state = game_state.player_state
        can_afford = player_state.money >= self.cost
        if not can_afford:
            play_sound(SoundId.WARNING)
            return "Not enough gold!"

        did_add_item = game_engine.try_add_item_to_inventory(self.item_id)
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

    def on_select(self, game_engine: Any) -> Optional[str]:
        game_state = game_engine.game_state
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


class ResetTalentsNpcAction(AbstractNpcAction):

    def __init__(self, price: int):
        self.price = price

    def on_select(self, game_engine: Any) -> Optional[str]:
        game_state = game_engine.game_state
        player_state = game_state.player_state
        can_afford = player_state.money >= self.price
        if not can_afford:
            play_sound(SoundId.WARNING)
            return "Not enough gold!"

        player_state.modify_money(- self.price)
        reset_talents(game_state)
        play_sound(SoundId.EVENT_RESET_TALENT)
        return "Talents reset"


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


def select_npc_action(npc_type: NpcType, option_index: int, game_engine: Any) -> Optional[str]:
    data = _npc_dialog_data[npc_type](game_engine.game_state)
    action = data.options[option_index].action
    if not action:
        return None
    optional_message = action.on_select(game_engine)
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


def buy_consumable_option(consumable_type: ConsumableType, cost: int) -> DialogOptionData:
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


def buy_item_option(item_id: ItemId, cost: int) -> DialogOptionData:
    item_type = item_id.item_type
    data = get_item_data_by_type(item_type)
    name_formatter = "{:<35}"
    buy_prompt = "> "
    cost_formatter = "[{} gold]"
    item_name = item_id.name
    icon_sprite = data.icon_sprite
    description_lines = create_item_description(item_id)
    return DialogOptionData(buy_prompt + name_formatter.format(item_name) + cost_formatter.format(cost),
                            "buy",
                            SellItemNpcAction(cost, item_id, item_name.lower()),
                            icon_sprite,
                            item_name,
                            ", ".join([line.text for line in description_lines]))


def sell_item_option(item_id: ItemId, price: int, detail_body: str) -> DialogOptionData:
    item_type = item_id.item_type
    name_formatter = "{:<13}"
    cost_formatter = "[{} gold]"
    sell_prompt = "> "
    data = get_item_data_by_type(item_type)
    item_name = item_id.name
    icon_sprite = data.icon_sprite
    return DialogOptionData(sell_prompt + name_formatter.format(item_name) + cost_formatter.format(price), "sell",
                            BuyItemNpcAction(item_id, price, item_name.lower()),
                            icon_sprite, item_name, detail_body)


def reset_talents_option(price: int) -> DialogOptionData:
    return DialogOptionData(f"> Reset talents [{price} gold]", "reset", ResetTalentsNpcAction(price))
