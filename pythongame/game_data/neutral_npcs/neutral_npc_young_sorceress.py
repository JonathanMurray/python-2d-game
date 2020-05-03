from pythongame.core.common import NpcType, Sprite, Direction, Millis, PortraitIconSprite, \
    ItemType, PeriodicTimer, HeroId, ItemId
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map
from pythongame.core.game_state import GameState
from pythongame.core.item_data import plain_item_id
from pythongame.core.item_data import randomized_item_id
from pythongame.core.npc_behaviors import register_npc_behavior
from pythongame.core.npc_quest_behaviors import register_quest_giver_dialog, QuestGiverNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.quests import QuestId, Quest
from pythongame.core.view.image_loading import SpriteSheet

QUEST_MIN_LEVEL = 1
QUEST_ID = QuestId.RETRIEVE_FROG
QUEST_ITEM_TYPE = ItemType.QUEST_FROG


class NpcMind(QuestGiverNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, QUEST_ID, plain_item_id(QUEST_ITEM_TYPE), QUEST_MIN_LEVEL)
        self.timer = PeriodicTimer(Millis(500))
        self.quest_timer = PeriodicTimer(Millis(1000))


def _get_reward_for_hero(game_state: GameState) -> ItemId:
    hero_id = game_state.player_state.hero_id
    if hero_id == HeroId.MAGE:
        return randomized_item_id(ItemType.STAFF_OF_FIRE)
    elif hero_id == HeroId.ROGUE:
        return randomized_item_id(ItemType.THIEFS_MASK)
    elif hero_id == HeroId.WARRIOR:
        return randomized_item_id(ItemType.CLEAVER)
    else:
        return randomized_item_id(ItemType.LEATHER_ARMOR)


def register_young_sorceress_npc():
    npc_type = NpcType.NEUTRAL_YOUNG_SORCERESS
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.NEUTRAL_NPC_YOUNG_SORCERESS
    movement_speed = 0.03
    register_npc_data(npc_type, NpcData.neutral(sprite, size, movement_speed))
    register_npc_behavior(npc_type, NpcMind)
    sprite_sheet = SpriteSheet("resources/graphics/manga_spritesheet.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    x = 6
    indices_by_dir = {
        Direction.DOWN: [(x, 4), (x + 1, 4), (x + 2, 4)],
        Direction.LEFT: [(x, 5), (x + 1, 5), (x + 2, 5)],
        Direction.RIGHT: [(x, 6), (x + 1, 6), (x + 2, 6)],
        Direction.UP: [(x, 7), (x + 1, 7), (x + 2, 7)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-8, -16))

    register_quest_giver_dialog(
        npc_name="Mida",
        npc_type=NpcType.NEUTRAL_YOUNG_SORCERESS,
        icon_sprite=PortraitIconSprite.YOUNG_SORCERESS,
        icon_sprite_file_path='resources/graphics/portrait_young_sorceress_npc.png',
        quest=Quest(QUEST_ID, "Lost pet", "Retrieve Mida's pet frog from the goblin king."),
        quest_min_level=QUEST_MIN_LEVEL,
        quest_intro="Will you help me? I'll give you something in return. Promise!",
        boss_npc_type=NpcType.GOBLIN_WARRIOR,
        quest_item_type=ItemType.QUEST_FROG,
        custom_options=[],
        dialog_before_quest="",
        dialog_give_quest="Hey you! Have you seen my pet frog? I bet it was that old green mean goblin king that took "
                          "it!",
        dialog_during_quest="Hi friend! Any luck?",
        dialog_after_completed="Thank you for helping me!",
        reward_item_id=_get_reward_for_hero
    )
