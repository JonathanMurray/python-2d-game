import random
from typing import Dict, Type, Optional, List

from pythongame.core.common import *
from pythongame.core.damage_interactions import deal_npc_damage, DamageType
from pythongame.core.enemy_target_selection import EnemyTarget, get_target
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.math import is_x_and_y_within_distance, get_perpendicular_directions
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.pathfinding.npc_pathfinding import NpcPathfinder
from pythongame.core.sound_player import play_sound


class DialogOptionGraphics:
    # TODO handle option icons
    def __init__(self, text_header: str, text_detailed: str, ui_icon_sprite: UiIconSprite):
        self.text_header = text_header
        self.text_detailed = text_detailed
        self.ui_icon_sprite = ui_icon_sprite


# Used to display dialog from an npc along with the NPC's portrait
class DialogGraphics:
    def __init__(self, portrait_icon_sprite: PortraitIconSprite, text_body: str, options: List[DialogOptionGraphics],
                 active_option_index: int):
        self.portrait_icon_sprite = portrait_icon_sprite
        self.text_body = text_body
        self.options = options
        self.active_option_index = active_option_index


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
        self._attack_interval = attack_interval
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
            # TODO Only reset attack cooldown when enemy was in range to actually attack
            self._time_since_attack = 0
            if not is_player_invisible:
                enemy_position = enemy_entity.get_center_position()
                target_center_pos = target.entity.get_center_position()
                if is_x_and_y_within_distance(enemy_position, target_center_pos, 80):
                    deal_npc_damage(self.damage_amount, DamageType.PHYSICAL, game_state, enemy_entity, npc, target)


def _move_in_dir(enemy_entity, direction):
    if direction:
        enemy_entity.set_moving_in_dir(direction)
    else:
        enemy_entity.set_not_moving()


class AbstractNpcAction:

    # perform action, and optionally return a message to be displayed
    def act(self, game_state: GameState) -> Optional[str]:
        pass


class SellConsumableNpcAction(AbstractNpcAction):
    def __init__(self, cost: int, consumable_type: ConsumableType, name: str):
        self.cost = cost
        self.consumable_type = consumable_type
        self.name = name

    def act(self, game_state: GameState):
        player_state = game_state.player_state
        can_afford = player_state.money >= self.cost
        has_space = player_state.consumable_inventory.has_space_for_more()
        if not can_afford:
            play_sound(SoundId.WARNING)
            return "Not enough gold!"
        if not has_space:
            play_sound(SoundId.WARNING)
            return "Not enough space!"
        player_state.money -= self.cost
        player_state.consumable_inventory.add_consumable(self.consumable_type)
        play_sound(SoundId.EVENT_PURCHASED_SOMETHING)
        return "Bought " + self.name


class DialogOptionData:
    def __init__(self, text_header: str, text_detailed: str, action: Optional[AbstractNpcAction],
                 ui_icon_sprite: UiIconSprite):
        self.text_header = text_header
        self.text_detailed = text_detailed
        self.action = action
        self.ui_icon_sprite = ui_icon_sprite


class DialogData:
    def __init__(self, portrait_icon_sprite: PortraitIconSprite, text_body: str, options: List[DialogOptionData]):
        self.portrait_icon_sprite = portrait_icon_sprite
        self.text_body = text_body
        self.options = options


_npc_mind_constructors: Dict[NpcType, Type[AbstractNpcMind]] = {}

_npc_dialog_data: Dict[NpcType, DialogData] = {}


def register_npc_behavior(npc_type: NpcType, mind_constructor: Type[AbstractNpcMind]):
    _npc_mind_constructors[npc_type] = mind_constructor


def create_npc_mind(npc_type: NpcType, global_path_finder: GlobalPathFinder):
    constructor = _npc_mind_constructors[npc_type]
    return constructor(global_path_finder)


def register_npc_dialog_data(npc_type: NpcType, data: DialogData):
    _npc_dialog_data[npc_type] = data


def invoke_npc_action(npc_type: NpcType, option_index: int, game_state: GameState) -> Optional[str]:
    action = _npc_dialog_data[npc_type].options[option_index].action
    if not action:
        return None
    optional_message = action.act(game_state)
    return optional_message


def has_npc_dialog(npc_type: NpcType) -> bool:
    return npc_type in _npc_dialog_data


def get_dialog_graphics(npc_type: NpcType, active_option_index: int) -> DialogGraphics:
    data = _npc_dialog_data[npc_type]
    options_graphics = [DialogOptionGraphics(o.text_header, o.text_detailed, o.ui_icon_sprite) for o in data.options]
    return DialogGraphics(data.portrait_icon_sprite, data.text_body, options_graphics, active_option_index)


def get_dialog_data(npc_type: NpcType) -> DialogData:
    return _npc_dialog_data[npc_type]
