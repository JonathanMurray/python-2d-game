from typing import Optional

from pygame.rect import Rect

from pythongame.core.abilities import AbilityData, register_ability_data
from pythongame.core.ability_effects import register_ability_effect, AbilityResult, AbilityWasUsedSuccessfully
from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect, get_buff_effect
from pythongame.core.common import BuffType, Millis, AbilityType, SoundId, HeroId, UiIconSprite, PeriodicTimer, \
    HeroUpgradeId, HeroStat
from pythongame.core.damage_interactions import deal_player_damage_to_enemy, DamageType
from pythongame.core.game_data import register_ui_icon_sprite_path, \
    HEROES, register_buff_as_channeling
from pythongame.core.game_state import GameState, NonPlayerCharacter, CameraShake
from pythongame.core.math import translate_in_direction, get_middle_point
from pythongame.core.sound_player import play_sound
from pythongame.core.visual_effects import VisualRect, VisualCircle
from pythongame.core.world_entity import WorldEntity

CHARGE_DURATION = Millis(500)
IMPACT_STUN_DURATION = Millis(200)
BONUS_SPEED_MULTIPLIER = 5
BUFF_TYPE_CHARGING = BuffType.CHARGING
BUFF_TYPE_STUNNED = BuffType.STUNNED_FROM_CHARGE_IMPACT

MIN_DMG = 4
MAX_DMG = 8


def _apply_ability(game_state: GameState) -> AbilityResult:
    game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE_CHARGING), CHARGE_DURATION)
    return AbilityWasUsedSuccessfully()


class Charging(AbstractBuffEffect):

    def __init__(self):
        self.graphics_timer = PeriodicTimer(Millis(40))
        self.time_since_start = 0

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.stun_status.add_one()
        game_state.modify_hero_stat(HeroStat.MOVEMENT_SPEED, BONUS_SPEED_MULTIPLIER)
        game_state.game_world.player_entity.set_moving_in_dir(game_state.game_world.player_entity.direction)

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis) -> Optional[bool]:

        self.time_since_start += time_passed

        charger_center_pos = buffed_entity.get_center_position()

        if self.graphics_timer.update_and_check_if_ready(time_passed):
            visual_circle = VisualCircle((250, 250, 250), charger_center_pos, 15, 25, Millis(120), 2, None)
            game_state.game_world.visual_effects.append(visual_circle)

        rect_w = 32
        # NOTE: We assume that this ability is used by this specific hero
        hero_entity_size = HEROES[HeroId.WARRIOR].entity_size
        impact_pos = translate_in_direction(
            charger_center_pos, buffed_entity.direction, rect_w / 2 + hero_entity_size[0] / 2)

        impact_rect = Rect(int(impact_pos[0] - rect_w / 2), int(impact_pos[1] - rect_w / 2), rect_w, rect_w)
        affected_enemies = game_state.game_world.get_enemy_intersecting_rect(impact_rect)
        for enemy in affected_enemies:
            visual_impact_pos = get_middle_point(charger_center_pos, enemy.world_entity.get_center_position())
            damage = MIN_DMG
            # Talent: Apply damage bonus even if using charge in melee range
            has_melee_upgrade = game_state.player_state.has_upgrade(HeroUpgradeId.ABILITY_CHARGE_MELEE)
            damage_increased = self.time_since_start > float(CHARGE_DURATION) * 0.3 or has_melee_upgrade
            if damage_increased:
                # TODO Stun target as a bonus here
                damage = MAX_DMG
            deal_player_damage_to_enemy(game_state, enemy, damage, DamageType.PHYSICAL,
                                        visual_emphasis=damage_increased)
            game_state.game_world.visual_effects.append(
                VisualRect((250, 170, 0), visual_impact_pos, 45, 25, IMPACT_STUN_DURATION, 2, None))
            game_state.game_world.visual_effects.append(
                VisualRect((150, 0, 0), visual_impact_pos, 35, 20, IMPACT_STUN_DURATION, 2, None))
            game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE_STUNNED), IMPACT_STUN_DURATION)
            enemy.gain_buff_effect(get_buff_effect(BUFF_TYPE_STUNNED), IMPACT_STUN_DURATION)
            game_state.camera_shake = CameraShake(Millis(50), Millis(150), 12)
            play_sound(SoundId.ABILITY_CHARGE_HIT)
            has_stomp_cooldown_upgrade = game_state.player_state.has_upgrade(
                HeroUpgradeId.ABILITY_CHARGE_RESET_STOMP_COOLDOWN)
            if has_stomp_cooldown_upgrade:
                game_state.player_state.set_ability_cooldown_to_zero(AbilityType.STOMP)
            # The buff should end upon impact
            return True
        return False

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.stun_status.remove_one()
        game_state.modify_hero_stat(HeroStat.MOVEMENT_SPEED, -BONUS_SPEED_MULTIPLIER)

    def get_buff_type(self):
        return BUFF_TYPE_CHARGING


class StunnedFromCharge(AbstractBuffEffect):

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        if buffed_npc:
            buffed_npc.stun_status.add_one()
        else:
            game_state.player_state.stun_status.add_one()
        buffed_entity.set_not_moving()

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        if buffed_npc:
            buffed_npc.stun_status.remove_one()
        else:
            game_state.player_state.stun_status.remove_one()

    def get_buff_type(self):
        return BUFF_TYPE_STUNNED


def register_charge_ability():
    ability_type = AbilityType.CHARGE
    register_ability_effect(ability_type, _apply_ability)
    ui_icon_sprite = UiIconSprite.ABILITY_CHARGE
    description = "Charge forward, dealing " + str(MIN_DMG) + "-" + str(
        MAX_DMG) + " physical damage on impact if an enemy is hit. (Higher damage on long range)"
    register_ability_data(
        ability_type,
        AbilityData("Charge", ui_icon_sprite, 12, Millis(5000), description, SoundId.ABILITY_CHARGE))
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/icon_charge.png")
    register_buff_effect(BUFF_TYPE_CHARGING, Charging)
    register_buff_as_channeling(BUFF_TYPE_CHARGING)
    register_buff_effect(BUFF_TYPE_STUNNED, StunnedFromCharge)
