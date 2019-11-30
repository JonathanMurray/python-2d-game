from typing import List, Tuple, Optional, Dict, Any

import pygame
from pygame.rect import Rect

from pythongame.core.common import ConsumableType, ItemType, HeroId, UiIconSprite, AbilityType, PortraitIconSprite, \
    SoundId
from pythongame.core.game_data import ABILITIES, BUFF_TEXTS, \
    KEYS_BY_ABILITY_TYPE, CONSUMABLES, ITEMS, HEROES
from pythongame.core.game_state import BuffWithDuration, NonPlayerCharacter, PlayerState
from pythongame.core.item_inventory import ItemInventorySlot, ItemEquipmentCategory, ITEM_EQUIPMENT_CATEGORY_NAMES
from pythongame.core.math import is_point_in_rect
from pythongame.core.npc_behaviors import DialogData
from pythongame.core.sound_player import play_sound
from pythongame.core.talents import TalentsGraphics
from pythongame.core.view.render_util import DrawableArea
from pythongame.scenes_game.game_ui_state import GameUiState, ToggleButtonId
from pythongame.scenes_game.ui_components import AbilityIcon, ConsumableIcon, ItemIcon, TooltipGraphics, StatBar, \
    ToggleButton, ControlsWindow, StatsWindow, TalentIcon, TalentsWindow, ExpBar, Portrait, Minimap, Buffs, Text, \
    DialogOption, Dialog, Checkbox, Button, Message, PausedSplashScreen
from pythongame.scenes_game.ui_events import TrySwitchItemInInventory, EventTriggeredFromUi, \
    DragItemBetweenInventorySlots, DropItemOnGround, DragConsumableBetweenInventorySlots, DropConsumableOnGround, \
    PickTalent, StartDraggingItemOrConsumable, SaveGame, ToggleSound

COLOR_WHITE = (250, 250, 250)
COLOR_BLACK = (0, 0, 0)
COLOR_HIGHLIGHTED_ICON = (250, 250, 150)
COLOR_HOVERED_ICON_HIGHLIGHT = (200, 200, 250)
COLOR_HIGHLIGHT_HAS_UNSEEN = (150, 250, 200)
COLOR_BORDER = (139, 69, 19)
COLOR_ITEM_TOOLTIP_HEADER = (250, 250, 150)
UI_ICON_SIZE = (32, 32)
UI_ICON_BIG_SIZE = (36, 36)
PORTRAIT_ICON_SIZE = (100, 70)

DIR_FONTS = './resources/fonts/'


class DialogState:
    def __init__(self):
        self.option_index: int = 0
        self.data: DialogData = None
        self.npc: NonPlayerCharacter = None
        self.active = False


class GameUiView:

    def __init__(self, pygame_screen, camera_size: Tuple[int, int], screen_size: Tuple[int, int],
                 images_by_ui_sprite: Dict[UiIconSprite, Any], big_images_by_ui_sprite: Dict[UiIconSprite, Any],
                 images_by_portrait_sprite: Dict[PortraitIconSprite, Any]):

        # INIT PYGAME FONTS
        pygame.font.init()

        # SETUP FUNDAMENTALS
        self.screen_render = DrawableArea(pygame_screen)
        self.ui_render = DrawableArea(pygame_screen, self._translate_ui_position_to_screen)
        self.ui_screen_area = Rect(0, camera_size[1], screen_size[0], screen_size[1] - camera_size[1])
        self.camera_size = camera_size
        self.screen_size = screen_size

        # FONTS
        self.font_splash_screen = pygame.font.Font(DIR_FONTS + 'Arial Rounded Bold.ttf', 64)
        self.font_ui_stat_bar_numbers = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_ui_money = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_npc_action = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_ui_headers = pygame.font.Font(DIR_FONTS + 'Herculanum.ttf', 18)
        self.font_tooltip_header = pygame.font.Font(DIR_FONTS + 'Herculanum.ttf', 16)
        self.font_tooltip_details = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_stats = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 9)
        self.font_buff_texts = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_message = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 14)
        self.font_debug_info = pygame.font.Font(None, 19)
        self.font_game_world_text = pygame.font.Font(DIR_FONTS + 'Arial Rounded Bold.ttf', 12)
        self.font_game_world_text = pygame.font.Font(None, 19)
        self.font_ui_icon_keys = pygame.font.Font(DIR_FONTS + 'Courier New Bold.ttf', 12)
        self.font_level = pygame.font.Font(DIR_FONTS + 'Courier New Bold.ttf', 11)
        self.font_dialog = pygame.font.Font(DIR_FONTS + 'Merchant Copy.ttf', 24)
        self.font_dialog_option_detail_body = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)

        # IMAGES
        self.images_by_ui_sprite = images_by_ui_sprite
        self.big_images_by_ui_sprite = big_images_by_ui_sprite
        self.images_by_portrait_sprite = images_by_portrait_sprite
        self.images_by_item_category = {
            ItemEquipmentCategory.HEAD: self.images_by_ui_sprite[UiIconSprite.INVENTORY_TEMPLATE_HELMET],
            ItemEquipmentCategory.CHEST: self.images_by_ui_sprite[UiIconSprite.INVENTORY_TEMPLATE_CHEST],
            ItemEquipmentCategory.MAIN_HAND: self.images_by_ui_sprite[UiIconSprite.INVENTORY_TEMPLATE_MAINHAND],
            ItemEquipmentCategory.OFF_HAND: self.images_by_ui_sprite[UiIconSprite.INVENTORY_TEMPLATE_OFFHAND],
            ItemEquipmentCategory.NECK: self.images_by_ui_sprite[UiIconSprite.INVENTORY_TEMPLATE_NECK],
            ItemEquipmentCategory.RING: self.images_by_ui_sprite[UiIconSprite.INVENTORY_TEMPLATE_RING],
        }

        # UI COMPONENTS
        self.ability_icons_row: Rect = Rect(0, 0, 0, 0)
        self.ability_icons: List[AbilityIcon] = []
        self.consumable_icons_row: Rect = Rect(0, 0, 0, 0)
        self.consumable_icons: List[ConsumableIcon] = []
        self.inventory_icons_rect: Rect = Rect(0, 0, 0, 0)
        self.inventory_icons: List[ItemIcon] = []
        self.exp_bar = ExpBar(self.ui_render, Rect(140, 23, 300, 2), self.font_level)
        self.minimap = Minimap(self.ui_render, Rect(440, 52, 80, 80))
        self.buffs = Buffs(self.ui_render, self.font_buff_texts, (10, -35))
        self.money_text = Text(self.ui_render, self.font_ui_money, (24, 150), "NO MONEY")
        self.talents_window: TalentsWindow = None
        self.message = Message(self.screen_render, self.font_message, self.ui_screen_area.w // 2,
                               self.ui_screen_area.y - 30)
        self.paused_splash_screen = PausedSplashScreen(self.screen_render, self.font_splash_screen,
                                                       Rect(0, 0, self.screen_size[0], self.screen_size[1]))

        # SETUP UI COMPONENTS
        self._setup_ability_icons()
        self._setup_consumable_icons()
        self._setup_inventory_icons()
        self._setup_health_and_mana_bars()
        self._setup_stats_window()
        self._setup_talents_window(TalentsGraphics([]))
        self._setup_controls_window()
        self._setup_toggle_buttons()
        self._setup_portrait()
        self._setup_dialog()

        # QUICKLY CHANGING STATE
        self.hovered_component = None
        self.fps_string = ""
        self.enabled_toggle: ToggleButton = None
        self.item_slot_being_dragged: ItemIcon = None
        self.consumable_slot_being_dragged: ConsumableIcon = None
        self.is_mouse_hovering_ui = False
        self.mouse_screen_position = (0, 0)
        self.dialog_state = DialogState()

    def _setup_ability_icons(self):
        x_0 = 140
        y = 112
        icon_space = 2
        icon_rect_padding = 2
        abilities_rect_pos = (x_0 - icon_rect_padding, y - icon_rect_padding)
        max_num_abilities = 5
        self.ability_icons_row = Rect(
            abilities_rect_pos[0], abilities_rect_pos[1],
            (UI_ICON_SIZE[0] + icon_space) * max_num_abilities - icon_space + icon_rect_padding * 2,
            UI_ICON_SIZE[1] + icon_rect_padding * 2)

        self.ability_icons = []
        for i in range(max_num_abilities):
            x = x_0 + i * (UI_ICON_SIZE[0] + icon_space)
            rect = Rect(x, y, UI_ICON_SIZE[0], UI_ICON_SIZE[1])
            icon = AbilityIcon(self.ui_render, rect, None, None, self.font_ui_icon_keys, None, None, 0)
            self.ability_icons.append(icon)

    def _setup_consumable_icons(self):
        x_0 = 140
        y = 52
        icon_space = 2
        icon_rect_padding = 2
        consumables_rect_pos = (x_0 - icon_rect_padding, y - icon_rect_padding)
        max_num_consumables = 5
        self.consumable_icons_row = Rect(
            consumables_rect_pos[0], consumables_rect_pos[1],
            (UI_ICON_SIZE[0] + icon_space) * max_num_consumables - icon_space + icon_rect_padding * 2,
            UI_ICON_SIZE[1] + icon_rect_padding * 2)

        self.consumable_icons = []
        for i in range(max_num_consumables):
            x = x_0 + i * (UI_ICON_SIZE[0] + icon_space)
            rect = Rect(x, y, UI_ICON_SIZE[0], UI_ICON_SIZE[1])
            slot_number = i + 1
            icon = ConsumableIcon(self.ui_render, rect, None, str(slot_number), self.font_ui_icon_keys, None, [],
                                  slot_number)
            self.consumable_icons.append(icon)

    def _setup_inventory_icons(self):
        x_0 = 325
        y_0 = 52
        icon_space = 2
        icon_rect_padding = 2
        items_rect_pos = (x_0 - icon_rect_padding, y_0 - icon_rect_padding)
        num_item_slot_rows = 3
        num_slots_per_row = 3
        self.inventory_icons_rect = Rect(
            items_rect_pos[0], items_rect_pos[1],
            (UI_ICON_SIZE[0] + icon_space) * num_slots_per_row - icon_space + icon_rect_padding * 2,
            num_item_slot_rows * UI_ICON_SIZE[1] + (num_item_slot_rows - 1) * icon_space + icon_rect_padding * 2)
        for i in range(num_item_slot_rows * num_slots_per_row):
            x = x_0 + (i % num_slots_per_row) * (UI_ICON_SIZE[0] + icon_space)
            y = y_0 + (i // num_slots_per_row) * (UI_ICON_SIZE[1] + icon_space)
            rect = Rect(x, y, UI_ICON_SIZE[0], UI_ICON_SIZE[1])
            icon = ItemIcon(self.ui_render, rect, None, None, None, None, i)
            self.inventory_icons.append(icon)

    def _setup_health_and_mana_bars(self):
        rect_healthbar = Rect(20, 111, 100, 14)
        self.healthbar = StatBar(self.ui_render, rect_healthbar, (200, 0, 50), None, 0, 1, border=True,
                                 show_numbers=True, font=self.font_ui_stat_bar_numbers)
        rect_manabar = Rect(20, 132, 100, 14)
        self.manabar = StatBar(self.ui_render, rect_manabar, (50, 0, 200), None, 0, 1, border=True,
                               show_numbers=True, font=self.font_ui_stat_bar_numbers)

    def _setup_toggle_buttons(self):
        x = 545
        y_0 = 30
        w = 140
        h = 20
        font = self.font_tooltip_details
        self.stats_toggle = ToggleButton(self.ui_render, Rect(x, y_0, w, h), font, "STATS    [A]", ToggleButtonId.STATS,
                                         False, self.stats_window)
        self.talents_toggle = ToggleButton(self.ui_render, Rect(x, y_0 + 30, w, h), font, "TALENTS  [T]",
                                           ToggleButtonId.TALENTS, False, self.talents_window)
        self.controls_toggle = ToggleButton(self.ui_render, Rect(x, y_0 + 60, w, h), font, "CONTROLS [C]",
                                            ToggleButtonId.CONTROLS, False, self.controls_window)
        self.toggle_buttons = [self.stats_toggle, self.talents_toggle, self.controls_toggle]
        self.sound_checkbox = Checkbox(self.ui_render, Rect(x, y_0 + 90, 65, h), font, "SOUND", True)
        self.save_button = Button(self.ui_render, Rect(x + 75, y_0 + 90, 65, h), font, "SAVE")

    def _setup_stats_window(self):
        rect = Rect(545, -300, 140, 250)
        self.stats_window = StatsWindow(self.ui_render, rect, self.font_tooltip_details, self.font_stats, None, 0)

    def _setup_talents_window(self, talents: TalentsGraphics):
        rect = Rect(545, -300, 140, 260)
        icon_rows = []
        x_0 = rect[0] + 22
        y_0 = rect[1] + 35
        for i, choice_graphics in enumerate(talents.choice_graphics_items):
            y = y_0 + i * (UI_ICON_SIZE[1] + 30)
            y_icon = y + 3
            choice = choice_graphics.choice

            image_1 = self.images_by_ui_sprite[choice.first.ui_icon_sprite]
            tooltip_1 = TooltipGraphics(self.ui_render, COLOR_WHITE, choice.first.name, [choice.first.description],
                                        bottom_right=(x_0 + UI_ICON_SIZE[0], y_icon))
            icon_1 = TalentIcon(self.ui_render, Rect(x_0, y_icon, UI_ICON_SIZE[0], UI_ICON_SIZE[1]), image_1,
                                tooltip_1, choice_graphics.chosen_index == 0, choice.first.name, self.font_stats,
                                i, 0)

            image_2 = self.images_by_ui_sprite[choice.second.ui_icon_sprite]
            tooltip_2 = TooltipGraphics(self.ui_render, COLOR_WHITE, choice.second.name, [choice.second.description],
                                        bottom_right=(x_0 + UI_ICON_SIZE[0] + 60, y_icon))
            icon_2 = TalentIcon(self.ui_render, Rect(x_0 + 60, y_icon, UI_ICON_SIZE[0], UI_ICON_SIZE[1]), image_2,
                                tooltip_2, choice_graphics.chosen_index == 1, choice.second.name, self.font_stats,
                                i, 1)

            icon_rows.append((icon_1, icon_2))
        if self.talents_window is None:
            self.talents_window = TalentsWindow(
                self.ui_render, rect, self.font_tooltip_details, self.font_stats, talents, icon_rows)
        else:
            self.talents_window.update(rect, talents, icon_rows)

    def _setup_controls_window(self):
        rect = Rect(545, -300, 140, 170)
        self.controls_window = ControlsWindow(self.ui_render, rect, self.font_tooltip_details, self.font_stats)

    def _setup_portrait(self):
        rect = Rect(20, 18, PORTRAIT_ICON_SIZE[0], PORTRAIT_ICON_SIZE[1])
        self.portrait = Portrait(self.ui_render, rect, None)

    def _setup_dialog(self):
        self.dialog = Dialog(self.screen_render, None, None, [], 0, PORTRAIT_ICON_SIZE, UI_ICON_SIZE)

    # --------------------------------------------------------------------------------------------------------
    #                                     HANDLE USER INPUT
    # --------------------------------------------------------------------------------------------------------

    def handle_mouse_movement(self, mouse_screen_pos: Tuple[int, int]):
        self.mouse_screen_position = mouse_screen_pos
        self.is_mouse_hovering_ui = is_point_in_rect(mouse_screen_pos, self.ui_screen_area)

        mouse_ui_position = self._translate_screen_position_to_ui(mouse_screen_pos)

        simple_components = [self.healthbar, self.manabar, self.sound_checkbox, self.save_button] + \
                            self.ability_icons + self.toggle_buttons

        for component in simple_components:
            if component.contains(mouse_ui_position):
                self._on_hover_component(component)
                return
        # TODO Unify hover handling for consumables/items
        for icon in self.consumable_icons + self.inventory_icons:
            collision_offset = icon.get_collision_offset(mouse_ui_position)
            if collision_offset:
                self._on_hover_component(icon)
                return

        # TODO Unify hover handling of window icons
        if self.talents_window.shown:
            hovered_icon = self.talents_window.get_icon_containing(mouse_ui_position)
            if hovered_icon:
                self._on_hover_component(hovered_icon)
                return

        # If something was hovered, we would have returned from the method
        self._set_currently_hovered_component_not_hovered()

    def _on_hover_component(self, component):
        self._set_currently_hovered_component_not_hovered()
        self.hovered_component = component
        self.hovered_component.hovered = True

    def _set_currently_hovered_component_not_hovered(self):
        if self.hovered_component is not None:
            self.hovered_component.hovered = False
            self.hovered_component = None

    def handle_mouse_click(self) -> List[EventTriggeredFromUi]:
        if self.hovered_component in self.toggle_buttons:
            self._on_click_toggle(self.hovered_component)
        elif self.hovered_component == self.sound_checkbox:
            self.sound_checkbox.on_click()
            return [ToggleSound()]
        elif self.hovered_component == self.save_button:
            return [SaveGame()]
        elif self.hovered_component in self.inventory_icons and self.hovered_component.item_type:
            self.item_slot_being_dragged = self.hovered_component
            return [StartDraggingItemOrConsumable()]
        elif self.hovered_component in self.consumable_icons and self.hovered_component.consumable_types:
            self.consumable_slot_being_dragged = self.hovered_component
            return [StartDraggingItemOrConsumable()]
        elif self.hovered_component in self.talents_window.get_last_row_icons():
            return [PickTalent(self.hovered_component.option_index)]
        return []

    def handle_mouse_right_click(self) -> List[EventTriggeredFromUi]:
        if self.hovered_component in self.inventory_icons:
            self.item_slot_being_dragged = None
            item_icon: ItemIcon = self.hovered_component
            return [TrySwitchItemInInventory(item_icon.inventory_slot_index)]
        return []

    def handle_mouse_release(self) -> List[EventTriggeredFromUi]:
        triggered_events = []
        if self.item_slot_being_dragged:
            if self.hovered_component in self.inventory_icons and self.hovered_component != self.item_slot_being_dragged:
                item_icon: ItemIcon = self.hovered_component
                event = DragItemBetweenInventorySlots(self.item_slot_being_dragged.inventory_slot_index,
                                                      item_icon.inventory_slot_index)
                triggered_events.append(event)
            if not self.is_mouse_hovering_ui:
                event = DropItemOnGround(self.item_slot_being_dragged.inventory_slot_index, self.mouse_screen_position)
                triggered_events.append(event)
            self.item_slot_being_dragged = None

        if self.consumable_slot_being_dragged:
            if self.hovered_component in self.consumable_icons and self.hovered_component != self.consumable_slot_being_dragged:
                consumable_icon: ConsumableIcon = self.hovered_component
                event = DragConsumableBetweenInventorySlots(self.consumable_slot_being_dragged.slot_number,
                                                            consumable_icon.slot_number)
                triggered_events.append(event)
            if not self.is_mouse_hovering_ui:
                event = DropConsumableOnGround(self.consumable_slot_being_dragged.slot_number,
                                               self.mouse_screen_position)
                triggered_events.append(event)
            self.consumable_slot_being_dragged = None

        return triggered_events

    # --------------------------------------------------------------------------------------------------------
    #                              HANDLE TOGGLE BUTTON USER INTERACTIONS
    # --------------------------------------------------------------------------------------------------------

    def handle_space_click(self) -> Optional[Tuple[NonPlayerCharacter, int]]:
        if self.dialog_state.active:
            self.dialog_state.active = False
            self._update_dialog_graphics()
            return self.dialog_state.npc, self.dialog_state.option_index
        return None

    def click_toggle_button(self, ui_toggle: ToggleButtonId):
        toggle = [tb for tb in self.toggle_buttons if tb.toggle_id == ui_toggle][0]
        self._on_click_toggle(toggle)

    def _on_click_toggle(self, clicked_toggle: ToggleButton):
        play_sound(SoundId.UI_TOGGLE)
        if clicked_toggle.is_open:
            self.enabled_toggle.close()
            self.enabled_toggle = None
        else:
            if self.enabled_toggle is not None:
                self.enabled_toggle.close()
            self.enabled_toggle = clicked_toggle
            self.enabled_toggle.open()

    # --------------------------------------------------------------------------------------------------------
    #                              REACT TO OBSERVABLE EVENTS
    # --------------------------------------------------------------------------------------------------------

    def close_talent_window(self):
        if self.enabled_toggle == self.talents_toggle:
            self.enabled_toggle.close()
            self.enabled_toggle = None

    def on_talents_updated(self, talent_graphics: TalentsGraphics):
        self._setup_talents_window(talent_graphics)

    def on_talent_was_unlocked(self, _event):
        if self.enabled_toggle != self.talents_toggle:
            self.talents_toggle.highlighted = True

    def on_player_movement_speed_updated(self, speed_multiplier: float):
        self.stats_window.player_speed_multiplier = speed_multiplier

    def on_player_exp_updated(self, event: Tuple[int, float]):
        level, ratio_exp_until_next_level = event
        self.exp_bar.update(level, ratio_exp_until_next_level)

    def on_money_updated(self, money: int):
        self.money_text.text = "Money: " + str(money)

    def on_cooldowns_updated(self, ability_cooldowns_remaining: Dict[AbilityType, int]):
        for icon in self.ability_icons:
            ability_type = icon.ability_type
            if ability_type:
                ability = ABILITIES[ability_type]
                icon.cooldown_remaining_ratio = ability_cooldowns_remaining[ability_type] / ability.cooldown

    def on_health_updated(self, health: Tuple[int, int]):
        value, max_value = health
        self.healthbar.update(value, max_value)

    def on_mana_updated(self, mana: Tuple[int, int]):
        value, max_value = mana
        self.manabar.update(value, max_value)

    def on_buffs_updated(self, active_buffs: List[BuffWithDuration]):
        buffs = []
        for active_buff in active_buffs:
            buff_type = active_buff.buff_effect.get_buff_type()
            # Buffs that don't have description texts shouldn't be displayed. (They are typically irrelevant to the
            # player)
            if buff_type in BUFF_TEXTS:
                text = BUFF_TEXTS[buff_type]
                ratio_remaining = active_buff.get_ratio_duration_remaining()
                buffs.append((text, ratio_remaining))
        self.buffs.update(buffs)

    def on_player_stats_updated(self, player_state: PlayerState):
        self.stats_window.player_state = player_state
        health_regen = player_state.health_resource.get_effective_regen()
        mana_regen = player_state.mana_resource.get_effective_regen()

        tooltip_details = [
            "regeneration: " + "{:.1f}".format(health_regen) + "/s"]
        health_tooltip = TooltipGraphics(self.ui_render, COLOR_WHITE, "Health", tooltip_details,
                                         bottom_left=self.healthbar.rect.topleft)
        self.healthbar.tooltip = health_tooltip
        tooltip_details = [
            "regeneration: " + "{:.1f}".format(mana_regen) + "/s"]
        mana_tooltip = TooltipGraphics(self.ui_render, COLOR_WHITE, "Mana", tooltip_details,
                                       bottom_left=self.manabar.rect.topleft)
        self.manabar.tooltip = mana_tooltip

    def on_abilities_updated(self, abilities: List[AbilityType]):
        for i, ability_type in enumerate(abilities):
            ability = ABILITIES[ability_type]
            icon = self.ability_icons[i]
            icon.update(
                image=self.images_by_ui_sprite[ability.icon_sprite],
                label=KEYS_BY_ABILITY_TYPE[ability_type].key_string,
                ability=ability,
                ability_type=ability_type)

    def on_consumables_updated(self, consumable_slots: Dict[int, List[ConsumableType]]):
        for i, slot_number in enumerate(consumable_slots):
            icon = self.consumable_icons[i]
            consumable_types = consumable_slots[slot_number]
            image = None
            consumable = None
            if consumable_types:
                consumable = CONSUMABLES[consumable_types[0]]
                image = self.images_by_ui_sprite[consumable.icon_sprite]

            icon.update(image, consumable, consumable_types)

    def on_inventory_updated(self, item_slots: List[ItemInventorySlot]):
        for i in range(len(item_slots)):
            icon = self.inventory_icons[i]
            slot = item_slots[i]
            item_type = slot.get_item_type() if not slot.is_empty() else None
            slot_equipment_category = slot.enforced_equipment_category
            image = None
            tooltip = None
            if item_type:
                item = ITEMS[item_type]
                image = self.images_by_ui_sprite[item.icon_sprite]
                tooltip_details = []
                if item.item_equipment_category:
                    category_name = ITEM_EQUIPMENT_CATEGORY_NAMES[item.item_equipment_category]
                    tooltip_details.append("[" + category_name + "]")
                tooltip_details += item.description_lines
                tooltip = TooltipGraphics(self.ui_render, COLOR_ITEM_TOOLTIP_HEADER, item.name, tooltip_details,
                                          bottom_left=icon.rect.topleft)
            elif slot_equipment_category:
                image = self.images_by_item_category[slot_equipment_category]
                category_name = ITEM_EQUIPMENT_CATEGORY_NAMES[slot_equipment_category]
                tooltip_details = ["[" + category_name + "]",
                                   "You have nothing equipped. Drag an item here to equip it!"]
                tooltip = TooltipGraphics(self.ui_render, COLOR_WHITE, "...", tooltip_details,
                                          bottom_left=icon.rect.topleft)

            icon.image = image
            icon.tooltip = tooltip
            icon.slot_equipment_category = slot_equipment_category
            icon.item_type = item_type

    # --------------------------------------------------------------------------------------------------------
    #                              HANDLE DIALOG USER INTERACTIONS
    # --------------------------------------------------------------------------------------------------------

    def update_hero(self, hero_id: HeroId):
        sprite = HEROES[hero_id].portrait_icon_sprite
        image = self.images_by_portrait_sprite[sprite]
        self.portrait.image = image

    def start_dialog_with_npc(self, npc: NonPlayerCharacter, dialog_data: DialogData):
        self.dialog_state.active = True
        self.dialog_state.npc = npc
        self.dialog_state.data = dialog_data
        if self.dialog_state.option_index >= len(dialog_data.options):
            self.dialog_state.option_index = 0
        self._update_dialog_graphics()

    def change_dialog_option(self, delta: int):
        self.dialog_state.option_index = (self.dialog_state.option_index + delta) % len(self.dialog_state.data.options)
        self._update_dialog_graphics()

    def _update_dialog_graphics(self):
        if self.dialog_state.active:

            build_dialog_option = lambda option: DialogOption(
                option.summary, option.action_text,
                self.images_by_ui_sprite[option.ui_icon_sprite] if option.ui_icon_sprite else None,
                option.detail_header, option.detail_body)

            data = self.dialog_state.data
            self.dialog.portrait_image = self.images_by_portrait_sprite[data.portrait_icon_sprite]
            self.dialog.text_body = data.text_body
            self.dialog.options = [build_dialog_option(option) for option in data.options]
            self.dialog.active_option_index = self.dialog_state.option_index
            self.dialog.shown = True
        else:
            self.dialog.shown = False

    def has_open_dialog(self) -> bool:
        return self.dialog_state.active

    # --------------------------------------------------------------------------------------------------------
    #                                          RENDERING
    # --------------------------------------------------------------------------------------------------------

    def set_paused(self, paused: bool):
        self.paused_splash_screen.shown = paused

    def update_fps_string(self, fps_string: str):
        self.fps_string = fps_string

    def _translate_ui_position_to_screen(self, position):
        return position[0] + self.ui_screen_area.x, position[1] + self.ui_screen_area.y

    def _translate_screen_position_to_ui(self, position: Tuple[int, int]):
        return position[0] - self.ui_screen_area.x, position[1] - self.ui_screen_area.y

    def _render_item_being_dragged(self, item_type: ItemType, mouse_screen_position: Tuple[int, int],
                                   relative_mouse_pos: Tuple[int, int]):
        ui_icon_sprite = ITEMS[item_type].icon_sprite
        big_image = self.big_images_by_ui_sprite[ui_icon_sprite]
        self._render_dragged(big_image, mouse_screen_position, relative_mouse_pos)

    def _render_consumable_being_dragged(self, consumable_type: ConsumableType, mouse_screen_position: Tuple[int, int],
                                         relative_mouse_pos: Tuple[int, int]):
        ui_icon_sprite = CONSUMABLES[consumable_type].icon_sprite
        big_image = self.big_images_by_ui_sprite[ui_icon_sprite]
        self._render_dragged(big_image, mouse_screen_position, relative_mouse_pos)

    def _render_dragged(self, big_image, mouse_screen_position, relative_mouse_pos):
        position = (mouse_screen_position[0] - relative_mouse_pos[0] - (UI_ICON_BIG_SIZE[0] - UI_ICON_SIZE[0]) // 2,
                    mouse_screen_position[1] - relative_mouse_pos[1] - (UI_ICON_BIG_SIZE[1] - UI_ICON_SIZE[1]) // 2)
        self.screen_render.image(big_image, position)

    def render(self, ui_state: GameUiState):

        self.screen_render.rect(COLOR_BORDER, Rect(0, 0, self.camera_size[0], self.camera_size[1]), 1)
        self.screen_render.rect_filled((20, 10, 0), Rect(0, self.camera_size[1], self.screen_size[0],
                                                         self.screen_size[1] - self.camera_size[1]))

        # CONSUMABLES
        self.ui_render.rect_filled((60, 60, 80), self.consumable_icons_row)
        for icon in self.consumable_icons:
            # TODO treat this as state and update it elsewhere
            recently_clicked = icon.slot_number == ui_state.highlighted_consumable_action
            icon.render(recently_clicked)

        # ABILITIES
        self.ui_render.rect_filled((60, 60, 80), self.ability_icons_row)
        for icon in self.ability_icons:
            ability_type = icon.ability_type
            # TODO treat this as state and update it elsewhere
            if ability_type:
                recently_clicked = ability_type == ui_state.highlighted_ability_action
                icon.render(recently_clicked)

        # ITEMS
        self.ui_render.rect_filled((60, 60, 80), self.inventory_icons_rect)
        for icon in self.inventory_icons:
            # TODO treat this as state and update it elsewhere
            highlighted = self.item_slot_being_dragged and self.item_slot_being_dragged.item_type \
                          and ITEMS[self.item_slot_being_dragged.item_type].item_equipment_category \
                          and icon.slot_equipment_category == ITEMS[
                              self.item_slot_being_dragged.item_type].item_equipment_category
            icon.render(highlighted)

        # MINIMAP
        self.minimap.render(ui_state.player_minimap_relative_position)

        simple_components = [self.exp_bar, self.portrait, self.healthbar, self.manabar, self.money_text, self.dialog,
                             self.buffs, self.sound_checkbox, self.save_button, self.stats_window, self.talents_window,
                             self.controls_window] + self.toggle_buttons

        for component in simple_components:
            component.render()

        self.screen_render.rect(COLOR_BORDER, self.ui_screen_area, 1)

        self.screen_render.rect_transparent(Rect(0, 0, 70, 20), 100, COLOR_BLACK)
        self.screen_render.text(self.font_debug_info, "fps: " + self.fps_string, (5, 3))

        self.message.render(ui_state.message)

        if self.hovered_component and self.hovered_component.tooltip and not self.item_slot_being_dragged \
                and not self.consumable_slot_being_dragged:
            tooltip: TooltipGraphics = self.hovered_component.tooltip
            tooltip.render()

        # TODO Bring back relative render position for dragged entities
        if self.item_slot_being_dragged:
            self._render_item_being_dragged(self.item_slot_being_dragged.item_type, self.mouse_screen_position,
                                            (UI_ICON_SIZE[0] // 2, (UI_ICON_SIZE[1] // 2)))
        elif self.consumable_slot_being_dragged:
            self._render_consumable_being_dragged(self.consumable_slot_being_dragged.consumable_types[0],
                                                  self.mouse_screen_position,
                                                  (UI_ICON_SIZE[0] // 2, (UI_ICON_SIZE[1] // 2)))

        self.paused_splash_screen.render()
