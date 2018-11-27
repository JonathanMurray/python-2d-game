from pythongame.core.abilities import register_ability_effect
from pythongame.core.common import get_position_from_center_position, Sprite, ProjectileType, AbilityType, Millis, \
    Direction, translate_in_direction
from pythongame.core.game_data import register_ability_data, AbilityData, UiIconSprite, \
    register_ui_icon_sprite_path, SpriteSheet, \
    register_entity_sprite_map
from pythongame.core.game_state import GameState, WorldEntity, Projectile, Enemy
from pythongame.core.projectiles import create_projectile_controller, AbstractProjectileController, \
    register_projectile_controller
from pythongame.core.visual_effects import create_visual_damage_text, VisualCircle

PROJECTILE_SIZE = (48, 48)


class ProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(1500)

    def apply_enemy_collision(self, enemy: Enemy, game_state: GameState):
        damage_amount = 3
        enemy.lose_health(damage_amount)
        game_state.visual_effects.append(create_visual_damage_text(enemy.world_entity, damage_amount))
        game_state.visual_effects.append(VisualCircle((250, 100, 50), enemy.world_entity.get_center_position(), 45,
                                                      Millis(100), 0))
        return True


def _apply_ability(game_state: GameState):
    player_entity = game_state.player_entity
    distance_from_player = 35
    projectile_pos = translate_in_direction(
        get_position_from_center_position(player_entity.get_center_position(), PROJECTILE_SIZE),
        player_entity.direction,
        distance_from_player)
    projectile_speed = 0.3
    entity = WorldEntity(projectile_pos, PROJECTILE_SIZE, Sprite.PROJECTILE_PLAYER_FIREBALL, player_entity.direction,
                         projectile_speed)
    projectile = Projectile(entity, create_projectile_controller(ProjectileType.PLAYER_FIREBALL))
    game_state.projectile_entities.append(projectile)
    effect_circle_radius = 18
    effect_position = (projectile_pos[0] + PROJECTILE_SIZE[0] // 2,
                       projectile_pos[1] + PROJECTILE_SIZE[1] // 2)
    game_state.visual_effects.append(VisualCircle((250, 150, 50), effect_position, effect_circle_radius,
                                                  Millis(80), 0))


def register_fireball_ability():
    register_ability_effect(AbilityType.FIREBALL, _apply_ability)
    register_ability_data(AbilityType.FIREBALL, AbilityData(UiIconSprite.ABILITY_FIREBALL, 3, Millis(200)))
    register_ui_icon_sprite_path(UiIconSprite.ABILITY_FIREBALL, "resources/graphics/icon_fireball.png")
    register_projectile_controller(ProjectileType.PLAYER_FIREBALL, ProjectileController)

    sprite_sheet = SpriteSheet("resources/graphics/projectile_player_fireball.png")
    original_sprite_size = (64, 64)
    indices_by_dir = {
        Direction.LEFT: [(x, 0) for x in range(8)],
        Direction.UP: [(x, 2) for x in range(8)],
        Direction.RIGHT: [(x, 4) for x in range(8)],
        Direction.DOWN: [(x, 6) for x in range(8)]
    }
    register_entity_sprite_map(Sprite.PROJECTILE_PLAYER_FIREBALL, sprite_sheet, original_sprite_size, PROJECTILE_SIZE,
                               indices_by_dir, (0, 0))
