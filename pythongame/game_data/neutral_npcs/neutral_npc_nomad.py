import random
from typing import Optional

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, PortraitIconSprite, \
    PeriodicTimer, get_random_hint, ItemType, UiIconSprite, SoundId
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map, \
    register_portrait_icon_sprite_path
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity, QuestId, Quest, QuestGiverState
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind, AbstractNpcAction, \
    DialogData, DialogOptionData, register_conditional_npc_dialog_data, register_quest
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.sound_player import play_sound
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.core.visual_effects import create_visual_healing_text
from pythongame.scenes_game.game_ui_view import GameUiView

QUEST_ID = QuestId.MAIN_RETRIEVE_KEY
QUEST = Quest(QUEST_ID, "The red baron", "Defeat the red baron and retrieve the key")

ITEM_TYPE_KEY = ItemType.KEY
NPC_TYPE = NpcType.NEUTRAL_NOMAD
PORTRAIT_ICON_SPRITE = PortraitIconSprite.NOMAD


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
                if player_state.item_inventory.has_item_in_inventory(ITEM_TYPE_KEY):
                    npc.quest_giver_state = QuestGiverState.CAN_COMPLETE_QUEST
                else:
                    npc.quest_giver_state = QuestGiverState.WAITING_FOR_PLAYER
            elif player_state.has_completed_quest(QUEST_ID):
                npc.quest_giver_state = None
            elif _is_player_eligible_for_quest(game_state):
                npc.quest_giver_state = QuestGiverState.CAN_GIVE_NEW_QUEST
            else:
                npc.quest_giver_state = None

        if self.timer.update_and_check_if_ready(time_passed):
            if random.random() < 0.8:
                npc.world_entity.set_not_moving()
            else:
                direction = random.choice(get_all_directions())
                npc.world_entity.set_moving_in_dir(direction)


def _is_player_eligible_for_quest(game_state: GameState):
    eligible = game_state.player_state.level >= 3
    return eligible


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


class AcceptQuest(AbstractNpcAction):

    def on_select(self, game_state: GameState):
        game_state.player_state.start_quest(QUEST)
        play_sound(SoundId.EVENT_ACCEPTED_QUEST)
        return "Quest accepted: " + QUEST.name

    def on_hover(self, game_state: GameState, ui_view: GameUiView):
        highlight_boss_position(game_state, ui_view)

    def on_blur(self, game_state: GameState, ui_view: GameUiView):
        clear_highlight(ui_view)


class CompleteQuest(AbstractNpcAction):

    def on_select(self, game_state: GameState):
        if game_state.player_state.item_inventory.has_item_in_inventory(ITEM_TYPE_KEY):
            play_sound(SoundId.EVENT_COMPLETED_QUEST)
            game_state.player_state.complete_quest(QUEST)
        else:
            play_sound(SoundId.WARNING)
            return "You don't have that!"

    def on_hover(self, game_state: GameState, ui_view: GameUiView):
        highlight_boss_position(game_state, ui_view)

    def on_blur(self, game_state: GameState, ui_view: GameUiView):
        clear_highlight(ui_view)


def highlight_boss_position(game_state, ui_view):
    bosses = [npc for npc in game_state.non_player_characters if npc.npc_type == NpcType.WARRIOR_KING]
    if bosses:
        position = bosses[0].world_entity.get_center_position()
        world_area = game_state.entire_world_area
        position_ratio = ((position[0] - world_area.x) / world_area.w,
                          (position[1] - world_area.y) / world_area.h)
        ui_view.set_minimap_highlight(position_ratio)
    ui_view.set_inventory_highlight(ITEM_TYPE_KEY)


def clear_highlight(ui_view):
    ui_view.remove_minimap_highlight()
    ui_view.remove_inventory_highlight()


def register_nomad_npc():
    register_quest(QUEST_ID, QUEST)
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.NEUTRAL_NPC_NOMAD
    movement_speed = 0.03
    register_npc_data(NPC_TYPE, NpcData.neutral(sprite, size, movement_speed))
    register_npc_behavior(NPC_TYPE, NpcMind)
    _register_dialog()
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
    register_portrait_icon_sprite_path(PORTRAIT_ICON_SPRITE, 'resources/graphics/nomad_portrait.png')


def _register_dialog():
    option_blessing = DialogOptionData("Receive blessing", "gain full health", HealAction())
    option_advice = DialogOptionData("Ask for advice", "see random hint", HintAction())
    option_accept_quest = DialogOptionData(
        "QUEST: \"The red baron\"",
        "accept quest",
        AcceptQuest(),
        UiIconSprite.ITEM_KEY,
        "Key",
        "The red baron... Yes, he has caused us much trouble. He stole from me a key that may"
        " lead us out of here. You must bring it back to me!")
    option_complete_quest = DialogOptionData(
        "QUEST: \"The red baron\"",
        "give",
        CompleteQuest(),
        UiIconSprite.ITEM_KEY,
        "Key",
        "...")
    option_bye = DialogOptionData("\"Good bye\"", "cancel", None)
    name = "Nomad"
    dialog_text = "Greetings. I am here only to serve. Seek me out when you are wounded or need guidance!"
    dialog_before_quest = DialogData(name, PORTRAIT_ICON_SPRITE, dialog_text,
                                     [option_blessing, option_advice, option_bye])
    dialog_can_give_quest = DialogData(name, PORTRAIT_ICON_SPRITE, dialog_text,
                                       [option_blessing, option_advice, option_accept_quest, option_bye])
    dialog_during_quest = DialogData(name, PORTRAIT_ICON_SPRITE, dialog_text,
                                     [option_blessing, option_advice, option_complete_quest, option_bye])
    dialog_after_quest = DialogData(name, PORTRAIT_ICON_SPRITE, "Oh you're back...",
                                    [option_blessing, option_advice, option_bye])

    def get_dialog_data(game_state: GameState) -> DialogData:
        if game_state.player_state.has_completed_quest(QUEST_ID):
            return dialog_after_quest
        elif game_state.player_state.has_quest(QUEST_ID):
            return dialog_during_quest
        elif _is_player_eligible_for_quest(game_state):
            return dialog_can_give_quest
        else:
            return dialog_before_quest

    register_conditional_npc_dialog_data(NPC_TYPE, get_dialog_data)
