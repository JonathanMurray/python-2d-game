import random

from pythongame.core.ability_effects import register_ability_effect, AbilityWasUsedSuccessfully, AbilityResult
from pythongame.core.buff_effects import get_buff_effect, AbstractBuffEffect, register_buff_effect
from pythongame.core.common import Sprite, ProjectileType, AbilityType, Millis, \
    Direction, SoundId, BuffType, PeriodicTimer, HeroUpgrade
from pythongame.core.damage_interactions import deal_player_damage_to_enemy
from pythongame.core.game_data import register_ability_data, AbilityData, UiIconSprite, \
    register_ui_icon_sprite_path, register_entity_sprite_map, ABILITIES
from pythongame.core.game_state import GameState, WorldEntity, Projectile, NonPlayerCharacter
from pythongame.core.hero_upgrades import register_hero_upgrade_effect
from pythongame.core.math import get_position_from_center_position, translate_in_direction
from pythongame.core.projectile_controllers import create_projectile_controller, AbstractProjectileController, \
    register_projectile_controller
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.core.visual_effects import VisualCircle, VisualParticleSystem

# Note: Projectile size must be smaller than hero entity size (otherwise you get a collision when shooting next to wall)
PROJECTILE_SIZE = (28, 28)
MIN_DMG = 3
MAX_DMG = 4

BUFF_TYPE = BuffType.BURNT_BY_FIREBALL


def _create_visual_splash(effect_position, game_state):
    game_state.visual_effects.append(
        VisualCircle((250, 100, 50), effect_position, 22, 45, Millis(100), 0))
    particle_colors = [(250, 100, 100),
                       (250, 50, 100),
                       (250, 100, 50)]
    particle_system = VisualParticleSystem(
        num_particles=10,
        position=effect_position,
        colors=particle_colors,
        alpha=100,
        duration_interval=(Millis(50), Millis(200)))
    game_state.visual_effects.append(particle_system)


class ProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(1500)

    def apply_enemy_collision(self, npc: NonPlayerCharacter, game_state: GameState, projectile: Projectile):
        base_damage: float = MIN_DMG + random.random() * (MAX_DMG - MIN_DMG)
        damage_amount = base_damage + game_state.player_state.fireball_dmg_boost
        deal_player_damage_to_enemy(game_state, npc, damage_amount)
        _create_visual_splash(npc.world_entity.get_center_position(), game_state)
        has_burn_upgrade = game_state.player_state.has_upgrade(HeroUpgrade.ABILITY_FIREBALL_BURN)
        if has_burn_upgrade:
            npc.gain_buff_effect(get_buff_effect(BUFF_TYPE), Millis(2500))
        projectile.has_collided_and_should_be_removed = True

    def apply_wall_collision(self, game_state: GameState, projectile: Projectile):
        _create_visual_splash(projectile.world_entity.get_center_position(), game_state)
        projectile.has_collided_and_should_be_removed = True


class BurntByFireball(AbstractBuffEffect):
    def __init__(self):
        self.timer = PeriodicTimer(Millis(500))

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            deal_player_damage_to_enemy(game_state, buffed_npc, 1)
            game_state.visual_effects.append(
                VisualCircle((180, 50, 50), buffed_npc.world_entity.get_center_position(), 10, 20, Millis(50), 0,
                             buffed_entity))

    def get_buff_type(self):
        return BUFF_TYPE


def _apply_ability(game_state: GameState) -> AbilityResult:
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
    effect_position = (projectile_pos[0] + PROJECTILE_SIZE[0] // 2,
                       projectile_pos[1] + PROJECTILE_SIZE[1] // 2)
    game_state.visual_effects.append(VisualCircle((250, 150, 50), effect_position, 15, 5, Millis(300), 0))
    game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.RECOVERING_AFTER_ABILITY), Millis(300))
    return AbilityWasUsedSuccessfully()


def _upgrade_fireball_mana_cost(_game_state: GameState):
    ABILITIES[AbilityType.FIREBALL].mana_cost -= 1


def register_fireball_ability():
    register_ability_effect(AbilityType.FIREBALL, _apply_ability)
    description = "Shoot a fireball, dealing " + str(MIN_DMG) + "-" + str(MAX_DMG) + \
                  " damage to the first enemy that it hits."
    register_ability_data(
        AbilityType.FIREBALL,
        AbilityData("Fireball", UiIconSprite.ABILITY_FIREBALL, 4, Millis(500), description, SoundId.ABILITY_FIREBALL))
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
    scaled_sprite_size = (48, 48)
    register_entity_sprite_map(Sprite.PROJECTILE_PLAYER_FIREBALL, sprite_sheet, original_sprite_size,
                               scaled_sprite_size, indices_by_dir, (-9, -9))
    register_buff_effect(BUFF_TYPE, BurntByFireball)
    register_hero_upgrade_effect(HeroUpgrade.ABILITY_FIREBALL_MANA_COST, _upgrade_fireball_mana_cost)
