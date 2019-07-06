import random

from pythongame.core.ability_effects import register_ability_effect
from pythongame.core.buff_effects import AbstractBuffEffect, get_buff_effect, register_buff_effect
from pythongame.core.common import AbilityType, Millis, \
    translate_in_direction, BuffType
from pythongame.core.damage_interactions import deal_player_damage_to_enemy
from pythongame.core.game_data import register_ability_data, AbilityData, UiIconSprite, \
    register_ui_icon_sprite_path
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter
from pythongame.core.visual_effects import VisualRect
from pythongame.game_data.player_data import PLAYER_ENTITY_SIZE

MIN_DMG = 2
MAX_DMG = 4
BUFF_TYPE = BuffType.RECOVERING_AFTER_SWORD_SLASH


def _apply_ability(game_state: GameState) -> bool:
    player_entity = game_state.player_entity
    rect_w = 36
    slash_pos = translate_in_direction(
        player_entity.get_center_position(),
        player_entity.direction,
        rect_w / 2 + PLAYER_ENTITY_SIZE[0] * 0.25)

    slash_rect = (int(slash_pos[0] - rect_w / 2), int(slash_pos[1] - rect_w / 2), rect_w, rect_w)
    affected_enemies = game_state.get_enemy_intersecting_rect(slash_rect)
    for enemy in affected_enemies:
        damage: float = MIN_DMG + random.random() * (MAX_DMG - MIN_DMG)
        deal_player_damage_to_enemy(game_state, enemy, damage)

    game_state.visual_effects.append(
        VisualRect((100, 0, 0), slash_pos, rect_w, int(rect_w * 0.7), Millis(150), 2, None))
    game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE), Millis(150))
    return True


class RecoveringAfterSwordSlash(AbstractBuffEffect):
    def __init__(self):
        self._time_since_firing = 0

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.add_stun()
        game_state.player_entity.set_not_moving()

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.remove_stun()

    def get_buff_type(self):
        return BUFF_TYPE


def register_sword_slash_ability():
    ability_type = AbilityType.SWORD_SLASH
    ui_icon_sprite = UiIconSprite.ABILITY_SWORD_SLASH

    register_ability_effect(ability_type, _apply_ability)
    description = "Damages enemies in front of you (" + str(MIN_DMG) + "-" + str(MAX_DMG) + ")"
    register_ability_data(
        ability_type,
        AbilityData("Slash", ui_icon_sprite, 0, Millis(500), description, None))
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/icon_slash.png")
    register_buff_effect(BUFF_TYPE, RecoveringAfterSwordSlash)
