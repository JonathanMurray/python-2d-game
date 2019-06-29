from pythongame.core.common import Millis, NpcType, Sprite, Direction, ItemType, ConsumableType
from pythongame.core.game_data import register_npc_data, NpcData, SpriteSheet, register_entity_sprite_map
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.loot import LootEntry, LootTable, LootGroup
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):
        pass


def register_chest_enemy():
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.ENEMY_CHEST
    npc_type = NpcType.CHEST
    health = 1
    possible_drops = [
        LootEntry.item(ItemType.WINGED_BOOTS),
        LootEntry.item(ItemType.AMULET_OF_MANA_1),
        LootEntry.item(ItemType.AMULET_OF_MANA_2),
        LootEntry.item(ItemType.AMULET_OF_MANA_3),
        LootEntry.item(ItemType.STAFF_OF_FIRE),
        LootEntry.item(ItemType.BLESSED_SHIELD_1),
        LootEntry.item(ItemType.BLESSED_SHIELD_2),
        LootEntry.item(ItemType.BLESSED_SHIELD_3),
        LootEntry.item(ItemType.SOLDIERS_HELMET_1),
        LootEntry.item(ItemType.SOLDIERS_HELMET_2),
        LootEntry.item(ItemType.SOLDIERS_HELMET_3),
        LootEntry.item(ItemType.BLUE_ROBE_1),
        LootEntry.item(ItemType.BLUE_ROBE_2),
        LootEntry.item(ItemType.BLUE_ROBE_3),
        LootEntry.consumable(ConsumableType.SCROLL_ABILITY_SUMMON)
    ]
    loot = LootTable([LootGroup(1, possible_drops, 1)])
    register_npc_data(npc_type, NpcData(sprite, size, health, 0, 0, 0, True, False, None, None, loot))
    register_npc_behavior(npc_type, NpcMind)

    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 64)
    scaled_sprite_size = (50, 75)
    indices_by_dir = {Direction.DOWN: [(9, 3)]}
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (-6, -33))