from typing import Optional

from pythongame.core.common import NpcType, Sprite, Direction, PortraitIconSprite, \
    get_random_hint, ItemType, SoundId
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map
from pythongame.core.game_state import GameState, QuestId, Quest
from pythongame.core.item_data import plain_item_id
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcAction, \
    DialogOptionData
from pythongame.core.npc_quest_behaviors import register_quest_giver_dialog, QuestGiverNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.sound_player import play_sound
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.core.visual_effects import create_visual_healing_text

QUEST_ID = QuestId.MAIN_RETRIEVE_KEY
QUEST = Quest(QUEST_ID, "The red baron", "Defeat the red baron and retrieve the key that he stole.")

ITEM_TYPE_KEY = ItemType.KEY
NPC_TYPE = NpcType.NEUTRAL_NOMAD
PORTRAIT_ICON_SPRITE = PortraitIconSprite.NOMAD


def item_id_key():
    # We defer calling this method as key item may not be registered yet otherwise
    return plain_item_id(ITEM_TYPE_KEY)


class NpcMind(QuestGiverNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, QUEST_ID, plain_item_id(ITEM_TYPE_KEY))


# TODO use
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


def register_nomad_npc():
    sprite = Sprite.NEUTRAL_NPC_NOMAD
    register_npc_data(NPC_TYPE, NpcData.neutral(sprite=sprite, size=(30, 30), speed=0.03))
    register_npc_behavior(NPC_TYPE, NpcMind)
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
        quest_intro="The red baron... Yes, he has caused us much trouble. He stole from me a key that may "
                    "lead us out of here. You must bring it back to me!",
        boss_npc_type=NpcType.WARRIOR_KING,
        quest_item_type=ItemType.KEY,
        custom_options=[DialogOptionData("Receive blessing", "gain full health", HealAction()),
                        DialogOptionData("Ask for advice", "see random hint", HintAction())],
        dialog_give_quest="Greetings. I am here only to serve. Seek me out when you are wounded or need guidance!",
        dialog_during_quest="Greetings. I am here only to serve. Seek me out when you are wounded or need guidance!",
        dialog_after_completed="Greetings. I am here only to serve. Seek me out when you are wounded or need guidance!",
        reward_item_id=lambda _: None
    )
