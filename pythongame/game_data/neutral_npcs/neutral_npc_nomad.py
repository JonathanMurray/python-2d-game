from typing import Optional

from pythongame.core.common import NpcType, Sprite, Direction, PortraitIconSprite, \
    get_random_hint, ItemType, SoundId
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map
from pythongame.core.item_data import plain_item_id
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcAction, \
    DialogOptionData
from pythongame.core.npc_quest_behaviors import register_quest_giver_dialog, QuestGiverNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.quests import QuestId, Quest
from pythongame.core.sound_player import play_sound
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.core.visual_effects import create_visual_healing_text
from pythongame.scenes.scenes_game.game_engine import GameEngine

QUEST_MIN_LEVEL = 3
QUEST_ID = QuestId.MAIN_RETRIEVE_KEY
QUEST = Quest(QUEST_ID, "The red baron", "Defeat the red baron and retrieve any item of interest that he's carrying.")
QUEST_ITEM_TYPE = ItemType.QUEST_KEY


class NpcMind(QuestGiverNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, QUEST_ID, plain_item_id(QUEST_ITEM_TYPE), QUEST_MIN_LEVEL)


class HealAction(AbstractNpcAction):
    def on_select(self, game_engine: GameEngine) -> Optional[str]:
        game_state = game_engine.game_state
        if not game_state.player_state.health_resource.is_at_max():
            health_gained = game_state.player_state.health_resource.gain_to_max()
            game_state.game_world.visual_effects.append(
                create_visual_healing_text(game_state.game_world.player_entity, health_gained))
            play_sound(SoundId.CONSUMABLE_POTION)
            return "You feel healthy again!"
        play_sound(SoundId.WARNING)
        return "Already at full health!"


class HintAction(AbstractNpcAction):
    def on_select(self, game_engine: GameEngine) -> Optional[str]:
        return get_random_hint()


def register_nomad_npc():
    sprite = Sprite.NEUTRAL_NPC_NOMAD
    npc_type = NpcType.NEUTRAL_NOMAD
    register_npc_data(npc_type, NpcData.neutral(sprite=sprite, size=(30, 30), speed=0.03))
    register_npc_behavior(npc_type, NpcMind)
    register_entity_sprite_map(
        sprite=sprite,
        sprite_sheet=SpriteSheet("resources/graphics/enemy_sprite_sheet_3.png"),
        original_sprite_size=(32, 32),
        scaled_sprite_size=(48, 48),
        indices_by_dir={
            Direction.DOWN: [(3, 0), (4, 0), (5, 0)],
            Direction.LEFT: [(3, 1), (4, 1), (5, 1)],
            Direction.RIGHT: [(3, 2), (4, 2), (5, 2)],
            Direction.UP: [(3, 3), (4, 3), (5, 3)]
        },
        position_relative_to_entity=(-8, -16)
    )

    register_quest_giver_dialog(
        npc_name="Nomad",
        npc_type=NpcType.NEUTRAL_NOMAD,
        icon_sprite=PortraitIconSprite.NOMAD,
        icon_sprite_file_path='resources/graphics/nomad_portrait.png',
        quest=QUEST,
        quest_min_level=QUEST_MIN_LEVEL,
        quest_intro="The red baron has caused us great trouble. Get rid of him and I'll be forever "
                    "grateful! Oh, and please bring back anything interesting that he's carrying.",
        boss_npc_type=NpcType.WARRIOR_KING,
        quest_item_type=QUEST_ITEM_TYPE,
        custom_options=[DialogOptionData("Receive blessing", "gain full health", HealAction()),
                        DialogOptionData("Ask for advice", "see random hint", HintAction())],
        dialog_before_quest="Greetings. I am here only to serve. Seek me out when you are wounded or need guidance!",
        dialog_give_quest="Greetings. I am here only to serve. Seek me out when you are wounded or need guidance!",
        dialog_during_quest="Greetings. I am here only to serve. Seek me out when you are wounded or need guidance!",
        dialog_after_completed="Greetings. I am here only to serve. Seek me out when you are wounded or need guidance!",
        reward_item_id=lambda _: plain_item_id(ItemType.PORTAL_KEY)
    )
