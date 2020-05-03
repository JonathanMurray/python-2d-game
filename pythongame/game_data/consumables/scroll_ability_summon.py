from pythongame.core.buff_effects import get_buff_effect, AbstractBuffEffect, register_buff_effect
from pythongame.core.common import *
from pythongame.core.consumable_effects import ConsumableWasConsumed, \
    register_consumable_effect, ConsumableFailedToBeConsumed
from pythongame.core.damage_interactions import deal_npc_damage_to_npc
from pythongame.core.entity_creation import create_npc
from pythongame.core.game_data import register_entity_sprite_initializer, register_ui_icon_sprite_path, \
    register_consumable_data, ConsumableData, POTION_ENTITY_SIZE, ConsumableCategory, \
    NON_PLAYER_CHARACTERS, NpcData, register_npc_data, register_entity_sprite_map
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.math import *
from pythongame.core.npc_behaviors import AbstractNpcMind, register_npc_behavior
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.pathfinding.npc_pathfinding import NpcPathfinder
from pythongame.core.view.image_loading import SpriteInitializer, SpriteSheet
from pythongame.core.visual_effects import VisualCircle, VisualLine
from pythongame.core.world_entity import WorldEntity

DURATION_SUMMON = Millis(50000)


def _apply_scroll(game_state: GameState):
    player_entity = game_state.game_world.player_entity

    summon_size = NON_PLAYER_CHARACTERS[NpcType.PLAYER_SUMMON_DRAGON].size
    player_size = game_state.game_world.player_entity.pygame_collision_rect.w, game_state.game_world.player_entity.h
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
        summon = create_npc(NpcType.PLAYER_SUMMON_DRAGON, summon_pos)
        is_valid_pos = not game_state.game_world.would_entity_collide_if_new_pos(summon.world_entity, summon_pos)
        if is_valid_pos:
            game_state.game_world.remove_all_player_summons()
            game_state.game_world.add_non_player_character(summon)
            summon.gain_buff_effect(get_buff_effect(BuffType.SUMMON_DIE_AFTER_DURATION), DURATION_SUMMON)
            game_state.game_world.visual_effects.append(
                VisualCircle((200, 200, 30), player_entity.get_position(), 40, 70, Millis(140), 3))
            game_state.game_world.visual_effects.append(
                VisualCircle((200, 200, 30), summon_pos, 40, 70, Millis(140), 3))
            return ConsumableWasConsumed("Summoned dragon")
    return ConsumableFailedToBeConsumed("No space to summon dragon")


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
            nearby_enemies = game_state.game_world.get_enemies_within_x_y_distance_of(300,
                                                                                      npc.world_entity.get_position())
            if nearby_enemies:
                target_entity = nearby_enemies[0].world_entity
            else:
                target_entity = game_state.game_world.player_entity
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
            nearby_enemies = game_state.game_world.get_enemies_within_x_y_distance_of(100, summon_entity.get_position())
            if nearby_enemies:
                damage_amount = 3
                target = nearby_enemies[0]
                deal_npc_damage_to_npc(game_state, target, damage_amount)
                game_state.game_world.visual_effects.append(
                    VisualLine((220, 0, 0), summon_entity.get_center_position(),
                               target.world_entity.get_center_position(), Millis(100), damage_amount))


def _move_in_dir(enemy_entity, direction):
    if direction:
        enemy_entity.set_moving_in_dir(direction)
    else:
        enemy_entity.set_not_moving()


class DieAfterDuration(AbstractBuffEffect):

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_npc.health_resource.set_zero()

    def get_buff_type(self):
        return BuffType.SUMMON_DIE_AFTER_DURATION


def register_summon_scroll():
    consumable_type = ConsumableType.SCROLL_SUMMON_DRAGON
    sprite = Sprite.CONSUMABLE_SCROLL_SUMMON_DRAGON
    ui_icon_sprite = UiIconSprite.CONSUMABLE_SCROLL_SUMMON_DRAGON

    register_consumable_effect(consumable_type, _apply_scroll)
    image_path = "resources/graphics/icon_scroll_ability_summon.png"
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_path, POTION_ENTITY_SIZE))
    register_ui_icon_sprite_path(ui_icon_sprite, image_path)
    description = "Summon a dragonling to fight for you (" + str(int(DURATION_SUMMON / 1000)) + "s)"
    data = ConsumableData(ui_icon_sprite, sprite, "Dragon's scroll", description, ConsumableCategory.OTHER,
                          SoundId.CONSUMABLE_POTION)
    register_consumable_data(consumable_type, data)

    summoned_npc_type = NpcType.PLAYER_SUMMON_DRAGON
    summon_sprite = Sprite.PLAYER_SUMMON_DRAGON

    health_regen = 0.6
    move_speed = 0.14
    health = 28
    npc_data = NpcData.player_summon(summon_sprite, (32, 32), health, health_regen, move_speed)
    register_npc_data(summoned_npc_type, npc_data)
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
