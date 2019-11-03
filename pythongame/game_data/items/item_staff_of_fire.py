from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_custom_effect_item


class ItemEffect(AbstractItemEffect):

    def __init__(self, item_type: ItemType):
        super().__init__(item_type)
        self.fireball_damage_boost = 1

    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.fireball_dmg_boost += self.fireball_damage_boost

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.fireball_dmg_boost -= self.fireball_damage_boost

    def get_description(self):
        return ["(Only usable by mage)",
                "Increases the damage of your fireball ability by " + str(self.fireball_damage_boost)]


def register_staff_of_fire_item():
    item_type = ItemType.STAFF_OF_FIRE
    register_custom_effect_item(
        item_type=item_type,
        ui_icon_sprite=UiIconSprite.ITEM_STAFF_OF_FIRE,
        sprite=Sprite.ITEM_STAFF_OF_FIRE,
        image_file_path="resources/graphics/item_staff_of_fire.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Staff of Fire",
        item_effect=ItemEffect(item_type)
    )
