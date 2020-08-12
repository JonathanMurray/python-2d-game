import random
from typing import Optional, Tuple, Callable

from pythongame.core.common import NpcType
from pythongame.core.entity_creation import create_hero_world_entity, create_npc
from pythongame.core.game_state import GameState, NonPlayerCharacter, PlayerState, GameWorldState
from pythongame.dungeon_generator import GeneratedDungeon, DungeonGenerator


def create_dungeon_game_state(player_state: PlayerState, camera_size: Tuple[int, int],
                              difficulty_level: int) -> GameState:
    dungeon = _generate_dungeon(difficulty_level)
    player_entity = create_hero_world_entity(player_state.hero_id, dungeon.player_position)
    game_world = GameWorldState(
        player_entity=player_entity,
        non_player_characters=dungeon.npcs,
        consumables_on_ground=[],
        items_on_ground=[],
        money_piles_on_ground=[],
        walls=dungeon.walls,
        entire_world_area=dungeon.world_area,
        decoration_entities=dungeon.decorations,
        portals=[],
        chests=[],
        shrines=[],
        dungeon_entrances=[],
    )
    return GameState(
        game_world=game_world,
        camera_size=camera_size,
        player_state=player_state,
        is_dungeon=True,
        player_spawn_position=dungeon.player_position
    )


def _generate_dungeon(difficulty_level: int) -> GeneratedDungeon:
    # Prefer maps that are longer on the horizontal axis, due to the aspect ratio of the in-game camera
    w = random.randint(70, 100)
    world_size = (w, 140 - w)
    dungeon_generator = DungeonGenerator(
        world_size=world_size,
        max_num_rooms=5,
        room_allowed_width=(8, 25),
        room_allowed_height=(8, 25),
        corridor_allowed_width=(3, 5),
        generate_npc=_generate_npc_function(difficulty_level))
    grid, rooms = dungeon_generator.generate_random_grid()
    return dungeon_generator.generate_random_dungeon_from_grid(grid, rooms)


def _generate_npc_function(difficulty_level: int) -> Callable[[int, int], Optional[NonPlayerCharacter]]:
    if difficulty_level == 1:
        return _generate_npc_1
    elif difficulty_level == 2:
        return _generate_npc_2
    elif difficulty_level == 3:
        return _generate_npc_3
    elif difficulty_level == 4:
        return _generate_npc_4
    else:
        print("WARN: Unhandled dungeon difficulty level (%s)! Falling back to some other difficulty" % difficulty_level)
        return _generate_npc_4


def _generate_npc_1(x: int, y: int) -> Optional[NonPlayerCharacter]:
    valid_enemy_types = [NpcType.GOBLIN_SPEARMAN_ELITE, NpcType.SKELETON_MAGE, NpcType.ZOMBIE_FAST, NpcType.NECROMANCER]
    if random.random() < 0.3:
        npc_type = random.choice(valid_enemy_types)
        return create_npc(npc_type, (x, y))


def _generate_npc_2(x: int, y: int) -> Optional[NonPlayerCharacter]:
    valid_enemy_types = [NpcType.WARRIOR, NpcType.VETERAN, NpcType.ICE_WITCH]
    if random.random() < 0.5:
        npc_type = random.choice(valid_enemy_types)
        return create_npc(npc_type, (x, y))


def _generate_npc_3(x: int, y: int) -> Optional[NonPlayerCharacter]:
    valid_enemy_types = [NpcType.HUMAN_SUMMONER, NpcType.ICE_WITCH, NpcType.VETERAN]
    if random.random() < 0.5:
        npc_type = random.choice(valid_enemy_types)
        return create_npc(npc_type, (x, y))


def _generate_npc_4(x: int, y: int) -> Optional[NonPlayerCharacter]:
    valid_enemy_types = [NpcType.SKELETON_BOSS, NpcType.GOBLIN_WARRIOR, NpcType.WARRIOR_KING]
    if random.random() < 0.3:
        npc_type = random.choice(valid_enemy_types)
        return create_npc(npc_type, (x, y))
