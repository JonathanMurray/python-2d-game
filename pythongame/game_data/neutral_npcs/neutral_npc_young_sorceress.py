import random
from typing import Optional

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, PortraitIconSprite, \
    UiIconSprite, ItemType, PeriodicTimer, HeroId, SoundId, ItemId, plain_item_id
from pythongame.core.entity_creation import create_item_on_ground
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map, \
    register_portrait_icon_sprite_path, get_item_data, get_item_data_by_type, randomized_item_id
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity, QuestId, Quest, QuestGiverState
from pythongame.core.item_effects import try_add_item_to_inventory
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind, AbstractNpcAction, \
    DialogData, DialogOptionData, register_conditional_npc_dialog_data, register_quest
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.sound_player import play_sound
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.scenes_game.game_ui_view import GameUiView

QUEST_ID = QuestId.RETRIEVE_FROG
QUEST = Quest(QUEST_ID, "Lost pet", "Retrieve pet frog from goblin king")
ITEM_ID_FROG = plain_item_id(ItemType.FROG)
ITEM_TYPE = ItemType.FROG
NPC_TYPE = NpcType.NEUTRAL_YOUNG_SORCERESS
UI_ICON_SPRITE = PortraitIconSprite.YOUNG_SORCERESS


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
                if player_state.item_inventory.has_item_in_inventory(ITEM_ID_FROG):
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


class GiveQuest(AbstractNpcAction):

    def on_select(self, game_state: GameState) -> Optional[str]:
        game_state.player_state.start_quest(QUEST)
        play_sound(SoundId.EVENT_ACCEPTED_QUEST)
        return "Quest accepted: " + QUEST.name

    def on_hover(self, game_state: GameState, ui_view: GameUiView):
        _highlight_boss_location(game_state, ui_view)

    def on_blur(self, game_state: GameState, ui_view: GameUiView):
        _clear_highlight(ui_view)


class AcceptFrog(AbstractNpcAction):

    def on_select(self, game_state: GameState) -> Optional[str]:
        player_has_it = game_state.player_state.item_inventory.has_item_in_inventory(ITEM_ID_FROG)
        if player_has_it:
            game_state.player_state.item_inventory.lose_item_from_inventory(ITEM_ID_FROG)

            reward_item_id = _get_reward_for_hero(game_state.player_state.hero_id)
            reward_data = get_item_data(reward_item_id)
            did_add_item = try_add_item_to_inventory(game_state, reward_item_id)
            if not did_add_item:
                game_state.items_on_ground.append(
                    create_item_on_ground(reward_item_id, game_state.player_entity.get_position()))
            play_sound(SoundId.EVENT_COMPLETED_QUEST)
            game_state.player_state.complete_quest(QUEST)
            return "Reward gained: " + reward_data.name
        else:
            play_sound(SoundId.WARNING)
            return "You don't have that!"

    def on_hover(self, game_state: GameState, ui_view: GameUiView):
        _highlight_boss_location(game_state, ui_view)

    def on_blur(self, game_state: GameState, ui_view: GameUiView):
        _clear_highlight(ui_view)


def _get_reward_for_hero(hero_id: HeroId) -> ItemId:
    if hero_id == HeroId.MAGE:
        return randomized_item_id(ItemType.STAFF_OF_FIRE)
    elif hero_id == HeroId.ROGUE:
        return randomized_item_id(ItemType.THIEFS_MASK)
    elif hero_id == HeroId.WARRIOR:
        return randomized_item_id(ItemType.CLEAVER)
    else:
        return randomized_item_id(ItemType.LEATHER_ARMOR)


def _highlight_boss_location(game_state, ui_view):
    bosses = [npc for npc in game_state.non_player_characters if npc.npc_type == NpcType.GOBLIN_WARRIOR]
    if bosses:
        position = bosses[0].world_entity.get_center_position()
        world_area = game_state.entire_world_area
        position_ratio = ((position[0] - world_area.x) / world_area.w,
                          (position[1] - world_area.y) / world_area.h)
        ui_view.set_minimap_highlight(position_ratio)
    ui_view.set_inventory_highlight(ITEM_ID_FROG)


def _clear_highlight(ui_view):
    ui_view.remove_minimap_highlight()
    ui_view.remove_inventory_highlight()


def register_young_sorceress_npc():
    register_quest(QUEST_ID, QUEST)
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.NEUTRAL_NPC_YOUNG_SORCERESS
    movement_speed = 0.03
    register_npc_data(NPC_TYPE, NpcData.neutral(sprite, size, movement_speed))
    register_npc_behavior(NPC_TYPE, NpcMind)
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

    _register_dialog()


def _register_dialog():
    prompt = "QUEST: "
    frog_data = get_item_data_by_type(ITEM_TYPE)
    bye_option = DialogOptionData("\"Good bye\"", "cancel", None)
    name = "Mida"
    dialog_1 = DialogData(
        name,
        UI_ICON_SPRITE,
        "Hey you! Have you seen my pet frog? I bet it was that old green mean goblin king that took it!",
        [
            DialogOptionData(prompt + "\"Lost pet \"", "accept quest", GiveQuest(), UiIconSprite.ITEM_FROG,
                             frog_data.name,
                             "Will you help me? I'll give you something in return. Promise!"),
            bye_option
        ])
    dialog_2 = DialogData(
        name,
        UI_ICON_SPRITE,
        "Hi friend! Any luck?",
        [
            DialogOptionData(prompt + "\"Lost pet\"", "give", AcceptFrog(), UiIconSprite.ITEM_FROG, frog_data.name,
                             "..."),
            bye_option
        ])
    dialog_3 = DialogData(name, UI_ICON_SPRITE, "Thank you for helping me!", [bye_option])

    def get_dialog_data(game_state: GameState):
        if game_state.player_state.has_completed_quest(QUEST_ID):
            return dialog_3
        elif game_state.player_state.has_quest(QUEST_ID):
            return dialog_2
        else:
            return dialog_1

    register_conditional_npc_dialog_data(NPC_TYPE, get_dialog_data)
    register_portrait_icon_sprite_path(UI_ICON_SPRITE, 'resources/graphics/portrait_young_sorceress_npc.png')
