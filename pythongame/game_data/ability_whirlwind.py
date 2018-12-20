import random

from pythongame.core.ability_effects import register_ability_effect
from pythongame.core.buff_effects import AbstractBuffEffect, get_buff_effect, register_buff_effect
from pythongame.core.common import AbilityType, translate_in_direction, get_position_from_center_position, Sprite, \
    ProjectileType, Millis, Direction, BuffType
from pythongame.core.damage_interactions import deal_player_damage_to_enemy
from pythongame.core.game_data import register_ability_data, AbilityData, UiIconSprite, \
    register_ui_icon_sprite_path, register_entity_sprite_map, SpriteSheet
from pythongame.core.game_state import GameState, WorldEntity, Projectile, Enemy
from pythongame.core.projectile_controllers import create_projectile_controller, AbstractProjectileController, \
    register_projectile_controller
from pythongame.core.visual_effects import VisualRect

BUFF_TYPE = BuffType.STUNNED_BY_WHIRLWIND
PROJECTILE_SPRITE = Sprite.PROJECTILE_PLAYER_WHIRLWIND
PROJECTILE_TYPE = ProjectileType.PLAYER_WHIRLWIND
PROJECTILE_SIZE = (120, 90)


def _apply_ability(game_state: GameState):
    player_entity = game_state.player_entity
    aoe_center_pos = translate_in_direction(player_entity.get_center_position(), player_entity.direction, 60)
    aoe_pos = get_position_from_center_position(aoe_center_pos, PROJECTILE_SIZE)
    projectile_speed = 0.08
    entity = WorldEntity(aoe_pos, PROJECTILE_SIZE, PROJECTILE_SPRITE, player_entity.direction, projectile_speed)
    projectile = Projectile(entity, create_projectile_controller(PROJECTILE_TYPE))
    game_state.projectile_entities.append(projectile)


class ProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(3000)
        self._dmg_cooldown = 500
        self._time_since_dmg = self._dmg_cooldown
        self._direction_change_cooldown = 250
        self._time_since_direction_change = self._direction_change_cooldown
        self._relative_direction = 0
        self._stun_duration = 300

        self._rotation_motion = random.choice([-1, 1])

    def notify_time_passed(self, game_state: GameState, projectile: Projectile, time_passed: Millis):
        super().notify_time_passed(game_state, projectile, time_passed)
        self._time_since_dmg += time_passed
        self._time_since_direction_change += time_passed
        projectile_entity = projectile.world_entity
        if self._time_since_dmg > self._dmg_cooldown:
            self._time_since_dmg = 0
            for enemy in game_state.get_enemies_intersecting_with(projectile_entity):
                damage_amount = 1
                damage_was_dealt = deal_player_damage_to_enemy(game_state, enemy, damage_amount)
                if damage_was_dealt:
                    enemy.gain_buff_effect(get_buff_effect(BUFF_TYPE), Millis(self._stun_duration))

        if self._time_since_direction_change > self._direction_change_cooldown:
            self._time_since_direction_change = 0

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

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_enemy: Enemy):
        buffed_enemy.add_stun()
        effect_position = buffed_entity.get_center_position()
        game_state.visual_effects.append(
            VisualRect((250, 250, 50), effect_position, 30, 40, Millis(100), 1, buffed_entity))

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_enemy: Enemy,
                            time_passed: Millis):
        pass

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_enemy: Enemy):
        buffed_enemy.remove_stun()

    def get_buff_type(self):
        return BUFF_TYPE


def register_whirlwind_ability():
    ability_type = AbilityType.WHIRLWIND
    ui_icon_sprite = UiIconSprite.ABILITY_WHIRLWIND
    mana_cost = 8
    cooldown = Millis(750)

    register_ability_effect(ability_type, _apply_ability)
    register_ability_data(
        ability_type,
        AbilityData("Whirlwind", ui_icon_sprite, mana_cost, cooldown, "Deals damage to all enemies along its path"))
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/whirlwind.png")
    sprite_sheet = SpriteSheet("resources/graphics/ability_whirlwind_transparent_spritemap.png")
    original_sprite_size = (94, 111)
    scaled_sprite_size = (140, 140)
    indices_by_dir = {
        Direction.DOWN: [(0, 0), (1, 0), (2, 0), (1, 0)]
    }
    register_entity_sprite_map(PROJECTILE_SPRITE, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (-20, -50))
    register_projectile_controller(PROJECTILE_TYPE, ProjectileController)
    register_buff_effect(BUFF_TYPE, Stunned)
