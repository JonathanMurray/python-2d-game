import random

from pythongame.core.abilities import AbilityData, register_ability_data
from pythongame.core.ability_effects import register_ability_effect, AbilityWasUsedSuccessfully, AbilityResult
from pythongame.core.buff_effects import AbstractBuffEffect, get_buff_effect, register_buff_effect
from pythongame.core.common import AbilityType, Sprite, \
    ProjectileType, Millis, Direction, BuffType, SoundId, PeriodicTimer, HeroUpgradeId
from pythongame.core.damage_interactions import deal_player_damage_to_enemy, DamageType
from pythongame.core.game_data import UiIconSprite, \
    register_ui_icon_sprite_path, register_entity_sprite_map
from pythongame.core.game_state import GameState, Projectile, NonPlayerCharacter
from pythongame.core.math import get_position_from_center_position, translate_in_direction
from pythongame.core.projectile_controllers import create_projectile_controller, AbstractProjectileController, \
    register_projectile_controller
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.core.visual_effects import VisualRect, create_visual_stun_text
from pythongame.core.world_entity import WorldEntity

BUFF_TYPE = BuffType.STUNNED_BY_WHIRLWIND
PROJECTILE_SPRITE = Sprite.PROJECTILE_PLAYER_WHIRLWIND
PROJECTILE_TYPE = ProjectileType.PLAYER_WHIRLWIND
PROJECTILE_SIZE = (140, 110)

PROJECTILE_DURATION = Millis(3000)
PROJECTILE_DAMAGE_INTERVAL = Millis(350)
PROJECTILE_MAX_TOTAL_DAMAGE = int(round(PROJECTILE_DURATION / PROJECTILE_DAMAGE_INTERVAL))

WHIRLWIND_TALENT_STUN_DURATION = Millis(500)


def _apply_ability(game_state: GameState) -> AbilityResult:
    player_entity = game_state.game_world.player_entity
    aoe_center_pos = translate_in_direction(player_entity.get_center_position(), player_entity.direction, 60)
    aoe_pos = get_position_from_center_position(aoe_center_pos, PROJECTILE_SIZE)
    projectile_speed = 0.1
    entity = WorldEntity(aoe_pos, PROJECTILE_SIZE, PROJECTILE_SPRITE, player_entity.direction, projectile_speed)
    projectile = Projectile(entity, create_projectile_controller(PROJECTILE_TYPE))
    game_state.game_world.projectile_entities.append(projectile)
    has_lightfooted_upgrade = game_state.player_state.has_upgrade(HeroUpgradeId.MAGE_LIGHT_FOOTED)
    if not has_lightfooted_upgrade:
        game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.RECOVERING_AFTER_ABILITY), Millis(300))
    return AbilityWasUsedSuccessfully()


class ProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(PROJECTILE_DURATION)
        self.damage_timer = PeriodicTimer(PROJECTILE_DAMAGE_INTERVAL)
        self.direction_change_timer = PeriodicTimer(Millis(250))
        self._relative_direction = 0
        self._rotation_motion = random.choice([-1, 1])

    def notify_time_passed(self, game_state: GameState, projectile: Projectile, time_passed: Millis):
        super().notify_time_passed(game_state, projectile, time_passed)
        projectile_entity = projectile.world_entity

        if self.damage_timer.update_and_check_if_ready(time_passed):
            for enemy in game_state.game_world.get_enemy_intersecting_with(projectile_entity):
                damage_amount = 1
                damage_was_dealt = deal_player_damage_to_enemy(game_state, enemy, damage_amount, DamageType.MAGIC)
                if damage_was_dealt:
                    has_stun_upgrade = game_state.player_state.has_upgrade(HeroUpgradeId.ABILITY_WHIRLWIND_STUN)
                    if has_stun_upgrade and random.random() < 0.2:
                        enemy.gain_buff_effect(get_buff_effect(BUFF_TYPE), WHIRLWIND_TALENT_STUN_DURATION)

        if self.direction_change_timer.update_and_check_if_ready(time_passed):
            should_rotate = True
            # keep going straight ahead sometimes
            if self._relative_direction == 0 and random.random() < 0.5:
                should_rotate = False

            if should_rotate:
                if self._rotation_motion == 1:
                    projectile_entity.rotate_right()
                    self._relative_direction += 90
                elif self._rotation_motion == -1:
                    projectile_entity.rotate_left()
                    self._relative_direction -= 90

                if self._relative_direction == 90:
                    self._rotation_motion = -1
                elif self._relative_direction == -90:
                    self._rotation_motion = 1


class Stunned(AbstractBuffEffect):
    def __init__(self):
        pass

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_npc.stun_status.add_one()
        buffed_entity.set_not_moving()
        effect_position = buffed_entity.get_center_position()
        game_state.game_world.visual_effects.append(
            VisualRect((250, 250, 50), effect_position, 30, 40, Millis(100), 1, buffed_entity))
        game_state.game_world.visual_effects.append(create_visual_stun_text(buffed_entity))

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        pass

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_npc.stun_status.remove_one()

    def get_buff_type(self):
        return BUFF_TYPE


def register_whirlwind_ability():
    ability_type = AbilityType.WHIRLWIND
    ui_icon_sprite = UiIconSprite.ABILITY_WHIRLWIND
    mana_cost = 13
    cooldown = Millis(750)

    register_ability_effect(ability_type, _apply_ability)
    description = "Summon a whirlwind that deals up to " + str(PROJECTILE_MAX_TOTAL_DAMAGE) + \
                  " magic damage to enemies in its path."
    ability_data = AbilityData("Whirlwind", ui_icon_sprite, mana_cost, cooldown, description, SoundId.ABILITY_WHIRLWIND)
    register_ability_data(ability_type, ability_data)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/whirlwind.png")
    sprite_sheet = SpriteSheet("resources/graphics/ability_whirlwind_transparent_spritemap.png")
    original_sprite_size = (94, 111)
    scaled_sprite_size = (140, 140)
    indices_by_dir = {
        Direction.DOWN: [(0, 0), (1, 0), (2, 0), (1, 0)]
    }
    register_entity_sprite_map(PROJECTILE_SPRITE, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (-8, -50))
    register_projectile_controller(PROJECTILE_TYPE, ProjectileController)
    register_buff_effect(BUFF_TYPE, Stunned)
