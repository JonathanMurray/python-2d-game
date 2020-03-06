import random

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, PortraitIconSprite, \
    ItemType, PeriodicTimer
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map, \
    register_portrait_icon_sprite_path
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity, QuestId, Quest, QuestGiverState
from pythongame.core.item_data import plain_item_id, randomized_item_id
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind, DialogData, DialogOptionData, \
    register_conditional_npc_dialog_data
from pythongame.core.npc_behaviors import sell_item_option
from pythongame.core.npc_quest_behaviors import complete_quest_option, give_quest_option
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.view.image_loading import SpriteSheet

UI_ICON_SPRITE = PortraitIconSprite.VIKING
QUEST_ID = QuestId.RETRIEVE_CORRUPTED_ORB
QUEST = Quest(QUEST_ID, "Corrupted orb", "Defeat the skeleton king and retrieve the magic orb.")
ITEM_TYPE_CORRUPTED_ORB = ItemType.QUEST_CORRUPTED_ORB
NPC_TYPE = NpcType.NEUTRAL_DWARF


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self.timer = PeriodicTimer(Millis(500))
        self.quest_timer = PeriodicTimer(Millis(1000))

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):

        if self.quest_timer.update_and_check_if_ready(time_passed):
            player_state = game_state.player_state
            if player_state.has_quest(QUEST_ID):
                if player_state.item_inventory.has_item_in_inventory(plain_item_id(ITEM_TYPE_CORRUPTED_ORB)):
                    npc.quest_giver_state = QuestGiverState.CAN_COMPLETE_QUEST
                else:
                    npc.quest_giver_state = QuestGiverState.WAITING_FOR_PLAYER
            elif player_state.has_completed_quest(QUEST_ID):
                npc.quest_giver_state = None
            else:
                npc.quest_giver_state = QuestGiverState.CAN_GIVE_NEW_QUEST

        if self.timer.update_and_check_if_ready(time_passed):
            if random.random() < 0.8:
                npc.world_entity.set_not_moving()
            else:
                direction = random.choice(get_all_directions())
                npc.world_entity.set_moving_in_dir(direction)


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

    _register_dialog()


def _register_dialog():
    bye_option = DialogOptionData("\"Good bye\"", "cancel", None)
    name = "Gimli"
    sell_option_1 = sell_item_option(plain_item_id(ItemType.GOLD_NUGGET), 20,
                                     "I'll give you good money for a nugget of pure gold!")
    sell_option_2 = sell_item_option(plain_item_id(ItemType.SAPPHIRE), 30,
                                     "If you find a sapphire I can make you real rich!")
    boss_npc_type = NpcType.SKELETON_BOSS
    give_quest = give_quest_option(
        QUEST,
        "I've heard tales of a powerful skeleton mage that possesses a very rare magic orb. I think it's time that it "
        "finds itself a new owner!",
        boss_npc_type,
        ITEM_TYPE_CORRUPTED_ORB)
    dialog_1 = DialogData(
        name,
        UI_ICON_SPRITE,
        "Hello there. I'm always looking for treasure. If you find any, we might be able to strike a deal!",
        [sell_option_1, sell_option_2, give_quest, bye_option])
    complete_quest = complete_quest_option(QUEST, boss_npc_type, ITEM_TYPE_CORRUPTED_ORB,
                                           randomized_item_id(ItemType.ROYAL_SWORD))
    dialog_2 = DialogData(
        name,
        UI_ICON_SPRITE,
        "Hey! Any luck with the orb?",
        [sell_option_1, sell_option_2, complete_quest, bye_option])
    dialog_3 = DialogData(
        name,
        UI_ICON_SPRITE,
        "Hi old friend! Got any more good stuff?",
        [
            sell_option_1,
            sell_option_2,
            bye_option
        ])

    def get_dialog_data(game_state: GameState) -> DialogData:
        if game_state.player_state.has_completed_quest(QUEST_ID):
            return dialog_3
        elif game_state.player_state.has_quest(QUEST_ID):
            return dialog_2
        else:
            return dialog_1

    register_conditional_npc_dialog_data(NPC_TYPE, get_dialog_data)
    register_portrait_icon_sprite_path(UI_ICON_SPRITE, 'resources/graphics/viking_portrait.png')
