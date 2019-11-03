from pythongame.core.buff_effects import get_buff_effect, register_buff_effect, AbstractBuffEffect
from pythongame.core.common import ItemType, Sprite, BuffType, Millis, PeriodicTimer
from pythongame.core.damage_interactions import deal_player_damage_to_enemy
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import Event, PlayerDamagedEnemy, GameState, WorldEntity, \
    NonPlayerCharacter
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer
from pythongame.core.visual_effects import VisualCircle

ITEM_TYPE = ItemType.GOATS_RING
BUFF_TYPE = BuffType.DEBUFFED_BY_GOATS_RING
DAMAGE_SOURCE = "goats_ring"


class ItemEffect(AbstractItemEffect):

    def __init__(self, item_type: ItemType):
        super().__init__(item_type)

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerDamagedEnemy):
            # Compare "source" to prevent the debuff from renewing itself indefinitely
            if event.damage_source != DAMAGE_SOURCE:
                event.enemy_npc.gain_buff_effect(get_buff_effect(BUFF_TYPE), Millis(6000))


class DebuffedByGoatsRing(AbstractBuffEffect):

    def __init__(self):
        self.dmg_timer = PeriodicTimer(Millis(1000))
        self.graphics_timer = PeriodicTimer(Millis(400))

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.dmg_timer.update_and_check_if_ready(time_passed):
            deal_player_damage_to_enemy(game_state, buffed_npc, 1, DAMAGE_SOURCE)
        if self.graphics_timer.update_and_check_if_ready(time_passed):
            position = buffed_entity.get_center_position()
            visual_effect1 = VisualCircle((0, 100, 40), position, 9, 16, Millis(400), 2, buffed_entity)
            visual_effect2 = VisualCircle((0, 180, 90), position, 9, 16, Millis(500), 2, buffed_entity)
            game_state.visual_effects.append(visual_effect1)
            game_state.visual_effects.append(visual_effect2)

    def get_buff_type(self):
        return BUFF_TYPE


def register_goats_ring():
    ui_icon_sprite = UiIconSprite.ITEM_GOATS_RING
    sprite = Sprite.ITEM_GOATS_RING
    image_file_path = "resources/graphics/item_goats_ring.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_effect(ITEM_TYPE, ItemEffect(ITEM_TYPE))
    name = "The Goat's Curse"
    description = ["Curses enemies to take damage over time"]
    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.RING)
    register_item_data(ITEM_TYPE, item_data)
    register_buff_effect(BUFF_TYPE, DebuffedByGoatsRing)
