from pythongame.core.common import *
from pythongame.core.common import NpcType, Millis, get_all_directions, ItemType, PeriodicTimer
from pythongame.core.entity_creation import create_item_on_ground
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity, Quest, QuestGiverState, QuestId
from pythongame.core.item_data import build_item_name
from pythongame.core.item_data import get_item_data_by_type
from pythongame.core.item_data import plain_item_id
from pythongame.core.item_effects import try_add_item_to_inventory
from pythongame.core.npc_behaviors import AbstractNpcAction
from pythongame.core.npc_behaviors import AbstractNpcMind, DialogOptionData
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.sound_player import play_sound
from pythongame.scenes_game.game_ui_view import GameUiView


class GiveQuestNpcAction(AbstractNpcAction):

    def __init__(self, quest: Quest, boss_npc_type: NpcType, quest_item_type: ItemType):
        super().__init__()
        self.quest = quest
        self.boss_npc_type = boss_npc_type
        self.quest_item_type = quest_item_type

    def on_select(self, game_state: GameState) -> Optional[str]:
        game_state.player_state.start_quest(self.quest)
        play_sound(SoundId.EVENT_ACCEPTED_QUEST)
        return "Quest accepted: " + self.quest.name

    def on_hover(self, game_state: GameState, ui_view: GameUiView):
        _quest_on_hover(game_state, ui_view, self.boss_npc_type, plain_item_id(self.quest_item_type))

    def on_blur(self, game_state: GameState, ui_view: GameUiView):
        _quest_on_blur(ui_view)


class CompleteQuestNpcAction(AbstractNpcAction):

    def __init__(self, quest: Quest, boss_npc_type: NpcType, quest_item_type: ItemType,
                 reward_item_id: ItemId):
        super().__init__()
        self.quest = quest
        self.boss_npc_type = boss_npc_type
        self.quest_item_type = quest_item_type
        self.reward_item_id = reward_item_id

    def on_select(self, game_state: GameState) -> Optional[str]:
        player_has_it = game_state.player_state.item_inventory.has_item_in_inventory(
            plain_item_id(self.quest_item_type))
        if player_has_it:
            game_state.player_state.item_inventory.lose_item_from_inventory(plain_item_id(self.quest_item_type))
            did_add_item = try_add_item_to_inventory(game_state, self.reward_item_id)
            if not did_add_item:
                game_state.items_on_ground.append(
                    create_item_on_ground(self.reward_item_id, game_state.player_entity.get_position()))
            play_sound(SoundId.EVENT_COMPLETED_QUEST)
            game_state.player_state.complete_quest(self.quest)
            return "Reward gained: " + build_item_name(self.reward_item_id)
        else:
            play_sound(SoundId.WARNING)
            return "You don't have that!"

    def on_hover(self, game_state: GameState, ui_view: GameUiView):
        _quest_on_hover(game_state, ui_view, self.boss_npc_type, plain_item_id(self.quest_item_type))

    def on_blur(self, game_state: GameState, ui_view: GameUiView):
        _quest_on_blur(ui_view)


def _quest_on_hover(game_state: GameState, ui_view: GameUiView, boss_npc_type: NpcType, quest_item_id: ItemId):
    bosses = [npc for npc in game_state.non_player_characters if npc.npc_type == boss_npc_type]
    if bosses:
        position = bosses[0].world_entity.get_center_position()
        world_area = game_state.entire_world_area
        position_ratio = ((position[0] - world_area.x) / world_area.w,
                          (position[1] - world_area.y) / world_area.h)
        ui_view.set_minimap_highlight(position_ratio)
    ui_view.set_inventory_highlight(quest_item_id)


def _quest_on_blur(ui_view: GameUiView):
    ui_view.remove_minimap_highlight()
    ui_view.remove_inventory_highlight()


def give_quest_option(quest: Quest, quest_intro: str, boss_npc_type: NpcType,
                      quest_item_type: ItemType) -> DialogOptionData:
    return DialogOptionData(
        summary="QUEST: \"%s\"" % quest.name,
        action_text="accept quest",
        action=GiveQuestNpcAction(quest, boss_npc_type, quest_item_type),
        ui_icon_sprite=get_item_data_by_type(quest_item_type).icon_sprite,
        detail_header=quest.name,
        detail_body=quest_intro)


def complete_quest_option(quest: Quest, boss_npc_type: NpcType, quest_item_type: ItemType,
                          reward_item_id: ItemId) -> DialogOptionData:
    return DialogOptionData(
        summary="QUEST: \"%s\"" % quest.name,
        action_text="give",
        action=CompleteQuestNpcAction(quest, boss_npc_type, quest_item_type, reward_item_id),
        ui_icon_sprite=UiIconSprite.ITEM_CORRUPTED_ORB,
        detail_header=get_item_data_by_type(quest_item_type).base_name,
        detail_body="...")


class QuestGiverNpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder, quest_id: QuestId, quest_item_id: ItemId):
        super().__init__(global_path_finder)
        self.timer = PeriodicTimer(Millis(500))
        self.quest_timer = PeriodicTimer(Millis(1000))
        self.quest_id = quest_id
        self.quest_item_id = quest_item_id

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):

        if self.quest_timer.update_and_check_if_ready(time_passed):
            player_state = game_state.player_state
            if player_state.has_quest(self.quest_id):
                if player_state.item_inventory.has_item_in_inventory(self.quest_item_id):
                    npc.quest_giver_state = QuestGiverState.CAN_COMPLETE_QUEST
                else:
                    npc.quest_giver_state = QuestGiverState.WAITING_FOR_PLAYER
            elif player_state.has_completed_quest(self.quest_id):
                npc.quest_giver_state = None
            else:
                npc.quest_giver_state = QuestGiverState.CAN_GIVE_NEW_QUEST

        if self.timer.update_and_check_if_ready(time_passed):
            if random.random() < 0.8:
                npc.world_entity.set_not_moving()
            else:
                direction = random.choice(get_all_directions())
                npc.world_entity.set_moving_in_dir(direction)
