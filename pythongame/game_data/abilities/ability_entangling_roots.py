from pythongame.core.abilities import AbilityData, ABILITIES, register_ability_data
from pythongame.core.ability_effects import register_ability_effect, AbilityResult, AbilityWasUsedSuccessfully
from pythongame.core.buff_effects import register_buff_effect, AbstractBuffEffect, get_buff_effect
from pythongame.core.common import Sprite, ProjectileType, AbilityType, Millis, \
    Direction, BuffType, SoundId, UiIconSprite, PeriodicTimer, HeroUpgradeId
from pythongame.core.damage_interactions import deal_player_damage_to_enemy, DamageType
from pythongame.core.game_data import register_ui_icon_sprite_path, \
    register_entity_sprite_map
from pythongame.core.game_state import GameState, Projectile, NonPlayerCharacter
from pythongame.core.hero_upgrades import register_hero_upgrade_effect, AbstractHeroUpgradeEffect
from pythongame.core.math import get_position_from_center_position, translate_in_direction
from pythongame.core.projectile_controllers import create_projectile_controller, AbstractProjectileController, \
    register_projectile_controller
from pythongame.core.sound_player import play_sound
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.core.visual_effects import VisualCircle, VisualSprite, create_visual_stun_text
from pythongame.core.world_entity import WorldEntity

ENTANGLING_ROOTS_COOLDOWN = Millis(12_000)
ENTANGLING_ROOTS_UPGRADED_COOLDOWN = Millis(8_000)

BUFF_TYPE = BuffType.ROOTED_BY_ENTANGLING_ROOTS

PROJECTILE_SPRITE = Sprite.PROJECTILE_PLAYER_ENTANGLING_ROOTS
PROJECTILE_TYPE = ProjectileType.PLAYER_ENTANGLING_ROOTS
ICON_SPRITE = UiIconSprite.ABILITY_ENTANGLING_ROOTS
ABILITY_TYPE = AbilityType.ENTANGLING_ROOTS
PROJECTILE_SIZE = (55, 55)
ENTANGLING_ROOTS_SIZE = (50, 50)
DEBUFF_DURATION = Millis(5000)
DEBUFF_DAMAGE_INTERVAL = Millis(500)
DEBUFF_TOTAL_DAMAGE = int(round(DEBUFF_DURATION / DEBUFF_DAMAGE_INTERVAL))


class ProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(1500)

    def apply_enemy_collision(self, npc: NonPlayerCharacter, game_state: GameState, projectile: Projectile):
        damage_was_dealt = deal_player_damage_to_enemy(game_state, npc, 1, DamageType.MAGIC)
        if damage_was_dealt:
            npc.gain_buff_effect(get_buff_effect(BUFF_TYPE), DEBUFF_DURATION)
            victim_center_pos = npc.world_entity.get_center_position()
            visual_effect_pos = (victim_center_pos[0] - ENTANGLING_ROOTS_SIZE[0] // 2,
                                 victim_center_pos[1] - ENTANGLING_ROOTS_SIZE[1] // 2)
            debuff_visual_effect = VisualSprite(Sprite.DECORATION_ENTANGLING_ROOTS_EFFECT, visual_effect_pos,
                                                DEBUFF_DURATION, npc.world_entity)
            game_state.game_world.visual_effects.append(debuff_visual_effect)
            play_sound(SoundId.ABILITY_ENTANGLING_ROOTS_HIT)
        projectile.has_collided_and_should_be_removed = True


def _apply_ability(game_state: GameState) -> AbilityResult:
    player_entity = game_state.game_world.player_entity
    distance_from_player = 35
    projectile_pos = translate_in_direction(
        get_position_from_center_position(player_entity.get_center_position(), PROJECTILE_SIZE),
        player_entity.direction,
        distance_from_player)
    projectile_speed = 0.2
    entity = WorldEntity(projectile_pos, PROJECTILE_SIZE, PROJECTILE_SPRITE, player_entity.direction,
                         projectile_speed)
    projectile = Projectile(entity, create_projectile_controller(PROJECTILE_TYPE))
    game_state.game_world.projectile_entities.append(projectile)
    effect_position = (projectile_pos[0] + PROJECTILE_SIZE[0] // 2,
                       projectile_pos[1] + PROJECTILE_SIZE[1] // 2)
    game_state.game_world.visual_effects.append(VisualCircle((250, 150, 50), effect_position, 9, 18, Millis(80), 0))
    return AbilityWasUsedSuccessfully()


class Rooted(AbstractBuffEffect):

    def __init__(self):
        self.timer = PeriodicTimer(DEBUFF_DAMAGE_INTERVAL)

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_npc.stun_status.add_one()
        buffed_entity.set_not_moving()
        game_state.game_world.visual_effects.append(create_visual_stun_text(buffed_entity))

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            deal_player_damage_to_enemy(game_state, buffed_npc, 1, DamageType.MAGIC)
            game_state.game_world.visual_effects.append(
                VisualCircle((0, 150, 0), buffed_entity.get_center_position(), 30, 55, Millis(150), 2, buffed_entity))

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_npc.stun_status.remove_one()

    def get_buff_type(self):
        return BUFF_TYPE


class UpgradeEntanglingRootsCooldown(AbstractHeroUpgradeEffect):
    def apply(self, game_state: GameState):
        ABILITIES[AbilityType.ENTANGLING_ROOTS].cooldown = ENTANGLING_ROOTS_UPGRADED_COOLDOWN

    def revert(self, game_state: GameState):
        ABILITIES[AbilityType.ENTANGLING_ROOTS].cooldown = ENTANGLING_ROOTS_COOLDOWN


def register_entangling_roots_ability():
    register_ability_effect(ABILITY_TYPE, _apply_ability)
    description = "Stun an enemy and deal " + str(DEBUFF_TOTAL_DAMAGE) + " magic damage over " + \
                  "{:.0f}".format(DEBUFF_DURATION / 1000) + "s."
    mana_cost = 22
    ability_data = AbilityData("Entangling roots", ICON_SPRITE, mana_cost, ENTANGLING_ROOTS_COOLDOWN, description,
                               SoundId.ABILITY_ENTANGLING_ROOTS)
    register_ability_data(ABILITY_TYPE, ability_data)
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
    _register_engangling_roots_effect_decoration()
    register_hero_upgrade_effect(HeroUpgradeId.ABILITY_ENTANGLING_ROOTS_COOLDOWN, UpgradeEntanglingRootsCooldown())


def _register_engangling_roots_effect_decoration():
    sprite_sheet = SpriteSheet("resources/graphics/entangling_roots.png")
    original_sprite_size = (130, 114)
    indices_by_dir = {Direction.DOWN: [(0, 0)]}
    register_entity_sprite_map(Sprite.DECORATION_ENTANGLING_ROOTS_EFFECT, sprite_sheet, original_sprite_size,
                               ENTANGLING_ROOTS_SIZE, indices_by_dir, (0, 0))
