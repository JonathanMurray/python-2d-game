from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory

ITEM_TYPE = ItemType.ROYAL_SWORD
DAMAGE_BONUS = 0.1
ARMOR_BONUS = 1


class ItemEffect(AbstractItemEffect):
    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.damage_modifier_bonus += DAMAGE_BONUS
        game_state.player_state.armor_bonus += ARMOR_BONUS

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.damage_modifier_bonus -= DAMAGE_BONUS
        game_state.player_state.armor_bonus -= ARMOR_BONUS

    def get_item_type(self):
        return ITEM_TYPE


def register_royal_sword_item():
    ui_icon_sprite = UiIconSprite.ITEM_ROYAL_SWORD
    sprite = Sprite.ITEM_ROYAL_SWORD
    register_item_effect(ITEM_TYPE, ItemEffect())
    image_file_path = "resources/graphics/item_royal_sword.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    description = [str(ARMOR_BONUS) + " armor",
                   "+" + str(int(round(DAMAGE_BONUS * 100))) + "% damage"]
    item_data = ItemData(ui_icon_sprite, sprite, "Royal Sword", description, ItemEquipmentCategory.MAIN_HAND)
    register_item_data(ITEM_TYPE, item_data)
