from pythongame.core.common import NpcType, Sprite, Direction, PortraitIconSprite, \
    ItemType
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map
from pythongame.core.item_data import plain_item_id, random_item_two_affixes
from pythongame.core.npc_behaviors import register_npc_behavior
from pythongame.core.npc_behaviors import sell_item_option
from pythongame.core.npc_quest_behaviors import QuestGiverNpcMind, \
    register_quest_giver_dialog
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.quests import QuestId, Quest
from pythongame.core.view.image_loading import SpriteSheet

QUEST_MIN_LEVEL = 2
UI_ICON_SPRITE = PortraitIconSprite.VIKING
QUEST_ID = QuestId.RETRIEVE_CORRUPTED_ORB
QUEST_ITEM_TYPE = ItemType.QUEST_CORRUPTED_ORB


class NpcMind(QuestGiverNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, QUEST_ID, plain_item_id(QUEST_ITEM_TYPE), QUEST_MIN_LEVEL)


def register_dwarf_npc():
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.NEUTRAL_NPC_DWARF
    npc_type = NpcType.NEUTRAL_DWARF
    movement_speed = 0.03
    register_npc_data(npc_type, NpcData.neutral(sprite, size, movement_speed))
    register_npc_behavior(npc_type, NpcMind)
    sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    indices_by_dir = {
        Direction.DOWN: [(0, 4), (1, 4), (2, 4)],
        Direction.LEFT: [(0, 5), (1, 5), (2, 5)],
        Direction.RIGHT: [(0, 6), (1, 6), (2, 6)],
        Direction.UP: [(0, 7), (1, 7), (2, 7)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-8, -16))

    register_quest_giver_dialog(
        npc_name="Gimli",
        npc_type=npc_type,
        icon_sprite=UI_ICON_SPRITE,
        icon_sprite_file_path='resources/graphics/viking_portrait.png',
        quest=Quest(QUEST_ID, "Corrupted orb", "Defeat the skeleton king and retrieve the magic orb."),
        quest_min_level=QUEST_MIN_LEVEL,
        quest_intro="I've heard tales of a powerful skeleton mage that possesses a very rare magic orb. I think it's "
                    "time that it finds itself a new owner!",
        boss_npc_type=NpcType.SKELETON_BOSS,
        quest_item_type=QUEST_ITEM_TYPE,
        custom_options=[
            sell_item_option(plain_item_id(ItemType.GOLD_NUGGET), 20,
                             "I'll give you good money for a nugget of pure gold!"),
            sell_item_option(plain_item_id(ItemType.SAPPHIRE), 30, "If you find a sapphire I can make you real rich!")
        ],
        dialog_before_quest="Hello there. I'm always looking for treasure. If you find any, we might be able to strike a "
                            "deal!",
        dialog_give_quest="Hello there. I'm always looking for treasure. If you find any, we might be able to strike a "
                          "deal!",
        dialog_during_quest="Hey! Any luck with the orb?",
        dialog_after_completed="Hi old friend! Got any more good stuff?",
        reward_item_id=lambda _: random_item_two_affixes(5)
    )
