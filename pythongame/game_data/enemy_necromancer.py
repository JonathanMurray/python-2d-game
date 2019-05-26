import random

from pythongame.core.common import Millis, random_direction, NpcType, Sprite, \
    is_x_and_y_within_distance, Direction, sum_of_vectors, get_position_from_center_position
from pythongame.core.game_data import register_npc_data, NpcData, SpriteSheet, register_entity_sprite_map, \
    NON_PLAYER_CHARACTERS
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind
from pythongame.core.npc_creation import create_npc
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.visual_effects import VisualLine, VisualCircle

SPRITE = Sprite.ENEMY_NECROMANCER
ENEMY_TYPE = NpcType.NECROMANCER


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._time_since_decision = 0
        self._decision_interval = 750
        self._time_since_summoning = 0
        self._max_summoning_cooldown = 8000
        self._summoning_cooldown = self._max_summoning_cooldown
        self._time_since_healing = 0
        self._healing_cooldown = 5000

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, _player_entity: WorldEntity,
                    _is_player_invisible: bool, time_passed: Millis):
        self._time_since_decision += time_passed
        self._time_since_summoning += time_passed
        self._time_since_healing += time_passed
        if self._time_since_summoning > self._summoning_cooldown:
            necro_center_pos = npc.world_entity.get_center_position()
            self._time_since_summoning = 0
            relative_pos_from_summoner = (random.randint(-150, 150), random.randint(-150, 150))
            mummy_center_pos = sum_of_vectors(necro_center_pos, relative_pos_from_summoner)
            mummy_size = NON_PLAYER_CHARACTERS[NpcType.MUMMY].size
            mummy_pos = game_state.get_within_world(
                get_position_from_center_position(mummy_center_pos, mummy_size), mummy_size)
            mummy_enemy = create_npc(NpcType.MUMMY, mummy_pos)
            if not game_state.would_entity_collide_if_new_pos(mummy_enemy.world_entity, mummy_pos):
                self._summoning_cooldown = self._max_summoning_cooldown
                game_state.add_non_player_character(mummy_enemy)
                game_state.visual_effects.append(VisualCircle((80, 150, 100), necro_center_pos, 40, 70, Millis(120), 3))
                game_state.visual_effects.append(VisualCircle((80, 150, 100), mummy_center_pos, 40, 70, Millis(120), 3))
            else:
                # Failed to summon, so try again without waiting full duration
                self._summoning_cooldown = 1000

        if self._time_since_healing > self._healing_cooldown:
            self._time_since_healing = 0
            necro_center_pos = npc.world_entity.get_center_position()
            nearby_hurt_enemies = [
                e for e in game_state.non_player_characters
                if e.is_enemy
                   and is_x_and_y_within_distance(necro_center_pos, e.world_entity.get_center_position(), 200)
                   and e != npc and e.health < e.max_health
            ]
            if nearby_hurt_enemies:
                healing_target = nearby_hurt_enemies[0]
                healing_target.gain_health(5)
                healing_target_pos = healing_target.world_entity.get_center_position()
                visual_line = VisualLine((80, 200, 150), necro_center_pos, healing_target_pos, Millis(350), 3)
                game_state.visual_effects.append(visual_line)

        if self._time_since_decision > self._decision_interval:
            self._time_since_decision = 0
            if random.random() < 0.2:
                direction = random_direction()
                npc.world_entity.set_moving_in_dir(direction)
            else:
                npc.world_entity.set_not_moving()


def register_necromancer_enemy():
    size = (50, 60)
    health = 25
    register_npc_data(ENEMY_TYPE, NpcData(SPRITE, size, health, 0, 0.02, 15, True, False, None))
    register_npc_behavior(ENEMY_TYPE, NpcMind)

    enemy_sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_3.png")
    enemy_original_sprite_size = (32, 32)
    enemy_scaled_sprite_size = (50, 60)
    enemy_indices_by_dir = {
        Direction.DOWN: [(x, 0) for x in range(9, 12)],
        Direction.LEFT: [(x, 1) for x in range(9, 12)],
        Direction.RIGHT: [(x, 2) for x in range(9, 12)],
        Direction.UP: [(x, 3) for x in range(9, 12)]
    }
    register_entity_sprite_map(SPRITE, enemy_sprite_sheet, enemy_original_sprite_size,
                               enemy_scaled_sprite_size, enemy_indices_by_dir, (0, 0))
