from pythongame.core.buff_effects import AbstractBuffEffect, get_buff_effect, register_buff_effect
from pythongame.core.common import ConsumableType, Sprite, UiIconSprite, SoundId, Millis, BuffType, PeriodicTimer
from pythongame.core.consumable_effects import register_consumable_effect, ConsumableWasConsumed
from pythongame.core.damage_interactions import deal_player_damage_to_enemy, DamageType
from pythongame.core.game_data import register_entity_sprite_initializer, register_ui_icon_sprite_path, \
    register_consumable_data, ConsumableData, POTION_ENTITY_SIZE, ConsumableCategory
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.view.image_loading import SpriteInitializer
from pythongame.core.visual_effects import VisualCircle
from pythongame.core.world_entity import WorldEntity

DAMAGE = 1
BUFF_TYPE = BuffType.POISONED_BY_ACID_BOMB
DEBUFF_DURATION = Millis(8_000)
DEBUFF_DAMAGE_INTERVAL = Millis(800)
DEBUFF_TOTAL_DAMAGE = int(round(DEBUFF_DURATION / DEBUFF_DAMAGE_INTERVAL))


class BuffEffect(AbstractBuffEffect):

    def __init__(self):
        self._timer = PeriodicTimer(DEBUFF_DAMAGE_INTERVAL)

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self._timer.update_and_check_if_ready(time_passed):
            deal_player_damage_to_enemy(game_state, buffed_npc, DAMAGE, DamageType.MAGIC)
            pos = buffed_entity.get_center_position()
            effect = VisualCircle((100, 150, 100), pos, 40, 50, Millis(500), 1)
            game_state.game_world.visual_effects += [effect]

    def get_buff_type(self):
        return BUFF_TYPE


def _apply(game_state: GameState):
    pos = game_state.game_world.player_entity.get_center_position()
    effect1 = VisualCircle((100, 150, 100), pos, 40, 120, Millis(2200), 2)
    effect2 = VisualCircle((100, 150, 100), pos, 40, 130, Millis(2000), 1)
    game_state.game_world.visual_effects += [effect1, effect2]

    affected_enemies = game_state.game_world.get_enemies_within_x_y_distance_of(120, pos)
    for enemy in affected_enemies:
        enemy.gain_buff_effect(get_buff_effect(BUFF_TYPE), DEBUFF_DURATION)

    return ConsumableWasConsumed()


def register_acid_bomb_consumable():
    consumable_type = ConsumableType.ACID_BOMB
    sprite = Sprite.CONSUMABLE_ACID_BOMB
    ui_icon_sprite = UiIconSprite.CONSUMABLE_ACID_BOMB

    register_consumable_effect(consumable_type, _apply)
    image_path = "resources/graphics/consumable_acid_bomb.png"
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_path, POTION_ENTITY_SIZE))
    register_ui_icon_sprite_path(ui_icon_sprite, image_path)
    description = "Poisons nearby enemies, dealing " + str(DEBUFF_TOTAL_DAMAGE) + " magic damage over " + \
                  "{:.0f}".format(DEBUFF_DURATION / 1000) + "s."
    data = ConsumableData(ui_icon_sprite, sprite, "Acid bomb", description, ConsumableCategory.OTHER,
                          SoundId.CONSUMABLE_ACID_BOMB)
    register_consumable_data(consumable_type, data)
    register_buff_effect(BUFF_TYPE, BuffEffect)
