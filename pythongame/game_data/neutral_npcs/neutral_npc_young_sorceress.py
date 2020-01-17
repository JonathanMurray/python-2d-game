import random
from typing import Optional

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, PortraitIconSprite, \
    UiIconSprite, ItemType, PeriodicTimer, HeroId, SoundId
from pythongame.core.entity_creation import create_item_on_ground
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map, \
    register_portrait_icon_sprite_path, ITEMS
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
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

has_finished_quest = False  # TODO store this in "quests" in gamestate instead


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


def get_reward_for_hero(hero_id: HeroId):
    if hero_id == HeroId.MAGE:
        return ItemType.STAFF_OF_FIRE
    elif hero_id == HeroId.ROGUE:
        return ItemType.THIEFS_MASK
    elif hero_id == HeroId.WARRIOR:
        return ItemType.CLEAVER
    else:
        return ItemType.LEATHER_ARMOR


class AcceptFrog(AbstractNpcAction):

    def on_select(self, game_state: GameState) -> Optional[str]:
        global has_finished_quest
        player_has_it = game_state.player_state.item_inventory.has_item_in_inventory(ITEM_TYPE_FROG)
        if player_has_it:
            game_state.player_state.item_inventory.lose_item_from_inventory(ITEM_TYPE_FROG)

            reward_item_type = get_reward_for_hero(game_state.player_state.hero_id)
            reward_effect = get_item_effect(reward_item_type)
            reward_data = ITEMS[reward_item_type]
            reward_equipment_category = reward_data.item_equipment_category
            did_add_item = try_add_item_to_inventory(game_state, reward_effect, reward_equipment_category)
            if not did_add_item:
                game_state.items_on_ground.append(
                    create_item_on_ground(reward_item_type, game_state.player_entity.get_position()))
            play_sound(SoundId.EVENT_COMPLETED_QUEST)
            has_finished_quest = True
            return "Reward gained: " + reward_data.name
        else:
            play_sound(SoundId.WARNING)
            return "You don't have that!"

    def on_hover(self, game_state: GameState, ui_view: GameUiView):
        bosses = [npc for npc in game_state.non_player_characters if npc.npc_type == NpcType.GOBLIN_WARRIOR]
        if bosses:
            position = bosses[0].world_entity.get_center_position()
            world_area = game_state.entire_world_area
            position_ratio = ((position[0] - world_area.x) / world_area.w,
                              (position[1] - world_area.y) / world_area.h)
            ui_view.set_minimap_highlight(position_ratio)
        ui_view.set_inventory_highlight(ITEM_TYPE_FROG)

    def on_blur(self, game_state: GameState, ui_view: GameUiView):
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
    introduction = "Hey you! Have you seen my pet frog? I bet it was that old green mean goblin king that took it!"
    prompt = "QUEST: "
    frog_data = ITEMS[ItemType.FROG]
    bye_option = DialogOptionData("\"Good bye\"", "cancel", None)
    dialog_options = [
        DialogOptionData(prompt + "\"Lost pet\"", "give", AcceptFrog(), UiIconSprite.ITEM_FROG, frog_data.name,
                         "Please help me get my frog back! I'll give you something in return. Promise!"),
        bye_option]
    default_dialog = DialogData(UI_ICON_SPRITE, introduction, dialog_options)
    finished_quest_dialog = DialogData(UI_ICON_SPRITE, "Thank you for helping me!", [bye_option])

    def get_dialog_data(_game_state: GameState):
        if has_finished_quest:
            return finished_quest_dialog
        else:
            return default_dialog

    register_conditional_npc_dialog_data(NPC_TYPE, get_dialog_data)
    register_portrait_icon_sprite_path(UI_ICON_SPRITE, 'resources/graphics/portrait_young_sorceress_npc.png')
