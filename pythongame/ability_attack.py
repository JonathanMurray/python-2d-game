import pygame

from pythongame.abilities import register_ability_effect
from pythongame.common import get_position_from_center_position, Sprite, ProjectileType, AbilityType, Millis
from pythongame.game_data import register_ability_data, AbilityData, UiIconSprite, \
    register_ui_icon_sprite_path, register_entity_sprite_initializer, SpriteInitializer
from pythongame.game_state import GameState, WorldEntity, Projectile, Enemy
from pythongame.projectiles import create_projectile_controller, AbstractProjectileController, \
    register_projectile_controller
from pythongame.visual_effects import create_visual_damage_text, VisualCircle

ATTACK_PROJECTILE_SIZE = (25, 25)


class PlayerProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(3000)

    def apply_enemy_collision(self, enemy: Enemy, game_state: GameState):
        damage_amount = 3
        enemy.lose_health(damage_amount)
        game_state.visual_effects.append(create_visual_damage_text(enemy.world_entity, damage_amount))
        game_state.visual_effects.append(VisualCircle((250, 100, 50), enemy.world_entity.get_center_position(), 45,
                                                      Millis(100), 0))
        return True


def _apply_attack(game_state: GameState):
    player_center_position = game_state.player_entity.get_center_position()
    projectile_pos = get_position_from_center_position(player_center_position, ATTACK_PROJECTILE_SIZE)
    entity = WorldEntity(projectile_pos, ATTACK_PROJECTILE_SIZE, Sprite.FIREBALL, game_state.player_entity.direction,
                         0.3)
    projectile = Projectile(entity, create_projectile_controller(ProjectileType.PLAYER))
    game_state.projectile_entities.append(projectile)


def register_attack_ability():
    register_ability_effect(AbilityType.ATTACK, _apply_attack)
    register_ability_data(AbilityType.ATTACK, AbilityData(UiIconSprite.ATTACK_ABILITY, 3, "Q", pygame.K_q, Millis(200)))
    register_ui_icon_sprite_path(UiIconSprite.ATTACK_ABILITY, "resources/fireball.png")
    register_entity_sprite_initializer(
        Sprite.FIREBALL, SpriteInitializer("resources/fireball.png", ATTACK_PROJECTILE_SIZE))
    register_projectile_controller(ProjectileType.PLAYER, PlayerProjectileController)
