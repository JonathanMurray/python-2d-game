from pythongame.core.ability_effects import register_ability_effect
from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect, get_buff_effect
from pythongame.core.common import BuffType, Millis, AbilityType, Sprite, ProjectileType, \
    get_position_from_center_position
from pythongame.core.damage_interactions import deal_player_damage_to_enemy
from pythongame.core.game_data import register_ability_data, AbilityData, UiIconSprite, register_ui_icon_sprite_path, \
    register_entity_sprite_initializer, SpriteInitializer, register_buff_text
from pythongame.core.game_state import GameState, Enemy, WorldEntity, Projectile
from pythongame.core.projectile_controllers import AbstractProjectileController, register_projectile_controller, \
    create_projectile_controller
from pythongame.core.visual_effects import VisualCircle, VisualRect

PROJECTILE_SIZE = (30, 30)


def _apply_channel_attack(game_state: GameState):
    game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.CHANNELING_MAGIC_MISSILES), Millis(1000))


class ChannelingMagicMissiles(AbstractBuffEffect):
    def __init__(self):
        self._time_since_firing = 0

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_enemy: Enemy):
        game_state.player_state.is_stunned = True
        game_state.player_entity.set_not_moving()

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_enemy: Enemy,
                            time_passed: Millis):
        self._time_since_firing += time_passed
        if self._time_since_firing > 150:
            self._time_since_firing = 0
            player_center_position = game_state.player_entity.get_center_position()
            projectile_pos = get_position_from_center_position(player_center_position, PROJECTILE_SIZE)
            entity = WorldEntity(projectile_pos, PROJECTILE_SIZE, Sprite.PROJECTILE_PLAYER_MAGIC_MISSILE,
                                 game_state.player_entity.direction, 0.5)
            projectile = Projectile(entity, create_projectile_controller(ProjectileType.PLAYER_MAGIC_MISSILE))
            game_state.projectile_entities.append(projectile)
            game_state.visual_effects.append(VisualRect((250, 0, 250), player_center_position, 45, 60, Millis(250), 1))

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_enemy: Enemy):
        game_state.player_state.is_stunned = False

    def get_buff_type(self):
        return BuffType.CHANNELING_MAGIC_MISSILES


class PlayerMagicMissileProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(400)
        self._enemies_hit = []

    def apply_enemy_collision(self, enemy: Enemy, game_state: GameState):
        if enemy not in self._enemies_hit:
            deal_player_damage_to_enemy(game_state, enemy, 1)
            game_state.visual_effects.append(
                VisualCircle((250, 100, 250), enemy.world_entity.get_center_position(), 15, 25, Millis(100), 0))
            self._enemies_hit.append(enemy)
        return False


def register_channel_attack_ability():
    register_ability_effect(AbilityType.CHANNEL_ATTACK, _apply_channel_attack)
    register_ability_data(
        AbilityType.CHANNEL_ATTACK,
        AbilityData("TODO", UiIconSprite.ABILITY_MAGIC_MISSILE, 12, Millis(8000), "TODO"))

    register_ui_icon_sprite_path(UiIconSprite.ABILITY_MAGIC_MISSILE, "resources/graphics/magic_missile.png")
    register_buff_effect(BuffType.CHANNELING_MAGIC_MISSILES, ChannelingMagicMissiles)
    register_entity_sprite_initializer(
        Sprite.PROJECTILE_PLAYER_MAGIC_MISSILE,
        SpriteInitializer("resources/graphics/magic_missile.png", PROJECTILE_SIZE))
    register_projectile_controller(ProjectileType.PLAYER_MAGIC_MISSILE, PlayerMagicMissileProjectileController)
    register_buff_text(BuffType.CHANNELING_MAGIC_MISSILES, "Channeling")
