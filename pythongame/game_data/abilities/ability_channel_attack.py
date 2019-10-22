from pythongame.core.ability_effects import register_ability_effect, AbilityWasUsedSuccessfully, AbilityResult
from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect, get_buff_effect
from pythongame.core.common import BuffType, Millis, AbilityType, Sprite, ProjectileType, UiIconSprite, PeriodicTimer
from pythongame.core.damage_interactions import deal_player_damage_to_enemy
from pythongame.core.game_data import register_ability_data, AbilityData, register_ui_icon_sprite_path, \
    register_entity_sprite_initializer, SpriteInitializer, register_buff_as_channeling
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity, Projectile
from pythongame.core.math import get_position_from_center_position
from pythongame.core.projectile_controllers import AbstractProjectileController, register_projectile_controller, \
    create_projectile_controller
from pythongame.core.visual_effects import VisualCircle, VisualRect

CHANNEL_DURATION = Millis(1000)
PROJECTILE_SIZE = (30, 30)
PROJECTILE_SPEED = 0.7


def _apply_channel_attack(game_state: GameState) -> AbilityResult:
    game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.CHANNELING_MAGIC_MISSILES), CHANNEL_DURATION)
    return AbilityWasUsedSuccessfully()


class ChannelingMagicMissiles(AbstractBuffEffect):
    def __init__(self):
        self.timer = PeriodicTimer(Millis(70))

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.stun_status.add_one()
        game_state.player_entity.set_not_moving()

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            player_center_position = game_state.player_entity.get_center_position()
            projectile_pos = get_position_from_center_position(player_center_position, PROJECTILE_SIZE)
            entity = WorldEntity(projectile_pos, PROJECTILE_SIZE, Sprite.PROJECTILE_PLAYER_MAGIC_MISSILE,
                                 game_state.player_entity.direction, PROJECTILE_SPEED)
            projectile = Projectile(entity, create_projectile_controller(ProjectileType.PLAYER_MAGIC_MISSILE))
            game_state.projectile_entities.append(projectile)
            game_state.visual_effects.append(VisualRect((250, 0, 250), player_center_position, 45, 60, Millis(250), 1))

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.stun_status.remove_one()

    def get_buff_type(self):
        return BuffType.CHANNELING_MAGIC_MISSILES


class PlayerMagicMissileProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(500)
        self._enemies_hit = []

    def apply_enemy_collision(self, npc: NonPlayerCharacter, game_state: GameState, projectile: Projectile):
        if npc not in self._enemies_hit:
            damage = 1
            deal_player_damage_to_enemy(game_state, npc, damage)
            game_state.visual_effects.append(
                VisualCircle((250, 100, 250), npc.world_entity.get_center_position(), 15, 25, Millis(100), 0))
            self._enemies_hit.append(npc)
        # Projectile pierces enemies (so we don't mark projectile as destroyed)


def register_channel_attack_ability():
    register_ability_effect(AbilityType.CHANNEL_ATTACK, _apply_channel_attack)
    description = "Channel for " + "{:.1f}".format(CHANNEL_DURATION / 1000) + \
                  "s, firing piercing missiles in front of you that damage enemies."
    mana_cost = 40
    cooldown = Millis(30000)
    ability_data = AbilityData("Arcane Fire", UiIconSprite.ABILITY_MAGIC_MISSILE, mana_cost, cooldown, description,
                               None)
    register_ability_data(AbilityType.CHANNEL_ATTACK, ability_data)

    register_ui_icon_sprite_path(UiIconSprite.ABILITY_MAGIC_MISSILE, "resources/graphics/magic_missile.png")
    register_buff_effect(BuffType.CHANNELING_MAGIC_MISSILES, ChannelingMagicMissiles)
    register_entity_sprite_initializer(
        Sprite.PROJECTILE_PLAYER_MAGIC_MISSILE,
        SpriteInitializer("resources/graphics/magic_missile.png", PROJECTILE_SIZE))
    register_projectile_controller(ProjectileType.PLAYER_MAGIC_MISSILE, PlayerMagicMissileProjectileController)
    register_buff_as_channeling(BuffType.CHANNELING_MAGIC_MISSILES)
