from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory

ITEM_TYPE = ItemType.ELITE_ARMOR
HEALTH_REGEN_BOOST = 0.5
ARMOR_BOOST = 2


class ItemEffect(AbstractItemEffect):

    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.health_resource.regen_bonus += HEALTH_REGEN_BOOST
        game_state.player_state.armor_bonus += ARMOR_BOOST

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.health_resource.regen_bonus -= HEALTH_REGEN_BOOST
        game_state.player_state.armor_bonus -= ARMOR_BOOST

    def get_item_type(self):
        return ITEM_TYPE


def register_elite_armor():
    ui_icon_sprite = UiIconSprite.ITEM_ELITE_ARMOR
    sprite = Sprite.ITEM_ELITE_ARMOR
    image_file_path = "resources/graphics/item_elite_armor.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_effect(ITEM_TYPE, ItemEffect())
    name = "Elite Armor"
    description = [str(ARMOR_BOOST) + " armor",
                   "+" + str(HEALTH_REGEN_BOOST) + " health regen"]
    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.CHEST)
    register_item_data(ITEM_TYPE, item_data)
