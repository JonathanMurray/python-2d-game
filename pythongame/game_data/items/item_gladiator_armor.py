from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer

ITEM_TYPE = ItemType.GLADIATOR_ARMOR
MAX_HEALTH_BOOST = 15
ARMOR_BOOST = 2
DAMAGE_BOOST = 0.05


class ItemEffect(AbstractItemEffect):

    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.health_resource.increase_max(MAX_HEALTH_BOOST)
        game_state.player_state.armor_bonus += ARMOR_BOOST
        game_state.player_state.damage_modifier_bonus += DAMAGE_BOOST

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.health_resource.decrease_max(MAX_HEALTH_BOOST)
        game_state.player_state.armor_bonus -= ARMOR_BOOST
        game_state.player_state.damage_modifier_bonus -= DAMAGE_BOOST

    def get_item_type(self):
        return ITEM_TYPE


def register_gladiator_armor():
    ui_icon_sprite = UiIconSprite.ITEM_GLADIATOR_ARMOR
    sprite = Sprite.ITEM_GLADIATOR_ARMOR
    image_file_path = "resources/graphics/item_gladiator_armor.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_effect(ITEM_TYPE, ItemEffect())
    name = "Gladiator's armor"
    description = [str(ARMOR_BOOST) + " armor",
                   "+" + str(MAX_HEALTH_BOOST) + " max health",
                   "+" + str(int(round(DAMAGE_BOOST * 100))) + "% damage"]
    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.CHEST)
    register_item_data(ITEM_TYPE, item_data)
