import random

from pythongame.core.abilities import AbilityData, register_ability_data
from pythongame.core.ability_effects import register_ability_effect, AbilityWasUsedSuccessfully, AbilityResult
from pythongame.core.buff_effects import get_buff_effect, AbstractBuffEffect, register_buff_effect
from pythongame.core.common import AbilityType, Millis, BuffType, UiIconSprite, SoundId, PeriodicTimer
from pythongame.core.damage_interactions import deal_player_damage_to_enemy, DamageType
from pythongame.core.game_data import register_ui_icon_sprite_path, \
    register_buff_as_channeling
from pythongame.core.game_state import GameState, NonPlayerCharacter, CameraShake
from pythongame.core.sound_player import play_sound
from pythongame.core.visual_effects import VisualRect, VisualCircle, create_visual_stun_text
from pythongame.core.world_entity import WorldEntity

STUN_DURATION = Millis(2500)
CHANNELING_STOMP = BuffType.CHANNELING_STOMP
STUNNED_BY_STOMP = BuffType.STUNNED_BY_STOMP

MIN_DMG = 2
MAX_DMG = 5


def _apply_ability(game_state: GameState) -> AbilityResult:
    game_state.player_state.gain_buff_effect(get_buff_effect(CHANNELING_STOMP), Millis(500))
    return AbilityWasUsedSuccessfully()


class ChannelingStomp(AbstractBuffEffect):

    def __init__(self):
        self.timer = PeriodicTimer(Millis(80))
        self.graphics_size = 40

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.stun_status.add_one()
        game_state.game_world.player_entity.set_not_moving()

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis) -> bool:
        if self.timer.update_and_check_if_ready(time_passed):
            visual_effect = VisualCircle(
                (250, 250, 250), buffed_entity.get_center_position(), self.graphics_size, self.graphics_size + 10,
                Millis(70), 2, None)
            self.graphics_size -= 7
            game_state.game_world.visual_effects.append(visual_effect)
        return False

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.stun_status.remove_one()
        hero_center_pos = game_state.game_world.player_entity.get_center_position()
        distance = 80
        affected_enemies = game_state.game_world.get_enemies_within_x_y_distance_of(distance, hero_center_pos)
        game_state.game_world.visual_effects.append(
            VisualRect((50, 50, 50), hero_center_pos, distance * 2, int(distance * 2.1), Millis(200), 2, None))
        game_state.game_world.visual_effects.append(
            VisualRect((150, 150, 0), hero_center_pos, distance, distance * 2, Millis(150), 3, None))
        game_state.game_world.visual_effects.append(
            VisualRect((250, 250, 0), hero_center_pos, distance, distance * 2, Millis(100), 4, None))
        for enemy in affected_enemies:
            damage: float = MIN_DMG + random.random() * (MAX_DMG - MIN_DMG)
            deal_player_damage_to_enemy(game_state, enemy, damage, DamageType.PHYSICAL)
            enemy.gain_buff_effect(get_buff_effect(STUNNED_BY_STOMP), STUN_DURATION)
        game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.RECOVERING_AFTER_ABILITY), Millis(300))
        play_sound(SoundId.ABILITY_STOMP_HIT)
        game_state.camera_shake = CameraShake(Millis(50), Millis(200), 12)

    def get_buff_type(self):
        return CHANNELING_STOMP


class StunnedFromStomp(AbstractBuffEffect):

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_npc.stun_status.add_one()
        buffed_entity.set_not_moving()
        game_state.game_world.visual_effects.append(create_visual_stun_text(buffed_entity))

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_npc.stun_status.remove_one()

    def get_buff_type(self):
        return STUNNED_BY_STOMP


def register_stomp_ability():
    ability_type = AbilityType.STOMP
    ui_icon_sprite = UiIconSprite.ABILITY_STOMP

    register_ability_effect(ability_type, _apply_ability)
    description = "Deal " + str(MIN_DMG) + "-" + str(MAX_DMG) + " physical damage to all enemies around you and stun " + \
                  "them for " + "{:.1f}".format(STUN_DURATION / 1000) + "s."
    register_ability_data(
        ability_type,
        AbilityData("War Stomp", ui_icon_sprite, 13, Millis(10000), description, SoundId.ABILITY_STOMP))
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/warstomp_icon.png")
    register_buff_effect(CHANNELING_STOMP, ChannelingStomp)
    register_buff_as_channeling(CHANNELING_STOMP)
    register_buff_effect(STUNNED_BY_STOMP, StunnedFromStomp)
