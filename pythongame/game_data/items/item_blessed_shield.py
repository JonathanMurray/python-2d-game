from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect

ITEM_TYPES = [ItemType.BLESSED_SHIELD_1, ItemType.BLESSED_SHIELD_2, ItemType.BLESSED_SHIELD_3]
HEALTH_REGEN_BOOSTS = [0.2, 0.3, 0.4]


class ItemEffect(AbstractItemEffect):

    def __init__(self, health_regen_boost: float, item_type: ItemType):
        self.health_regen_boost = health_regen_boost
        self.item_type = item_type

    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.health_resource.regen += self.health_regen_boost

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.health_resource.regen -= self.health_regen_boost

    def get_item_type(self):
        return self.item_type


def register_blessed_shield_item():
    ui_icon_sprite = UiIconSprite.ITEM_BLESSED_SHIELD
    sprite = Sprite.ITEM_BLESSED_SHIELD
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_blessed_shield.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_blessed_shield.png", ITEM_ENTITY_SIZE))
    for i in range(3):
        item_type = ITEM_TYPES[i]
        health_regen_boost = HEALTH_REGEN_BOOSTS[i]
        register_item_effect(item_type, ItemEffect(health_regen_boost, item_type))
        name = "Blessed Shield (" + str(i + 1) + ")"
        description = "Grants +" + str(health_regen_boost) + " health regeneration"
        register_item_data(item_type, ItemData(ui_icon_sprite, sprite, name, description))
