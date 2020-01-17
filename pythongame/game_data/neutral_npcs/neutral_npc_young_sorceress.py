import random
from typing import Optional

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, PortraitIconSprite, \
    UiIconSprite, ItemType, PeriodicTimer, HeroId, SoundId
from pythongame.core.entity_creation import create_item_on_ground
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map, \
    register_portrait_icon_sprite_path, ITEMS
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity, QuestId, Quest
from pythongame.core.item_effects import get_item_effect, try_add_item_to_inventory
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind, AbstractNpcAction, \
    DialogData, DialogOptionData, register_conditional_npc_dialog_data
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.sound_player import play_sound
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.scenes_game.game_ui_view import GameUiView

ITEM_TYPE_FROG = ItemType.FROG
NPC_TYPE = NpcType.NEUTRAL_YOUNG_SORCERESS
UI_ICON_SPRITE = PortraitIconSprite.YOUNG_SORCERESS


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self.timer = PeriodicTimer(Millis(500))

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            if random.random() < 0.8:
                npc.world_entity.set_not_moving()
            else:
                direction = random.choice(get_all_directions())
                npc.world_entity.set_moving_in_dir(direction)


class GiveQuest(AbstractNpcAction):

    def on_select(self, game_state: GameState) -> Optional[str]:
        quest = Quest(QuestId.RETRIEVE_FROG, "Lost pet", "Retrieve pet frog from goblin king")
        game_state.player_state.start_quest(quest)
        return "Quest accepted: " + quest.name

    def on_hover(self, game_state: GameState, ui_view: GameUiView):
        _highlight_boss_location(game_state, ui_view)

    def on_blur(self, game_state: GameState, ui_view: GameUiView):
        _clear_highlight(ui_view)


class AcceptFrog(AbstractNpcAction):

    def on_select(self, game_state: GameState) -> Optional[str]:
        player_has_it = game_state.player_state.item_inventory.has_item_in_inventory(ITEM_TYPE_FROG)
        if player_has_it:
            game_state.player_state.item_inventory.lose_item_from_inventory(ITEM_TYPE_FROG)

            reward_item_type = _get_reward_for_hero(game_state.player_state.hero_id)
            reward_effect = get_item_effect(reward_item_type)
            reward_data = ITEMS[reward_item_type]
            reward_equipment_category = reward_data.item_equipment_category
            did_add_item = try_add_item_to_inventory(game_state, reward_effect, reward_equipment_category)
            if not did_add_item:
                game_state.items_on_ground.append(
                    create_item_on_ground(reward_item_type, game_state.player_entity.get_position()))
            play_sound(SoundId.EVENT_COMPLETED_QUEST)
            game_state.player_state.complete_quest(QuestId.RETRIEVE_FROG)
            return "Reward gained: " + reward_data.name
        else:
            play_sound(SoundId.WARNING)
            return "You don't have that!"

    def on_hover(self, game_state: GameState, ui_view: GameUiView):
        _highlight_boss_location(game_state, ui_view)

    def on_blur(self, game_state: GameState, ui_view: GameUiView):
        _clear_highlight(ui_view)


def _get_reward_for_hero(hero_id: HeroId):
    if hero_id == HeroId.MAGE:
        return ItemType.STAFF_OF_FIRE
    elif hero_id == HeroId.ROGUE:
        return ItemType.THIEFS_MASK
    elif hero_id == HeroId.WARRIOR:
        return ItemType.CLEAVER
    else:
        return ItemType.LEATHER_ARMOR


def _highlight_boss_location(game_state, ui_view):
    bosses = [npc for npc in game_state.non_player_characters if npc.npc_type == NpcType.GOBLIN_WARRIOR]
    if bosses:
        position = bosses[0].world_entity.get_center_position()
        world_area = game_state.entire_world_area
        position_ratio = ((position[0] - world_area.x) / world_area.w,
                          (position[1] - world_area.y) / world_area.h)
        ui_view.set_minimap_highlight(position_ratio)
    ui_view.set_inventory_highlight(ITEM_TYPE_FROG)


def _clear_highlight(ui_view):
    ui_view.remove_minimap_highlight()
    ui_view.remove_inventory_highlight()


def register_young_sorceress_npc():
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
    frog_data = ITEMS[ItemType.FROG]
    bye_option = DialogOptionData("\"Good bye\"", "cancel", None)
    dialog_1 = DialogData(
        UI_ICON_SPRITE,
        "Hey you! Have you seen my pet frog? I bet it was that old green mean goblin king that took it!",
        [
            DialogOptionData(prompt + "\"Lost pet \"", "accept quest", GiveQuest(), UiIconSprite.ITEM_FROG,
                             frog_data.name,
                             "Will you help me? I'll give you something in return. Promise!"),
            bye_option
        ])
    dialog_2 = DialogData(
        UI_ICON_SPRITE,
        "Hi friend! Any luck?",
        [
            DialogOptionData(prompt + "\"Lost pet\"", "give", AcceptFrog(), UiIconSprite.ITEM_FROG, frog_data.name,
                             "..."),
            bye_option
        ])
    dialog_3 = DialogData(UI_ICON_SPRITE, "Thank you for helping me!", [bye_option])

    def get_dialog_data(game_state: GameState):
        if game_state.player_state.has_completed_quest(QuestId.RETRIEVE_FROG):
            return dialog_3
        elif game_state.player_state.has_quest(QuestId.RETRIEVE_FROG):
            return dialog_2
        else:
            return dialog_1

    register_conditional_npc_dialog_data(NPC_TYPE, get_dialog_data)
    register_portrait_icon_sprite_path(UI_ICON_SPRITE, 'resources/graphics/portrait_young_sorceress_npc.png')
