from pythongame.core.ability_effects import register_ability_effect
from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect, get_buff_effect
from pythongame.core.common import BuffType, Millis, AbilityType, SoundId
from pythongame.core.damage_interactions import deal_player_damage_to_enemy
from pythongame.core.game_data import register_ability_data, AbilityData, UiIconSprite, register_ui_icon_sprite_path, \
    register_buff_text
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter
from pythongame.core.math import translate_in_direction, get_middle_point
from pythongame.core.visual_effects import VisualRect, VisualCircle
from pythongame.game_data.player_data import PLAYER_ENTITY_SIZE

CHARGE_DURATION = Millis(500)
IMPACT_STUN_DURATION = Millis(200)
BONUS_SPEED_MULTIPLIER = 5
BUFF_TYPE_CHARGING = BuffType.CHARGING
BUFF_TYPE_STUNNED = BuffType.STUNNED_FROM_CHARGE_IMPACT


def _apply_ability(game_state: GameState) -> bool:
    game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE_CHARGING), CHARGE_DURATION)
    return True


class Charging(AbstractBuffEffect):

    def __init__(self):
        self.time_since_graphics = 0
        self.time_since_start = 0

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.add_stun()
        game_state.player_entity.add_to_speed_multiplier(BONUS_SPEED_MULTIPLIER)
        game_state.player_entity.set_moving_in_dir(game_state.player_entity.direction)

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis) -> bool:

        self.time_since_graphics += time_passed
        self.time_since_start += time_passed

        charger_center_pos = buffed_entity.get_center_position()

        if self.time_since_graphics > 40:
            self.time_since_graphics = 0
            game_state.visual_effects.append(VisualCircle((250, 250, 250), charger_center_pos, 15, 25, Millis(120),
                                                          2, None))

        rect_w = 32
        impact_pos = translate_in_direction(
            charger_center_pos, buffed_entity.direction, rect_w / 2 + PLAYER_ENTITY_SIZE[0] / 2)

        impact_rect = (int(impact_pos[0] - rect_w / 2), int(impact_pos[1] - rect_w / 2), rect_w, rect_w)
        affected_enemies = game_state.get_enemy_intersecting_rect(impact_rect)
        for enemy in affected_enemies:
            visual_impact_pos = get_middle_point(charger_center_pos, enemy.world_entity.get_center_position())
            damage = 4
            if self.time_since_start > float(CHARGE_DURATION) * 0.3:
                damage += 4
            deal_player_damage_to_enemy(game_state, enemy, damage)
            game_state.visual_effects.append(
                VisualRect((250, 170, 0), visual_impact_pos, 45, 25, IMPACT_STUN_DURATION, 2, None))
            game_state.visual_effects.append(
                VisualRect((150, 0, 0), visual_impact_pos, 35, 20, IMPACT_STUN_DURATION, 2, None))
            game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE_STUNNED), IMPACT_STUN_DURATION)
            enemy.gain_buff_effect(get_buff_effect(BUFF_TYPE_STUNNED), IMPACT_STUN_DURATION)

            return True
        return False

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.remove_stun()
        game_state.player_entity.add_to_speed_multiplier(-BONUS_SPEED_MULTIPLIER)

    def get_buff_type(self):
        return BUFF_TYPE_CHARGING


class StunnedFromCharge(AbstractBuffEffect):

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        if buffed_npc:
            buffed_npc.add_stun()
        else:
            game_state.player_state.add_stun()
        buffed_entity.set_not_moving()

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        if buffed_npc:
            buffed_npc.remove_stun()
        else:
            game_state.player_state.remove_stun()

    def get_buff_type(self):
        return BUFF_TYPE_STUNNED


def register_charge_ability():
    ability_type = AbilityType.CHARGE
    register_ability_effect(ability_type, _apply_ability)
    ui_icon_sprite = UiIconSprite.ABILITY_CHARGE
    description = "Charge forward, damaging enemy on impact"
    register_ability_data(
        ability_type,
        AbilityData("Charge", ui_icon_sprite, 5, Millis(5000), description, SoundId.ABILITY_CHARGE))
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/icon_charge.png")
    register_buff_effect(BUFF_TYPE_CHARGING, Charging)
    register_buff_text(BUFF_TYPE_CHARGING, "Charging")
    register_buff_effect(BUFF_TYPE_STUNNED, StunnedFromCharge)
