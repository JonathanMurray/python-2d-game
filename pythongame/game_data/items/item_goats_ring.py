import random

from pythongame.core.buff_effects import get_buff_effect, register_buff_effect, AbstractBuffEffect
from pythongame.core.common import ItemType, Sprite, BuffType, Millis, PeriodicTimer
from pythongame.core.damage_interactions import deal_player_damage_to_enemy, DamageType
from pythongame.core.game_data import UiIconSprite
from pythongame.core.game_state import Event, PlayerDamagedEnemy, GameState, NonPlayerCharacter
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.visual_effects import VisualCircle
from pythongame.core.world_entity import WorldEntity
from pythongame.game_data.items.register_items_util import register_custom_effect_item

DMG_COOLDOWN = Millis(1000)
TICK_DMG = 1
DURATION = Millis(6000)
TOTAL_DAMAGE = DURATION / DMG_COOLDOWN * TICK_DMG

ITEM_TYPE = ItemType.GOATS_RING
BUFF_TYPE = BuffType.DEBUFFED_BY_GOATS_RING
DAMAGE_SOURCE = "goats_ring"


class ItemEffect(AbstractItemEffect):

    def __init__(self, proc_chance: float):
        self._proc_chance = proc_chance

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerDamagedEnemy):
            if random.random() < self._proc_chance:
                # Compare "source" to prevent the debuff from renewing itself indefinitely
                if event.damage_source != DAMAGE_SOURCE:
                    event.enemy_npc.gain_buff_effect(get_buff_effect(BUFF_TYPE), DURATION)


class DebuffedByGoatsRing(AbstractBuffEffect):

    def __init__(self):
        self.dmg_timer = PeriodicTimer(DMG_COOLDOWN)
        self.graphics_timer = PeriodicTimer(Millis(400))

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.dmg_timer.update_and_check_if_ready(time_passed):
            deal_player_damage_to_enemy(game_state, buffed_npc, TICK_DMG, DamageType.MAGIC, damage_source=DAMAGE_SOURCE)
        if self.graphics_timer.update_and_check_if_ready(time_passed):
            position = buffed_entity.get_center_position()
            visual_effect1 = VisualCircle((0, 100, 40), position, 9, 16, Millis(400), 2, buffed_entity)
            visual_effect2 = VisualCircle((0, 180, 90), position, 9, 16, Millis(500), 2, buffed_entity)
            game_state.game_world.visual_effects.append(visual_effect1)
            game_state.game_world.visual_effects.append(visual_effect2)

    def get_buff_type(self):
        return BUFF_TYPE


def register_goats_ring():
    item_type = ItemType.GOATS_RING
    proc_chance = 0.2
    register_custom_effect_item(
        item_type=item_type,
        item_level=5,
        ui_icon_sprite=UiIconSprite.ITEM_GOATS_RING,
        sprite=Sprite.ITEM_GOATS_RING,
        image_file_path="resources/graphics/item_goats_ring.png",
        item_equipment_category=ItemEquipmentCategory.RING,
        name="The Goat's Curse",
        custom_effect=ItemEffect(proc_chance),
        stat_modifier_intervals=[],
        custom_description=["Whenever you damage an enemy, there is a  " +
                            str(int(proc_chance * 100)) + "% chance that it will be cursed and take " +
                            str(TOTAL_DAMAGE) + " magic damage over " + "{:.0f}".format(DURATION / 1000) + "s"],
        is_unique=True
    )
    register_buff_effect(BUFF_TYPE, DebuffedByGoatsRing)
