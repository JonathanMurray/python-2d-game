from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory

ITEM_TYPES = [ItemType.ORB_OF_WISDOM_1, ItemType.ORB_OF_WISDOM_2, ItemType.ORB_OF_WISDOM_3]
BONUSES = [0.5, 0.75, 1]


class ItemEffect(AbstractItemEffect):

    def __init__(self, bonus: float, item_type: ItemType):
        self.bonus = bonus
        self.item_type = item_type

    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.mana_resource.regen_bonus += self.bonus

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.mana_resource.regen_bonus -= self.bonus

    def get_item_type(self):
        return self.item_type


def register_orb_of_wisdom_item():
    ui_icon_sprite = UiIconSprite.ITEM_ORB_OF_WISDOM
    sprite = Sprite.ITEM_ORB_OF_WISDOM
    image_file_path = "resources/graphics/item_orb_of_wisdom.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(
        sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    for i in range(3):
        item_type = ITEM_TYPES[i]
        bonus = BONUSES[i]
        register_item_effect(item_type, ItemEffect(bonus, item_type))
        name = "Orb of Wisdom (" + str(i + 1) + ")"
        description = "Grants +" + str(bonus) + " mana regeneration"
        item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.OFF_HAND)
        register_item_data(item_type, item_data)
