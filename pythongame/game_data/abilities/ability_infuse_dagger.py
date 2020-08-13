from pygame.rect import Rect

from pythongame.core.abilities import AbilityData, register_ability_data
from pythongame.core.ability_effects import register_ability_effect, AbilityWasUsedSuccessfully, AbilityFailedToExecute, \
    AbilityResult
from pythongame.core.buff_effects import get_buff_effect, AbstractBuffEffect, register_buff_effect
from pythongame.core.common import AbilityType, Millis, BuffType, UiIconSprite, SoundId, PeriodicTimer, \
    PLAYER_ENTITY_SIZE
from pythongame.core.damage_interactions import deal_player_damage_to_enemy, DamageType
from pythongame.core.game_data import register_ui_icon_sprite_path
from pythongame.core.game_state import GameState, NonPlayerCharacter, CameraShake
from pythongame.core.math import translate_in_direction
from pythongame.core.visual_effects import VisualRect, VisualCross, create_visual_stun_text
from pythongame.core.world_entity import WorldEntity

ABILITY_TYPE = AbilityType.INFUSE_DAGGER
DEBUFF = BuffType.DAMAGED_BY_INFUSED_DAGGER
DAMAGE_PER_TICK = 2
DAMAGE_TICK_INTERVAL = Millis(400)
DEBUFF_DURATION = Millis(5000)
TOTAL_DOT_DAMAGE = DEBUFF_DURATION // DAMAGE_TICK_INTERVAL * DAMAGE_PER_TICK


def _apply_ability(game_state: GameState) -> AbilityResult:
    player_entity = game_state.game_world.player_entity
    rect_w = 28
    slash_center_pos = translate_in_direction(
        player_entity.get_center_position(),
        player_entity.direction,
        rect_w / 2 + PLAYER_ENTITY_SIZE[0] * 0.25)
    slash_rect = Rect(int(slash_center_pos[0] - rect_w / 2), int(slash_center_pos[1] - rect_w / 2), rect_w, rect_w)
    affected_enemies = game_state.game_world.get_enemy_intersecting_rect(slash_rect)
    if not affected_enemies:
        return AbilityFailedToExecute(reason="No targets")

    # Note: Dependency on other ability 'stealth'
    should_stun = game_state.player_state.has_active_buff(BuffType.STEALTHING)
    if should_stun:
        game_state.camera_shake = CameraShake(Millis(50), Millis(150), 4)
    buff_effect = get_buff_effect(DEBUFF, should_stun)
    affected_enemies[0].gain_buff_effect(buff_effect, DEBUFF_DURATION)

    game_state.game_world.visual_effects.append(
        VisualRect((150, 150, 75), slash_center_pos, rect_w, int(rect_w * 0.7), Millis(200), 2, None))
    game_state.game_world.visual_effects.append(VisualCross((100, 100, 70), slash_center_pos, 6, Millis(100), 2))
    game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.RECOVERING_AFTER_ABILITY), Millis(250))
    return AbilityWasUsedSuccessfully()


class DamagedByInfusedDagger(AbstractBuffEffect):

    def __init__(self, should_stun: bool):
        self.timer = PeriodicTimer(DAMAGE_TICK_INTERVAL)
        self.should_stun = should_stun

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        if self.should_stun:
            buffed_npc.stun_status.add_one()
            buffed_entity.set_not_moving()
            game_state.game_world.visual_effects.append(create_visual_stun_text(buffed_entity))

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            deal_player_damage_to_enemy(game_state, buffed_npc, DAMAGE_PER_TICK, DamageType.PHYSICAL)
            if self.should_stun:
                effect_position = buffed_entity.get_center_position()
                game_state.game_world.visual_effects.append(
                    VisualRect((250, 250, 50), effect_position, 30, 40, Millis(100), 1, buffed_entity))

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        if self.should_stun:
            buffed_npc.stun_status.remove_one()

    def get_buff_type(self):
        return DEBUFF


def register_infuse_dagger_ability():
    ui_icon_sprite = UiIconSprite.ABILITY_INFUSE_DAGGER

    register_ability_effect(ABILITY_TYPE, _apply_ability)
    description = "Poison an enemy, dealing " + str(TOTAL_DOT_DAMAGE) + " physical damage over " + \
                  "{:.0f}".format(DEBUFF_DURATION / 1000) + "s. [from stealth: stun for full duration]"
    mana_cost = 18
    ability_data = AbilityData(
        "Infuse Dagger", ui_icon_sprite, mana_cost, Millis(10000), description, SoundId.ABILITY_INFUSE_DAGGER)
    register_ability_data(ABILITY_TYPE, ability_data)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/ability_infuse_dagger.png")

    register_buff_effect(DEBUFF, DamagedByInfusedDagger)
