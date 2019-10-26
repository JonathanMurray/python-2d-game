from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.image_loading import SpriteInitializer
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory

ITEM_TYPES = [ItemType.AMULET_OF_MANA_1, ItemType.AMULET_OF_MANA_2, ItemType.AMULET_OF_MANA_3]
MANA_REGEN_BOOSTS = [0.5, 0.75, 1]


class ItemEffect(AbstractItemEffect):

    def __init__(self, mana_regen_boost: float, item_type: ItemType):
        self.mana_regen_boost = mana_regen_boost
        self.item_type = item_type

    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.mana_resource.regen_bonus += self.mana_regen_boost

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.mana_resource.regen_bonus -= self.mana_regen_boost

    def get_item_type(self):
        return self.item_type


def register_amulet_of_mana_item():
    ui_icon_sprite = UiIconSprite.ITEM_AMULET_OF_MANA
    sprite = Sprite.ITEM_AMULET_OF_MANA
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_amulet.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_amulet.png", ITEM_ENTITY_SIZE))
    for i in range(3):
        item_type = ITEM_TYPES[i]
        mana_regen_boost = MANA_REGEN_BOOSTS[i]
        register_item_effect(item_type, ItemEffect(mana_regen_boost, item_type))
        name = "Amulet of Mana (" + str(i + 1) + ")"
        description = ["+" + str(mana_regen_boost) + " mana regen"]
        item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.NECK)
        register_item_data(item_type, item_data)
