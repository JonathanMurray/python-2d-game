from pythongame.core.ability_effects import register_ability_effect
from pythongame.core.buff_effects import register_buff_effect, AbstractBuffEffect, get_buff_effect
from pythongame.core.common import get_position_from_center_position, Sprite, ProjectileType, AbilityType, Millis, \
    Direction, translate_in_direction, BuffType
from pythongame.core.damage_interactions import deal_player_damage_to_enemy
from pythongame.core.game_data import register_ability_data, AbilityData, UiIconSprite, \
    register_ui_icon_sprite_path, SpriteSheet, \
    register_entity_sprite_map
from pythongame.core.game_state import GameState, WorldEntity, Projectile, Enemy
from pythongame.core.projectile_controllers import create_projectile_controller, AbstractProjectileController, \
    register_projectile_controller
from pythongame.core.visual_effects import VisualCircle

BUFF_TYPE = BuffType.ROOTED_BY_ENTANGLING_ROOTS

PROJECTILE_SPRITE = Sprite.PROJECTILE_PLAYER_ENTANGLING_ROOTS
PROJECTILE_TYPE = ProjectileType.PLAYER_ENTANGLING_ROOTS
ICON_SPRITE = UiIconSprite.ABILITY_ENTANGLING_ROOTS
ABILITY_TYPE = AbilityType.ENTANGLING_ROOTS
PROJECTILE_SIZE = (55, 55)


class ProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(1500)

    def apply_enemy_collision(self, enemy: Enemy, game_state: GameState):
        damage_was_dealt = deal_player_damage_to_enemy(game_state, enemy, 1)
        if not damage_was_dealt:
            return False
        enemy.gain_buff_effect(get_buff_effect(BUFF_TYPE), Millis(5000))
        return True


def _apply_ability(game_state: GameState):
    player_entity = game_state.player_entity
    distance_from_player = 35
    projectile_pos = translate_in_direction(
        get_position_from_center_position(player_entity.get_center_position(), PROJECTILE_SIZE),
        player_entity.direction,
        distance_from_player)
    projectile_speed = 0.1
    entity = WorldEntity(projectile_pos, PROJECTILE_SIZE, PROJECTILE_SPRITE, player_entity.direction,
                         projectile_speed)
    projectile = Projectile(entity, create_projectile_controller(PROJECTILE_TYPE))
    game_state.projectile_entities.append(projectile)
    effect_position = (projectile_pos[0] + PROJECTILE_SIZE[0] // 2,
                       projectile_pos[1] + PROJECTILE_SIZE[1] // 2)
    game_state.visual_effects.append(VisualCircle((250, 150, 50), effect_position, 9, 18, Millis(80), 0))


class Rooted(AbstractBuffEffect):

    def __init__(self):
        self._damage_interval = 1000
        self._graphics_interval = 500
        self._time_since_damage = self._damage_interval
        self._time_since_graphics = self._graphics_interval

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_enemy: Enemy):
        buffed_enemy.add_stun()

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_enemy: Enemy,
                            time_passed: Millis):
        self._time_since_damage += time_passed
        self._time_since_graphics += time_passed
        if self._time_since_damage > self._damage_interval:
            self._time_since_damage = 0
            deal_player_damage_to_enemy(game_state, buffed_enemy, 1)
        if self._time_since_graphics > self._graphics_interval:
            self._time_since_graphics = 0
            game_state.visual_effects.append(
                VisualCircle((0, 150, 0), buffed_entity.get_center_position(), 30, 55, Millis(150), 2, buffed_entity))

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_enemy: Enemy):
        buffed_enemy.remove_stun()

    def get_buff_type(self):
        return BUFF_TYPE


def register_entangling_roots_ability():
    register_ability_effect(ABILITY_TYPE, _apply_ability)
    register_ability_data(
        ABILITY_TYPE,
        AbilityData("Entangling roots", ICON_SPRITE, 5, Millis(3000), "Roots an enemy and deals damage over time"))
    register_ui_icon_sprite_path(ICON_SPRITE, "resources/graphics/ability_icon_entangling_roots.png")
    register_projectile_controller(PROJECTILE_TYPE, ProjectileController)

    sprite_sheet = SpriteSheet("resources/graphics/projectile_entangling_roots.png")
    original_sprite_size = (165, 214)
    indices_by_dir = {
        Direction.LEFT: [(x, 0) for x in range(9)]
    }
    register_entity_sprite_map(PROJECTILE_SPRITE, sprite_sheet, original_sprite_size, PROJECTILE_SIZE, indices_by_dir,
                               (0, 0))
    register_buff_effect(BUFF_TYPE, Rooted)
