from pythongame.core.common import Millis, NpcType, Sprite, Direction, SoundId
from pythongame.core.entity_creation import create_npc
from pythongame.core.game_data import NpcData
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.npc_behaviors import AbstractNpcMind, EnemySummonTrait, EnemyRandomWalkTrait
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.world_entity import WorldEntity
from pythongame.game_data.enemies.register_enemies_util import register_basic_enemy
from pythongame.game_data.loot_tables import LootTableId


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._summon_trait = EnemySummonTrait(2, [NpcType.FIRE_DEMON], (Millis(500), Millis(4000)), create_npc)
        self._random_walk_trait = EnemyRandomWalkTrait(Millis(750))

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    _is_player_invisible: bool, time_passed: Millis):
        self._summon_trait.update(npc, game_state, time_passed)
        self._random_walk_trait.update(npc, game_state, time_passed)


def register_human_summoner_enemy():
    x = 0
    indices_by_dir = {
        Direction.DOWN: [(x, 0), (x + 1, 0), (x + 2, 0), (x + 1, 0)],
        Direction.LEFT: [(x, 1), (x + 1, 1), (x + 2, 1), (x + 1, 1)],
        Direction.RIGHT: [(x, 2), (x + 1, 2), (x + 2, 2), (x + 1, 2)],
        Direction.UP: [(x, 3), (x + 1, 3), (x + 2, 3), (x + 1, 3)]
    }

    register_basic_enemy(
        npc_type=NpcType.HUMAN_SUMMONER,
        npc_data=NpcData.enemy(
            sprite=Sprite.ENEMY_HUMAN_SUMMONER,
            size=(32, 32),
            max_health=60,
            health_regen=2,
            speed=0.08,
            exp_reward=52,
            enemy_loot_table=LootTableId.LEVEL_6,
            death_sound_id=SoundId.DEATH_ICE_WITCH),  # TODO
        mind_constructor=NpcMind,
        spritesheet_path="resources/graphics/manga_characters_spritesheet.png",
        original_sprite_size=(32, 32),
        scaled_sprite_size=(48, 48),
        spritesheet_indices=indices_by_dir,
        sprite_position_relative_to_entity=(-8, -16)
    )
