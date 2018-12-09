import random

from pythongame.core.abilities import register_ability_effect
from pythongame.core.common import AbilityType, translate_in_direction, get_position_from_center_position, Sprite, \
    ProjectileType, Millis, get_perpendicular_directions
from pythongame.core.damage_interactions import deal_player_damage_to_enemy
from pythongame.core.game_data import register_ability_data, AbilityData, UiIconSprite, \
    register_ui_icon_sprite_path, SpriteInitializer, register_entity_sprite_initializer
from pythongame.core.game_state import GameState, WorldEntity, Projectile
from pythongame.core.projectiles import create_projectile_controller, AbstractProjectileController, \
    register_projectile_controller

AOE_PROJECTILE_SIZE = (140, 140)


def _apply_aoe_attack(game_state: GameState):
    player_entity = game_state.player_entity
    aoe_center_pos = translate_in_direction(player_entity.get_center_position(), player_entity.direction, 60)
    aoe_pos = get_position_from_center_position(aoe_center_pos, AOE_PROJECTILE_SIZE)
    projectile_speed = 0.07
    entity = WorldEntity(aoe_pos, AOE_PROJECTILE_SIZE, Sprite.WHIRLWIND, player_entity.direction,
                         projectile_speed)
    projectile = Projectile(entity, create_projectile_controller(ProjectileType.PLAYER_AOE))
    game_state.projectile_entities.append(projectile)


class PlayerAoeProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(3000)
        self._dmg_cooldown = 350
        self._time_since_dmg = self._dmg_cooldown

    def notify_time_passed(self, game_state: GameState, projectile: Projectile, time_passed: Millis):
        super().notify_time_passed(game_state, projectile, time_passed)
        self._time_since_dmg += time_passed
        if self._time_since_dmg > self._dmg_cooldown:
            self._time_since_dmg = False
            projectile_entity = projectile.world_entity
            for enemy in game_state.get_enemies_intersecting_with(projectile_entity):
                damage_amount = 1
                deal_player_damage_to_enemy(game_state, enemy, damage_amount)

            if random.random() < 0.07:
                projectile_entity.direction = random.choice(get_perpendicular_directions(projectile_entity.direction))


def register_aoe_attack_ability():
    register_ability_effect(AbilityType.AOE_ATTACK, _apply_aoe_attack)
    register_ability_data(AbilityType.AOE_ATTACK, AbilityData(UiIconSprite.AOE_ABILITY, 5, Millis(750)))
    register_ui_icon_sprite_path(UiIconSprite.AOE_ABILITY, "resources/graphics/whirlwind.png")
    register_entity_sprite_initializer(
        Sprite.WHIRLWIND, SpriteInitializer("resources/graphics/whirlwind.png", AOE_PROJECTILE_SIZE))
    register_projectile_controller(ProjectileType.PLAYER_AOE, PlayerAoeProjectileController)
