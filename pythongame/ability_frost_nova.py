from pythongame.core.abilities import register_ability_effect, Sprite
from pythongame.core.buffs import AbstractBuffEffect, register_buff_effect, get_buff_effect
from pythongame.core.common import AbilityType, Millis, \
    Direction, get_position_from_center_position, BuffType
from pythongame.core.game_data import register_ability_data, AbilityData, UiIconSprite, \
    register_ui_icon_sprite_path, SpriteSheet, register_entity_sprite_map
from pythongame.core.game_state import GameState, WorldEntity
from pythongame.core.visual_effects import VisualCircle, create_visual_damage_text, VisualSprite, VisualRect

EFFECT_SPRITE_SIZE = (230, 230)


def _apply_ability(game_state: GameState):
    player_entity = game_state.player_entity

    effect_circle_radius = 190
    player_center_pos = player_entity.get_center_position()
    game_state.visual_effects.append(
        VisualCircle((150, 150, 250), player_center_pos, effect_circle_radius, Millis(200), 3))
    affected_enemies = game_state.get_enemies_within_x_y_distance_of(180, player_center_pos)
    effect_position = get_position_from_center_position(player_center_pos, EFFECT_SPRITE_SIZE)
    game_state.visual_effects.append(VisualSprite(Sprite.EFFECT_ABILITY_FROST_NOVA, effect_position, Millis(200)))
    for enemy in affected_enemies:
        damage_amount = 2
        enemy.lose_health(damage_amount)
        game_state.visual_effects.append(create_visual_damage_text(enemy.world_entity, damage_amount))
        enemy.gain_buff_effect(get_buff_effect(BuffType.REDUCED_MOVEMENT_SPEED), Millis(4000))


class ReducedMovementSpeed(AbstractBuffEffect):
    def __init__(self):
        self._time_since_graphics = 0
        self._slow_amount = 0.75

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity):
        buffed_entity.add_to_speed_multiplier(-self._slow_amount)

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, time_passed: Millis):
        self._time_since_graphics += time_passed
        if self._time_since_graphics > 250:
            game_state.visual_effects.append(
                VisualRect((0, 100, 200), buffed_entity.get_center_position(), 50, Millis(80), buffed_entity))
            self._time_since_graphics = 0

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity):
        buffed_entity.add_to_speed_multiplier(self._slow_amount)

    def get_buff_type(self):
        return BuffType.REDUCED_MOVEMENT_SPEED


def register_frost_nova_ability():
    ability_type = AbilityType.FROST_NOVA
    register_ability_effect(ability_type, _apply_ability)
    ui_icon_sprite = UiIconSprite.ABILITY_FROST_NOVA
    register_ability_data(ability_type, AbilityData(ui_icon_sprite, 5, Millis(2000)))
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/ui_icon_ability_frost_nova.png")

    sprite_sheet = SpriteSheet("resources/graphics/effect_frost_explosion.png")
    original_sprite_size = (128, 130)
    indices_by_dir = {
        Direction.LEFT: [(x, 0) for x in range(6)]
    }
    register_entity_sprite_map(Sprite.EFFECT_ABILITY_FROST_NOVA, sprite_sheet, original_sprite_size, EFFECT_SPRITE_SIZE,
                               indices_by_dir, (0, 0))
    register_buff_effect(BuffType.REDUCED_MOVEMENT_SPEED, ReducedMovementSpeed)
