import random
from typing import Optional

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, PortraitIconSprite, \
    PeriodicTimer, get_random_hint, ItemType, UiIconSprite, SoundId
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map, \
    register_portrait_icon_sprite_path
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity, QuestId
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind, AbstractNpcAction, \
    register_npc_dialog_data, DialogData, DialogOptionData
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.sound_player import play_sound
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.core.visual_effects import create_visual_healing_text
from pythongame.scenes_game.game_ui_view import GameUiView

ITEM_TYPE_KEY = ItemType.KEY


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


class HealAction(AbstractNpcAction):

    def on_select(self, game_state: GameState) -> Optional[str]:
        if not game_state.player_state.health_resource.is_at_max():
            health_gained = game_state.player_state.health_resource.gain_to_max()
            game_state.visual_effects.append(create_visual_healing_text(game_state.player_entity, health_gained))
            play_sound(SoundId.CONSUMABLE_POTION)
            return "You feel healthy again!"
        play_sound(SoundId.WARNING)
        return "Already at full health!"


class HintAction(AbstractNpcAction):

    def on_select(self, game_state: GameState) -> Optional[str]:
        return get_random_hint()


class AcceptKey(AbstractNpcAction):

    def on_select(self, game_state: GameState):
        if game_state.player_state.item_inventory.has_item_in_inventory(ITEM_TYPE_KEY):
            play_sound(SoundId.EVENT_COMPLETED_QUEST)
            game_state.player_state.complete_quest(QuestId.MAIN_RETRIEVE_KEY)
        else:
            play_sound(SoundId.WARNING)
            return "You don't have that!"

    def on_hover(self, game_state: GameState, ui_view: GameUiView):
        bosses = [npc for npc in game_state.non_player_characters if npc.npc_type == NpcType.WARRIOR_KING]
        if bosses:
            position = bosses[0].world_entity.get_center_position()
            world_area = game_state.entire_world_area
            position_ratio = ((position[0] - world_area.x) / world_area.w,
                              (position[1] - world_area.y) / world_area.h)
            ui_view.set_minimap_highlight(position_ratio)
        ui_view.set_inventory_highlight(ITEM_TYPE_KEY)

    def on_blur(self, game_state: GameState, ui_view: GameUiView):
        ui_view.remove_minimap_highlight()
        ui_view.remove_inventory_highlight()


def register_nomad_npc():
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.NEUTRAL_NPC_NOMAD
    npc_type = NpcType.NEUTRAL_NOMAD
    movement_speed = 0.03
    register_npc_data(npc_type, NpcData.neutral(sprite, size, movement_speed))
    register_npc_behavior(npc_type, NpcMind)
    # TODO Handle states (no quest, accepted quest)
    text_body = "Greetings. I am here only to serve. Seek me out when you are wounded or need guidance!"
    dialog_options = [
        DialogOptionData("Receive blessing", "gain full health", HealAction()),
        DialogOptionData("Ask for advice", "see random hint", HintAction()),
        DialogOptionData("QUEST: \"The red baron\"", "give", AcceptKey(), UiIconSprite.ITEM_KEY,
                         "Key", "The red baron... Yes, he has caused us much trouble. He stole from me a key that may"
                                " lead us out of here. You must bring it back to me!"),
        DialogOptionData("\"Good bye\"", "cancel", None)]
    dialog_data = DialogData(PortraitIconSprite.NOMAD, text_body, dialog_options)
    register_npc_dialog_data(npc_type, dialog_data)
    sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_3.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    indices_by_dir = {
        Direction.DOWN: [(3, 0), (4, 0), (5, 0)],
        Direction.LEFT: [(3, 1), (4, 1), (5, 1)],
        Direction.RIGHT: [(3, 2), (4, 2), (5, 2)],
        Direction.UP: [(3, 3), (4, 3), (5, 3)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-8, -16))
    register_portrait_icon_sprite_path(PortraitIconSprite.NOMAD, 'resources/graphics/nomad_portrait.png')
