from typing import List, Tuple, Optional, Dict, Any

import pygame
from pygame.rect import Rect

from pythongame.core.abilities import ABILITIES
from pythongame.core.common import ConsumableType, HeroId, UiIconSprite, AbilityType, PortraitIconSprite, \
    SoundId, NpcType, Millis, DialogData, ItemId
from pythongame.core.game_data import BUFF_TEXTS, CONSUMABLES, HEROES
from pythongame.core.game_state import BuffWithDuration, NonPlayerCharacter, PlayerState
from pythongame.core.item_data import create_item_description
from pythongame.core.item_data import get_item_data_by_type, get_item_data
from pythongame.core.item_inventory import ItemInventorySlot, ItemEquipmentCategory, ITEM_EQUIPMENT_CATEGORY_NAMES
from pythongame.core.math import is_point_in_rect
from pythongame.core.quests import Quest
from pythongame.core.sound_player import play_sound
from pythongame.core.talents import TalentsState, TalentsConfig
from pythongame.core.view.render_util import DrawableArea
from pythongame.scenes.scenes_game.ui_components import AbilityIcon, ConsumableIcon, ItemIcon, TooltipGraphics, StatBar, \
    ToggleButton, ControlsWindow, StatsWindow, TalentsWindow, ExpBar, Portrait, Minimap, Buffs, Text, \
    DialogOption, Dialog, Checkbox, Button, Message, PausedSplashScreen, TalentTierData, TalentOptionData, TalentIcon, \
    ToggleButtonId, QuestsWindow, DetailLine
from pythongame.scenes.scenes_game.ui_events import TrySwitchItemInInventory, EventTriggeredFromUi, \
    DragItemBetweenInventorySlots, DropItemOnGround, DragConsumableBetweenInventorySlots, DropConsumableOnGround, \
    PickTalent, StartDraggingItemOrConsumable, SaveGame, ToggleSound, ToggleFullscreen, ToggleWindow

COLOR_WHITE = (250, 250, 250)
COLOR_BLACK = (0, 0, 0)
COLOR_BORDER = COLOR_WHITE
UI_ICON_SIZE = (32, 32)
UI_ICON_BIG_SIZE = (36, 36)
PORTRAIT_ICON_SIZE = (100, 70)

DIR_FONTS = './resources/fonts/'

HIGHLIGHT_CONSUMABLE_ACTION_DURATION = 120
HIGHLIGHT_ABILITY_ACTION_DURATION = 120


class DialogState:
    def __init__(self):
        self.option_index: int = 0
        self.data: DialogData = None
        self.npc: NonPlayerCharacter = None
        self.active = False


class InfoMessage:
    def __init__(self):
        self._ticks_since_message_updated = 0

        self.message = ""
        self._enqueued_messages = []

    def set_message(self, message: str):
        self.message = message
        self._ticks_since_message_updated = 0

    def enqueue_message(self, message: str):
        self._enqueued_messages.append(message)

    def clear_messages(self):
        self.message = None
        self._enqueued_messages.clear()

    def notify_time_passed(self, time_passed: Millis):
        self._ticks_since_message_updated += time_passed
        if self.message != "" and self._ticks_since_message_updated > 3500:
            if self._enqueued_messages:
                new_message = self._enqueued_messages.pop(0)
                self.set_message(new_message)
            else:
                self.message = ""


class GameUiView:

    def __init__(self, pygame_screen, camera_size: Tuple[int, int], screen_size: Tuple[int, int],
                 images_by_ui_sprite: Dict[UiIconSprite, Any], big_images_by_ui_sprite: Dict[UiIconSprite, Any],
                 images_by_portrait_sprite: Dict[PortraitIconSprite, Any], ability_key_labels: List[str]):

        # INIT PYGAME FONTS
        pygame.font.init()

        # SETUP FUNDAMENTALS
        self.screen_render = DrawableArea(pygame_screen)
        self.ui_render = DrawableArea(pygame_screen, self._translate_ui_position_to_screen)
        self.ui_screen_area = Rect(0, camera_size[1], screen_size[0], screen_size[1] - camera_size[1])
        self.camera_size = camera_size
        self.screen_size = screen_size
        self.ability_key_labels = ability_key_labels

        # FONTS
        self.font_splash_screen = pygame.font.Font(DIR_FONTS + 'Arial Rounded Bold.ttf', 64)
        self.font_ui_stat_bar_numbers = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_ui_money = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_tooltip_details = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_buttons = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_stats = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 9)
        self.font_buff_texts = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_message = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 14)
        self.font_debug_info = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_ui_icon_keys = pygame.font.Font(DIR_FONTS + 'Courier New Bold.ttf', 12)
        self.font_level = pygame.font.Font(DIR_FONTS + 'Courier New Bold.ttf', 11)

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
        self.exp_bar = ExpBar(self.ui_render, Rect(135, 8, 300, 2), self.font_level)
        self.minimap = Minimap(self.ui_render, Rect(475, 52, 80, 80), Rect(0, 0, 1, 1), (0, 0))
        self.buffs = Buffs(self.ui_render, self.font_buff_texts, (10, -35))
        self.money_text = Text(self.ui_render, self.font_ui_money, (24, 150), "NO MONEY")
        self.talents_window: TalentsWindow = None
        self.quests_window: QuestsWindow = None
        self.message = Message(self.screen_render, self.font_message, self.ui_screen_area.w // 2,
                               self.ui_screen_area.y - 30)
        self.paused_splash_screen = PausedSplashScreen(self.screen_render, self.font_splash_screen,
                                                       Rect(0, 0, self.screen_size[0], self.screen_size[1]))
        self.controls_window = ControlsWindow(self.ui_render, self.font_tooltip_details, self.font_stats)

        # SETUP UI COMPONENTS
        self._setup_ability_icons()
        self._setup_consumable_icons()
        self._setup_inventory_icons()
        self._setup_health_and_mana_bars()
        self._setup_stats_window()
        self._setup_talents_window(TalentsState(TalentsConfig({})))
        self._setup_quests_window()
        self._setup_toggle_buttons()
        self._setup_portrait()
        self._setup_dialog()

        # QUICKLY CHANGING STATE
        self.hovered_component = None
        self.fps_string = ""
        self.game_mode_string = ""
        self.enabled_toggle: ToggleButton = None
        self.item_slot_being_dragged: ItemIcon = None
        self.consumable_slot_being_dragged: ConsumableIcon = None
        self.is_mouse_hovering_ui = False
        self.mouse_screen_position = (0, 0)
        self.dialog_state = DialogState()

        self._ticks_since_last_consumable_action = 0
        self._ticks_since_last_ability_action = 0
        self.highlighted_consumable_action: Optional[int] = None
        self.highlighted_ability_action: Optional[AbilityType] = None
        self.manually_highlighted_inventory_item: Optional[ItemId] = None  # used for dialog

        self.info_message = InfoMessage()

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
        y_0 = 24
        icon_space = 2
        icon_rect_padding = 2
        items_rect_pos = (x_0 - icon_rect_padding, y_0 - icon_rect_padding)
        num_item_slot_rows = 4
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
        self.healthbar = StatBar(self.ui_render, rect_healthbar, (200, 0, 50), None, 0, 1,
                                 show_numbers=True, font=self.font_ui_stat_bar_numbers)
        rect_manabar = Rect(20, 132, 100, 14)
        self.manabar = StatBar(self.ui_render, rect_manabar, (50, 0, 200), None, 0, 1,
                               show_numbers=True, font=self.font_ui_stat_bar_numbers)

    def _setup_toggle_buttons(self):
        x = 600
        y_0 = 12
        w = 150
        h = 20
        font = self.font_buttons
        self.stats_toggle = ToggleButton(self.ui_render, Rect(x, y_0, w, h), font, "STATS    [A]", ToggleButtonId.STATS,
                                         False, self.stats_window)
        self.talents_toggle = ToggleButton(self.ui_render, Rect(x, y_0 + 25, w, h), font, "TALENTS  [N]",
                                           ToggleButtonId.TALENTS, False, self.talents_window)
        # TODO Add hotkey, and handle that user input in this module
        self.quests_toggle = ToggleButton(self.ui_render, Rect(x, y_0 + 50, w, h), font, "QUESTS   [B]",
                                          ToggleButtonId.QUESTS, False, self.quests_window)

        self.controls_toggle = ToggleButton(self.ui_render, Rect(x, y_0 + 75, w, h), font, "HELP     [H]",
                                            ToggleButtonId.HELP, False, self.controls_window)
        self.toggle_buttons = [self.stats_toggle, self.talents_toggle, self.quests_toggle, self.controls_toggle]
        self.sound_checkbox = Checkbox(self.ui_render, Rect(x, y_0 + 100, 70, h), "SOUND", True,
                                       lambda _: ToggleSound())
        self.save_button = Button(self.ui_render, Rect(x + 80, y_0 + 100, 70, h), "SAVE [S]", lambda: SaveGame())
        self.fullscreen_checkbox = Checkbox(self.ui_render, Rect(x, y_0 + 125, w, h), "FULLSCREEN",
                                            True, lambda _: ToggleFullscreen())

    def _setup_stats_window(self):
        self.stats_window = StatsWindow(self.ui_render, self.font_tooltip_details, self.font_stats, None, 0, None, 1)

    def _setup_quests_window(self):
        self.quests_window = QuestsWindow(self.ui_render, self.font_tooltip_details, self.font_stats)

    def _setup_talents_window(self, talents: TalentsState):
        talent_tiers: List[TalentTierData] = []
        option_data_from_config = lambda config: TalentOptionData(
            config.name, config.description, self.images_by_ui_sprite[config.ui_icon_sprite])
        for tier_state in talents.tiers:
            options = [option_data_from_config(config) for config in tier_state.options]
            tier_data = TalentTierData(tier_state.status, tier_state.required_level, tier_state.picked_index, options)
            talent_tiers.append(tier_data)
        if self.talents_window is None:
            self.talents_window = TalentsWindow(
                self.ui_render, self.font_tooltip_details, self.font_stats, talent_tiers)
        else:
            self.talents_window.update(talent_tiers)

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
        self._check_for_hovered_components()

    def handle_mouse_movement_in_dialog(self, mouse_screen_pos: Tuple[int, int]):
        self.mouse_screen_position = mouse_screen_pos
        self.is_mouse_hovering_ui = is_point_in_rect(mouse_screen_pos, self.ui_screen_area)
        self.dialog.handle_mouse_movement(mouse_screen_pos)

    def handle_mouse_click_in_dialog(self) -> Optional[Tuple[NpcType, int, int]]:
        clicked_option_index = self.dialog.get_hovered_option_index()
        if clicked_option_index is not None:
            previous_index = self.dialog_state.option_index
            self.dialog_state.option_index = clicked_option_index
            self._update_dialog_graphics()
            return self.dialog_state.npc.npc_type, previous_index, clicked_option_index

    def _check_for_hovered_components(self):
        mouse_ui_position = self._translate_screen_position_to_ui(self.mouse_screen_position)

        # noinspection PyTypeChecker
        simple_components = [self.healthbar, self.manabar, self.sound_checkbox, self.save_button,
                             self.fullscreen_checkbox] + self.ability_icons + self.toggle_buttons

        for component in simple_components:
            if component.contains(mouse_ui_position):
                self._on_hover_component(component)
                return
        # TODO Unify hover handling for consumables/items
        # noinspection PyTypeChecker
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
        elif self.hovered_component in [self.save_button, self.fullscreen_checkbox, self.sound_checkbox]:
            return [self.hovered_component.on_click()]
        elif self.hovered_component in self.inventory_icons and self.hovered_component.item_id:
            self.item_slot_being_dragged = self.hovered_component
            return [StartDraggingItemOrConsumable()]
        elif self.hovered_component in self.consumable_icons and self.hovered_component.consumable_types:
            self.consumable_slot_being_dragged = self.hovered_component
            return [StartDraggingItemOrConsumable()]
        elif self.hovered_component in self.talents_window.get_pickable_talent_icons():
            talent_icon: TalentIcon = self.hovered_component
            return [PickTalent(talent_icon.tier_index, talent_icon.option_index)]
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

    def handle_space_click(self) -> Optional[Tuple[NonPlayerCharacter, int]]:
        if self.dialog_state.active:
            self.dialog_state.active = False
            self._update_dialog_graphics()
            return self.dialog_state.npc, self.dialog_state.option_index
        return None

    def handle_key_press(self, key) -> List[EventTriggeredFromUi]:
        if key == pygame.K_s:
            return [SaveGame()]
        elif key == pygame.K_n:
            self._click_toggle_button(ToggleButtonId.TALENTS)
            return [ToggleWindow()]
        elif key == pygame.K_a:
            self._click_toggle_button(ToggleButtonId.STATS)
            return [ToggleWindow()]
        elif key == pygame.K_h:
            self._click_toggle_button(ToggleButtonId.HELP)
            return [ToggleWindow()]
        elif key == pygame.K_b:
            self._click_toggle_button(ToggleButtonId.QUESTS)
            return [ToggleWindow()]
        return []

    # --------------------------------------------------------------------------------------------------------
    #                              HANDLE TOGGLE BUTTON USER INTERACTIONS
    # --------------------------------------------------------------------------------------------------------

    def _click_toggle_button(self, ui_toggle: ToggleButtonId):
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
        self._check_for_hovered_components()

    def close_talent_window(self):
        if self.enabled_toggle == self.talents_toggle:
            self.enabled_toggle.close()
            self.enabled_toggle = None
            self._check_for_hovered_components()

    # --------------------------------------------------------------------------------------------------------
    #                              REACT TO OBSERVABLE EVENTS
    # --------------------------------------------------------------------------------------------------------

    def on_talents_updated(self, talents_state: TalentsState):
        self._setup_talents_window(talents_state)
        if talents_state.has_unpicked_talents() and not self.talents_toggle.is_open:
            self.talents_toggle.highlighted = True

    def on_talent_was_unlocked(self, _event):
        if self.enabled_toggle != self.talents_toggle:
            self.talents_toggle.highlighted = True

    def on_ability_was_clicked(self, ability_type: AbilityType):
        self.highlighted_ability_action = ability_type
        self._ticks_since_last_ability_action = 0

    def on_consumable_was_clicked(self, slot_number: int):
        self.highlighted_consumable_action = slot_number
        self._ticks_since_last_consumable_action = 0

    def on_player_movement_speed_updated(self, speed_multiplier: float):
        self.stats_window.player_speed_multiplier = speed_multiplier

    def on_player_exp_updated(self, event: Tuple[int, float]):
        level, ratio_exp_until_next_level = event
        self.exp_bar.update(level, ratio_exp_until_next_level)
        self.stats_window.level = level

    def on_player_quests_updated(self, event: Tuple[List[Quest], List[Quest]]):
        active_quests, completed_quests = event
        self.quests_window.active_quests = list(active_quests)
        self.quests_window.completed_quests = list(completed_quests)

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
            DetailLine("regeneration: " + "{:.1f}".format(health_regen) + "/s")]
        health_tooltip = TooltipGraphics(self.ui_render, COLOR_WHITE, "Health", tooltip_details,
                                         bottom_left=(self.healthbar.rect.left - 2, self.healthbar.rect.top - 1))
        self.healthbar.tooltip = health_tooltip
        tooltip_details = [
            DetailLine("regeneration: " + "{:.1f}".format(mana_regen) + "/s")]
        mana_tooltip = TooltipGraphics(self.ui_render, COLOR_WHITE, "Mana", tooltip_details,
                                       bottom_left=(self.manabar.rect.left - 2, self.manabar.rect.top - 1))
        self.manabar.tooltip = mana_tooltip

    def on_abilities_updated(self, abilities_by_key_string: Dict[str, AbilityType]):
        for i, icon in enumerate(self.ability_icons):
            key_string = self.ability_key_labels[i]
            ability_type = abilities_by_key_string.get(key_string, None)
            ability = ABILITIES[ability_type] if ability_type else None
            image = self.images_by_ui_sprite[ability.icon_sprite] if ability else None
            icon.update(
                image=image,
                label=key_string,
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
            item_id = slot.get_item_id() if not slot.is_empty() else None
            slot_equipment_category = slot.enforced_equipment_category
            image = None
            tooltip = None
            if item_id:
                item_type = item_id.item_type
                data = get_item_data_by_type(item_type)
                image = self.images_by_ui_sprite[data.icon_sprite]
                category_name = None
                if data.item_equipment_category:
                    category_name = ITEM_EQUIPMENT_CATEGORY_NAMES[data.item_equipment_category]
                description_lines = create_item_description(item_id)
                item_name = item_id.name
                is_rare = bool(item_id.affix_stats)
                is_unique = data.is_unique
                tooltip = TooltipGraphics.create_for_item(self.ui_render, item_name, category_name, icon.rect.topleft,
                                                          description_lines, is_rare=is_rare, is_unique=is_unique)
            elif slot_equipment_category:
                image = self.images_by_item_category[slot_equipment_category]
                category_name = ITEM_EQUIPMENT_CATEGORY_NAMES[slot_equipment_category]
                tooltip_details = [DetailLine("[" + category_name + "]"),
                                   DetailLine("You have nothing equipped. Drag an item here to equip it!")]
                tooltip = TooltipGraphics(self.ui_render, COLOR_WHITE, "...", tooltip_details,
                                          bottom_left=icon.rect.topleft)

            icon.image = image
            icon.tooltip = tooltip
            icon.slot_equipment_category = slot_equipment_category
            icon.item_id = item_id

    def on_fullscreen_changed(self, fullscreen: bool):
        self.fullscreen_checkbox.checked = fullscreen

    def on_world_area_updated(self, world_area: Rect):
        self.minimap.update_world_area(world_area)

    def on_walls_seen(self, seen_wall_positions: List[Tuple[int, int]]):
        self.minimap.add_walls(seen_wall_positions)

    def on_player_position_updated(self, center_position: Tuple[int, int]):
        self.minimap.update_player_position(center_position)

    # --------------------------------------------------------------------------------------------------------
    #                              HANDLE DIALOG USER INTERACTIONS
    # --------------------------------------------------------------------------------------------------------

    def start_dialog_with_npc(self, npc: NonPlayerCharacter, dialog_data: DialogData) -> int:
        self.dialog_state.active = True
        self.dialog_state.npc = npc
        self.dialog_state.data = dialog_data
        if self.dialog_state.option_index >= len(dialog_data.options):
            self.dialog_state.option_index = 0
        self._update_dialog_graphics()
        return self.dialog_state.option_index

    def change_dialog_option(self, delta: int) -> Tuple[NpcType, int, int]:
        previous_option_index = self.dialog_state.option_index
        self.dialog_state.option_index = (self.dialog_state.option_index + delta) % len(self.dialog_state.data.options)
        self._update_dialog_graphics()
        new_option_index = self.dialog_state.option_index
        return self.dialog_state.npc.npc_type, previous_option_index, new_option_index

    def _update_dialog_graphics(self):
        if self.dialog_state.active:

            build_dialog_option = lambda option: DialogOption(
                option.summary, option.action_text,
                self.images_by_ui_sprite[option.ui_icon_sprite] if option.ui_icon_sprite else None,
                option.detail_header, option.detail_body)

            data = self.dialog_state.data
            image = self.images_by_portrait_sprite[data.portrait_icon_sprite]
            text_body = data.text_body
            options = [build_dialog_option(option) for option in data.options]
            active_option_index = self.dialog_state.option_index
            self.dialog.show_with_data(data.name, image, text_body, options, active_option_index)
        else:
            self.dialog.hide()

    def has_open_dialog(self) -> bool:
        return self.dialog_state.active

    # --------------------------------------------------------------------------------------------------------
    #                                     UPDATE MISC. STATE
    # --------------------------------------------------------------------------------------------------------

    def update(self, time_passed: Millis):
        self.minimap.update(time_passed)

        self._ticks_since_last_consumable_action += time_passed
        if self._ticks_since_last_consumable_action > HIGHLIGHT_CONSUMABLE_ACTION_DURATION:
            self.highlighted_consumable_action = None

        self._ticks_since_last_ability_action += time_passed
        if self._ticks_since_last_ability_action > HIGHLIGHT_ABILITY_ACTION_DURATION:
            self.highlighted_ability_action = None

        self.info_message.notify_time_passed(time_passed)

    def update_hero(self, hero_id: HeroId):
        sprite = HEROES[hero_id].portrait_icon_sprite
        image = self.images_by_portrait_sprite[sprite]
        self.portrait.image = image
        self.stats_window.hero_id = hero_id

    def set_paused(self, paused: bool):
        self.paused_splash_screen.shown = paused

    def update_fps_string(self, fps_string: str):
        self.fps_string = fps_string

    def update_game_mode_string(self, game_mode_string: str):
        self.game_mode_string = game_mode_string

    def remove_highlight_from_talent_toggle(self):
        self.talents_toggle.highlighted = False

    def set_minimap_highlight(self, position_ratio: Tuple[float, float]):
        self.minimap.set_highlight(position_ratio)

    def remove_minimap_highlight(self):
        self.minimap.remove_highlight()

    def set_inventory_highlight(self, item_id: ItemId):
        for icon in self.inventory_icons:
            if icon.item_id == item_id:
                self.manually_highlighted_inventory_item = item_id

    def remove_inventory_highlight(self):
        self.manually_highlighted_inventory_item = None

    # --------------------------------------------------------------------------------------------------------
    #                                          RENDERING
    # --------------------------------------------------------------------------------------------------------

    def _translate_ui_position_to_screen(self, position):
        return position[0] + self.ui_screen_area.x, position[1] + self.ui_screen_area.y

    def _translate_screen_position_to_ui(self, position: Tuple[int, int]):
        return position[0] - self.ui_screen_area.x, position[1] - self.ui_screen_area.y

    def _render_item_being_dragged(self, item_id: ItemId, mouse_screen_position: Tuple[int, int],
                                   relative_mouse_pos: Tuple[int, int]):
        ui_icon_sprite = get_item_data(item_id).icon_sprite
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

    def render(self):

        self.screen_render.rect(COLOR_BORDER, Rect(0, 0, self.camera_size[0], self.camera_size[1]), 1)
        self.screen_render.rect_filled((20, 10, 0), Rect(0, self.camera_size[1], self.screen_size[0],
                                                         self.screen_size[1] - self.camera_size[1]))

        # CONSUMABLES
        self.ui_render.rect_filled((60, 60, 80), self.consumable_icons_row)
        for icon in self.consumable_icons:
            # TODO treat this as state and update it elsewhere
            recently_clicked = icon.slot_number == self.highlighted_consumable_action
            icon.render(recently_clicked)

        # ABILITIES
        self.ui_render.rect_filled((60, 60, 80), self.ability_icons_row)
        for icon in self.ability_icons:
            ability_type = icon.ability_type
            # TODO treat this as state and update it elsewhere
            if ability_type:
                recently_clicked = ability_type == self.highlighted_ability_action
                icon.render(recently_clicked)

        # ITEMS
        self.ui_render.rect_filled((60, 60, 80), self.inventory_icons_rect)
        for icon in self.inventory_icons:
            # TODO treat this as state and update it elsewhere
            highlighted = False
            if self.item_slot_being_dragged and self.item_slot_being_dragged.item_id:
                item_type = self.item_slot_being_dragged.item_id.item_type
                item_data = get_item_data_by_type(item_type)
                highlighted = item_data.item_equipment_category \
                              and icon.slot_equipment_category == item_data.item_equipment_category
            if self.manually_highlighted_inventory_item and self.manually_highlighted_inventory_item == icon.item_id:
                highlighted = True
            icon.render(highlighted)

        # MINIMAP
        self.minimap.render()

        simple_components = [self.exp_bar, self.portrait, self.healthbar, self.manabar, self.money_text,
                             self.buffs, self.sound_checkbox, self.save_button, self.fullscreen_checkbox,
                             self.stats_window, self.talents_window, self.quests_window,
                             self.controls_window] + self.toggle_buttons

        for component in simple_components:
            component.render()

        self.screen_render.rect(COLOR_BORDER, self.ui_screen_area, 1)

        self.screen_render.rect_transparent(Rect(1, 1, 70, 20), 100, COLOR_BLACK)
        self.screen_render.text(self.font_debug_info, "fps: " + self.fps_string, (6, 4))
        if self.game_mode_string:
            self.screen_render.rect_transparent(Rect(1, 23, 70, 20), 100, COLOR_BLACK)
            self.screen_render.text(self.font_debug_info, self.game_mode_string, (6, 26))

        self.message.render(self.info_message.message)

        # TODO Bring back relative render position for dragged entities
        if self.item_slot_being_dragged:
            self._render_item_being_dragged(self.item_slot_being_dragged.item_id, self.mouse_screen_position,
                                            (UI_ICON_SIZE[0] // 2, (UI_ICON_SIZE[1] // 2)))
        elif self.consumable_slot_being_dragged:
            self._render_consumable_being_dragged(self.consumable_slot_being_dragged.consumable_types[0],
                                                  self.mouse_screen_position,
                                                  (UI_ICON_SIZE[0] // 2, (UI_ICON_SIZE[1] // 2)))

        self.dialog.render()

        if self.hovered_component and self.hovered_component.tooltip and not self.item_slot_being_dragged \
                and not self.consumable_slot_being_dragged:
            tooltip: TooltipGraphics = self.hovered_component.tooltip
            tooltip.render()

        self.paused_splash_screen.render()
