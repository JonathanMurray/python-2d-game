import random

from pythongame.core.ability_effects import register_ability_effect
from pythongame.core.buff_effects import get_buff_effect, register_buff_effect, AbstractBuffEffect
from pythongame.core.common import Sprite, AbilityType, Millis, sum_of_vectors, NpcType, Direction, BuffType
from pythongame.core.damage_interactions import deal_npc_damage_to_npc
from pythongame.core.game_data import register_ability_data, AbilityData, UiIconSprite, \
    NON_PLAYER_CHARACTERS, register_npc_data, NpcData, SpriteSheet, register_entity_sprite_map, \
    register_ui_icon_sprite_path
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind
from pythongame.core.entity_creation import create_npc
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.pathfinding.npc_pathfinding import NpcPathfinder
from pythongame.core.visual_effects import VisualLine, VisualCircle


def _apply_ability(game_state: GameState) -> bool:
    player_entity = game_state.player_entity

    summon_size = NON_PLAYER_CHARACTERS[NpcType.PLAYER_SUMMON].size
    player_size = game_state.player_entity.w, game_state.player_entity.h
    candidate_relative_positions = [
        (0, - summon_size[1]),  # top
        (player_size[0], - summon_size[1]),  # top right
        (player_size[0], 0),  # right
        (player_size[0], player_size[1]),  # down right
        (0, player_size[1]),  # down
        (-summon_size[0], player_size[1]),  # down left
        (-summon_size[0], 0),  # left
        (-summon_size[0], -summon_size[1])  # top left
    ]
    for relative_pos in candidate_relative_positions:
        summon_pos = sum_of_vectors(player_entity.get_position(), relative_pos)
        summon = create_npc(NpcType.PLAYER_SUMMON, summon_pos)
        is_valid_pos = not game_state.would_entity_collide_if_new_pos(summon.world_entity, summon_pos)
        if is_valid_pos:
            game_state.remove_all_non_enemy_npcs()
            game_state.add_non_player_character(summon)
            summon.gain_buff_effect(get_buff_effect(BuffType.SUMMON_DIE_AFTER_DURATION), Millis(50000))
            game_state.visual_effects.append(
                VisualCircle((200, 200, 30), player_entity.get_position(), 40, 70, Millis(140), 3))
            game_state.visual_effects.append(VisualCircle((200, 200, 30), summon_pos, 40, 70, Millis(140), 3))
            return True
    return False


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._attack_interval = 1000
        self._time_since_attack = self._attack_interval
        self._update_path_interval = 900
        self._time_since_updated_path = random.randint(0, self._update_path_interval)
        self.pathfinder = NpcPathfinder(global_path_finder)
        self.next_waypoint = None
        self._reevaluate_next_waypoint_direction_interval = 1000
        self._time_since_reevaluated = self._reevaluate_next_waypoint_direction_interval

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):
        self._time_since_updated_path += time_passed
        self._time_since_reevaluated += time_passed
        self._time_since_attack += time_passed

        summon_entity = npc.world_entity

        if self._time_since_updated_path > self._update_path_interval:
            self._time_since_updated_path = 0
            nearby_enemies = game_state.get_enemies_within_x_y_distance_of(300, npc.world_entity.get_position())
            if nearby_enemies:
                target_entity = nearby_enemies[0].world_entity
            else:
                target_entity = game_state.player_entity
            self.pathfinder.update_path_towards_target(summon_entity, game_state, target_entity)

        new_next_waypoint = self.pathfinder.get_next_waypoint_along_path(summon_entity)

        should_update_waypoint = self.next_waypoint != new_next_waypoint
        if self._time_since_reevaluated > self._reevaluate_next_waypoint_direction_interval:
            self._time_since_reevaluated = 0
            should_update_waypoint = True

        if should_update_waypoint:
            self.next_waypoint = new_next_waypoint
            if self.next_waypoint:
                direction = self.pathfinder.get_dir_towards_considering_collisions(
                    game_state, summon_entity, self.next_waypoint)
                _move_in_dir(summon_entity, direction)
            else:
                summon_entity.set_not_moving()
        if self._time_since_attack > self._attack_interval:
            self._time_since_attack = 0
            nearby_enemies = game_state.get_enemies_within_x_y_distance_of(100, summon_entity.get_position())
            if nearby_enemies:
                damage_amount = 3
                target = nearby_enemies[0]
                deal_npc_damage_to_npc(game_state, target, damage_amount)
                game_state.visual_effects.append(
                    VisualLine((220, 0, 0), summon_entity.get_center_position(),
                               target.world_entity.get_center_position(), Millis(100), damage_amount))


def _move_in_dir(enemy_entity, direction):
    if direction:
        enemy_entity.set_moving_in_dir(direction)
    else:
        enemy_entity.set_not_moving()


class DieAfterDuration(AbstractBuffEffect):

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_npc.lose_all_health()

    def get_buff_type(self):
        return BuffType.SUMMON_DIE_AFTER_DURATION


def register_summon_ability():
    ability_type = AbilityType.SUMMON
    register_ability_effect(ability_type, _apply_ability)
    ui_icon_sprite = UiIconSprite.ABILITY_SUMMON
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/icon_ability_summon.png")
    description = "Follows you and attacks nearby enemies"
    cooldown = Millis(30000)
    mana_cost = 25
    register_ability_data(ability_type,
                          AbilityData("Summon Dragonwhelp", ui_icon_sprite, mana_cost, cooldown, description, None))

    summoned_npc_type = NpcType.PLAYER_SUMMON
    summon_sprite = Sprite.PLAYER_SUMMON

    health_regen = 0.6
    move_speed = 0.14
    health = 28
    register_npc_data(summoned_npc_type,
                      NpcData(summon_sprite, (32, 32), health, health_regen, move_speed, 0, False, False, None, None,
                              None))
    register_npc_behavior(summoned_npc_type, NpcMind)

    summon_sprite_sheet = SpriteSheet("resources/graphics/monsters_spritesheet.png")
    summon_original_size = (32, 32)
    summon_scaled_sprite_size = (52, 52)
    summon_indices_by_dir = {
        Direction.DOWN: [(x, 0) for x in range(9, 12)],
        Direction.LEFT: [(x, 1) for x in range(9, 12)],
        Direction.RIGHT: [(x, 2) for x in range(9, 12)],
        Direction.UP: [(x, 3) for x in range(9, 12)]
    }
    register_entity_sprite_map(summon_sprite, summon_sprite_sheet, summon_original_size,
                               summon_scaled_sprite_size, summon_indices_by_dir, (-10, -20))
    register_buff_effect(BuffType.SUMMON_DIE_AFTER_DURATION, DieAfterDuration)
