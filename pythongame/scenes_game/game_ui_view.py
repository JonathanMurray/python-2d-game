from typing import List, Tuple, Optional, Dict, Any

import pygame
from pygame.rect import Rect

from pythongame.core.common import ConsumableType, ItemType, HeroId, UiIconSprite, AbilityType, PortraitIconSprite
from pythongame.core.game_data import ABILITIES, BUFF_TEXTS, \
    KEYS_BY_ABILITY_TYPE, CONSUMABLES, ITEMS, HEROES
from pythongame.core.game_state import PlayerState
from pythongame.core.item_inventory import ItemInventorySlot, ItemEquipmentCategory, ITEM_EQUIPMENT_CATEGORY_NAMES
from pythongame.core.math import is_point_in_rect
from pythongame.core.npc_behaviors import DialogData
from pythongame.core.talents import TalentsGraphics
from pythongame.core.view.render_util import DrawableArea
from pythongame.scenes_game.game_ui_state import GameUiState, UiToggle
from pythongame.scenes_game.ui_components import AbilityIcon, ConsumableIcon, ItemIcon, TooltipGraphics, StatBar, \
    ToggleButton, ControlsWindow, StatsWindow, TalentIcon, TalentsWindow, ExpBar, Portrait, Minimap, Buffs, Text, \
    DialogOption, Dialog

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


class DraggedItemSlot:
    def __init__(self, slot_number: int, item_type: ItemType, relative_mouse_pos: Tuple[int, int]):
        self.slot_number = slot_number
        self.item_type = item_type
        self.relative_mouse_pos = relative_mouse_pos


class DraggedConsumableSlot:
    def __init__(self, slot_number: int, consumable_types: List[ConsumableType], relative_mouse_pos: Tuple[int, int]):
        self.slot_number = slot_number
        self.consumable_types = consumable_types
        self.relative_mouse_pos = relative_mouse_pos


class MouseHoverEvent:
    def __init__(self, item: Optional[DraggedItemSlot], consumable: Optional[DraggedConsumableSlot], is_over_ui: bool,
                 ui_toggle: Optional[UiToggle], talent_choice_option: Optional[Tuple[int, int]]):
        self.item = item
        self.consumable = consumable
        self.is_over_ui: bool = is_over_ui
        self.ui_toggle = ui_toggle
        self.talent_choice_option = talent_choice_option  # (choice_index, option_index)


class MouseDrag:
    def __init__(self, consumable: Optional[DraggedConsumableSlot], item: Optional[DraggedItemSlot],
                 screen_pos: Tuple[int, int]):
        self.consumable = consumable
        self.item = item
        self.screen_pos = screen_pos


class DialogConfig:
    def __init__(self, data: DialogData, option_index: int):
        self.data = data
        self.option_index = option_index


class GameUiView:

    def __init__(self, pygame_screen, camera_size: Tuple[int, int], screen_size: Tuple[int, int],
                 images_by_ui_sprite: Dict[UiIconSprite, Any], big_images_by_ui_sprite: Dict[UiIconSprite, Any],
                 images_by_portrait_sprite: Dict[PortraitIconSprite, Any]):
        pygame.font.init()
        self.screen_render = DrawableArea(pygame_screen)
        self.ui_render = DrawableArea(pygame_screen, self._translate_ui_position_to_screen)

        self.ui_screen_area = Rect(0, camera_size[1], screen_size[0], screen_size[1] - camera_size[1])
        self.camera_size = camera_size
        self.screen_size = screen_size

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

        self.images_by_ui_sprite = images_by_ui_sprite
        self.big_images_by_ui_sprite = big_images_by_ui_sprite
        self.images_by_portrait_sprite = images_by_portrait_sprite

        # This is updated every time the view is called
        self.camera_world_area = None

        self.ability_icons_row: Rect = Rect(0, 0, 0, 0)
        self.ability_icons: List[AbilityIcon] = []
        self.consumable_icons_row: Rect = Rect(0, 0, 0, 0)
        self.consumable_icons: List[ConsumableIcon] = []
        self.inventory_icons_rect: Rect = Rect(0, 0, 0, 0)
        self.inventory_icons: List[ItemIcon] = []
        self.exp_bar = ExpBar(self.ui_render, Rect(140, 23, 300, 2), self.font_level)
        self.minimap = Minimap(self.ui_render, Rect(440, 52, 80, 80))
        self.buffs = Buffs(self.ui_render, self.font_buff_texts)
        self.money_text = Text(self.ui_render, self.font_ui_money, (24, 150))

        self._setup_ability_icons()
        self._setup_consumable_icons()
        self._setup_inventory_icons()
        self._setup_health_and_mana_bars()
        self._setup_toggle_buttons()
        self._setup_stats_window()
        self._setup_talents_window(TalentsGraphics([]))
        self._setup_controls_window()
        self._setup_portrait()
        self._setup_dialog()

        self.hovered_component = None

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
            icon = AbilityIcon(self.ui_render, rect, None, None, self.font_ui_icon_keys, None, None)
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
        self.healthbar = StatBar(self.ui_render, rect_healthbar, (200, 0, 50), None, border=True,
                                 show_numbers=True, font=self.font_ui_stat_bar_numbers)
        rect_manabar = Rect(20, 132, 100, 14)
        self.manabar = StatBar(self.ui_render, rect_manabar, (50, 0, 200), None, border=True,
                               show_numbers=True, font=self.font_ui_stat_bar_numbers)

    def _setup_toggle_buttons(self):
        x = 555
        y_0 = 30
        w = 120
        h = 20
        font = self.font_tooltip_details
        self.toggle_buttons = [
            ToggleButton(self.ui_render, Rect(x, y_0, w, h), font, "STATS    [A]", UiToggle.STATS, False),
            ToggleButton(self.ui_render, Rect(x, y_0 + 30, w, h), font, "TALENTS  [T]", UiToggle.TALENTS, False),
            ToggleButton(self.ui_render, Rect(x, y_0 + 60, w, h), font, "CONTROLS [C]", UiToggle.CONTROLS, False)
        ]

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
        self.talents_window = TalentsWindow(self.ui_render, rect, self.font_tooltip_details, self.font_stats, talents,
                                            icon_rows)

    def _setup_controls_window(self):
        rect = Rect(545, -300, 140, 170)
        self.controls_window = ControlsWindow(self.ui_render, rect, self.font_tooltip_details, self.font_stats)

    def _setup_portrait(self):
        rect = Rect(20, 18, PORTRAIT_ICON_SIZE[0], PORTRAIT_ICON_SIZE[1])
        self.portrait = Portrait(self.ui_render, rect, None)

    def _setup_dialog(self):
        self.dialog = Dialog(self.screen_render, None, None, [], 0, PORTRAIT_ICON_SIZE, UI_ICON_SIZE)

    def update_abilities(self, abilities: List[AbilityType]):
        for i, ability_type in enumerate(abilities):
            ability = ABILITIES[ability_type]
            icon = self.ability_icons[i]
            icon.update(
                image=self.images_by_ui_sprite[ability.icon_sprite],
                label=KEYS_BY_ABILITY_TYPE[ability_type].key_string,
                ability=ability,
                ability_type=ability_type)

    def update_consumables(self, consumable_slots: Dict[int, List[ConsumableType]]):
        for i, slot_number in enumerate(consumable_slots):
            icon = self.consumable_icons[i]
            consumable_types = consumable_slots[slot_number]
            image = None
            consumable = None
            if consumable_types:
                consumable = CONSUMABLES[consumable_types[0]]
                image = self.images_by_ui_sprite[consumable.icon_sprite]

            icon.update(image, consumable, consumable_types)

    def update_inventory(self, item_slots: List[ItemInventorySlot]):
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
                image = self._get_image_for_item_category(slot_equipment_category)
                category_name = ITEM_EQUIPMENT_CATEGORY_NAMES[slot_equipment_category]
                tooltip_details = ["[" + category_name + "]",
                                   "You have nothing equipped. Drag an item here to equip it!"]
                tooltip = TooltipGraphics(self.ui_render, COLOR_WHITE, "...", tooltip_details,
                                          bottom_left=icon.rect.topleft)

            icon.image = image
            icon.tooltip = tooltip
            icon.slot_equipment_category = slot_equipment_category
            icon.item_type = item_type

    def update_regen(self, health_regen: float, mana_regen: float):
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

    def update_has_unseen_talents(self, has_unseen_talents: bool):
        # TODO Don't rely on TALENTS being second in the list
        self.toggle_buttons[1].highlighted = has_unseen_talents

    def update_talents(self, talents: TalentsGraphics):
        # TODO Don't recreate components
        self._setup_talents_window(talents)

    def update_player_stats(self, player_state: PlayerState, player_speed_multiplier: float):
        self.stats_window.player_state = player_state
        self.stats_window.player_speed_multiplier = player_speed_multiplier

    def update_hero(self, hero_id: HeroId):
        sprite = HEROES[hero_id].portrait_icon_sprite
        image = self.images_by_portrait_sprite[sprite]
        self.portrait.image = image

    def update_dialog(self, dialog_config: DialogConfig):
        if dialog_config:
            options = [
                DialogOption(
                    option.summary,
                    option.action_text,
                    self.images_by_ui_sprite[option.ui_icon_sprite] if option.ui_icon_sprite else None,
                    option.detail_header,
                    option.detail_body)
                for option in dialog_config.data.options]
            portrait_image = self.images_by_portrait_sprite[dialog_config.data.portrait_icon_sprite]
            self.dialog.portrait_image = portrait_image
            self.dialog.text_body = dialog_config.data.text_body
            self.dialog.options = options
            self.dialog.active_option_index = dialog_config.option_index
            self.dialog.shown = True
        else:
            self.dialog.shown = False

    def _translate_ui_position_to_screen(self, position):
        return position[0] + self.ui_screen_area.x, position[1] + self.ui_screen_area.y

    def _translate_screen_position_to_ui(self, position: Tuple[int, int]):
        return position[0] - self.ui_screen_area.x, position[1] - self.ui_screen_area.y

    def _get_image_for_item_category(self, slot_equipment_category: ItemEquipmentCategory):
        if slot_equipment_category == ItemEquipmentCategory.HEAD:
            ui_icon_sprite = UiIconSprite.INVENTORY_TEMPLATE_HELMET
        elif slot_equipment_category == ItemEquipmentCategory.CHEST:
            ui_icon_sprite = UiIconSprite.INVENTORY_TEMPLATE_CHEST
        elif slot_equipment_category == ItemEquipmentCategory.MAIN_HAND:
            ui_icon_sprite = UiIconSprite.INVENTORY_TEMPLATE_MAINHAND
        elif slot_equipment_category == ItemEquipmentCategory.OFF_HAND:
            ui_icon_sprite = UiIconSprite.INVENTORY_TEMPLATE_OFFHAND
        elif slot_equipment_category == ItemEquipmentCategory.NECK:
            ui_icon_sprite = UiIconSprite.INVENTORY_TEMPLATE_NECK
        elif slot_equipment_category == ItemEquipmentCategory.RING:
            ui_icon_sprite = UiIconSprite.INVENTORY_TEMPLATE_RING
        else:
            raise Exception("Unhandled equipment category: " + str(slot_equipment_category))
        return self.images_by_ui_sprite[ui_icon_sprite]

    def _message(self, message):
        w_rect = len(message) * 9 + 10
        x_message = self.ui_screen_area.w / 2 - w_rect / 2
        y_message = self.ui_screen_area.y - 30
        self.screen_render.rect_transparent(Rect(x_message - 10, y_message - 5, w_rect, 28), 135, (0, 0, 0))
        self.screen_render.text(self.font_message, message, (x_message, y_message))

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

    def _splash_screen_text(self, text, x, y):
        self.screen_render.text(self.font_splash_screen, text, (x, y), COLOR_WHITE)
        self.screen_render.text(self.font_splash_screen, text, (x + 2, y + 2), COLOR_BLACK)

    def handle_mouse(self, mouse_screen_pos: Tuple[int, int], toggle_enabled: Optional[UiToggle]) -> MouseHoverEvent:
        self.hovered_component = None

        hovered_item_slot = None
        hovered_consumable_slot = None
        is_mouse_hovering_ui = is_point_in_rect(mouse_screen_pos, self.ui_screen_area)
        hovered_ui_toggle = None
        hovered_talent_option: Optional[Tuple[int, int]] = None

        mouse_ui_position = self._translate_screen_position_to_ui(mouse_screen_pos)
        if self.healthbar.contains(mouse_ui_position):
            self.hovered_component = self.healthbar
        if self.manabar.contains(mouse_ui_position):
            self.hovered_component = self.manabar
        for icon in self.consumable_icons:
            collision_offset = icon.get_collision_offset(mouse_ui_position)
            if collision_offset:
                self.hovered_component = icon
                hovered_consumable_slot = DraggedConsumableSlot(icon.slot_number, icon.consumable_types,
                                                                collision_offset)
        for icon in self.ability_icons:
            if icon.contains(mouse_ui_position):
                self.hovered_component = icon
        for icon in self.inventory_icons:
            collision_offset = icon.get_collision_offset(mouse_ui_position)
            if collision_offset:
                self.hovered_component = icon
                hovered_item_slot = DraggedItemSlot(icon.inventory_slot_index, icon.item_type, collision_offset)
        if toggle_enabled == UiToggle.TALENTS:
            hovered_icon = self.talents_window.get_icon_containing(mouse_ui_position)
            if hovered_icon:
                self.hovered_component = hovered_icon
                hovered_talent_option = (hovered_icon.choice_index, hovered_icon.option_index)
        for toggle_button in self.toggle_buttons:
            if toggle_button.contains(mouse_ui_position):
                self.hovered_component = toggle_button
                hovered_ui_toggle = toggle_button.toggle_id

        return MouseHoverEvent(hovered_item_slot, hovered_consumable_slot, is_mouse_hovering_ui, hovered_ui_toggle,
                               hovered_talent_option)

    def render_ui(
            self,
            player_state: PlayerState,
            ui_state: GameUiState,
            text_in_topleft_corner: str,
            is_paused: bool,
            mouse_drag: Optional[MouseDrag]):

        self.screen_render.rect(COLOR_BORDER, Rect(0, 0, self.camera_size[0], self.camera_size[1]), 1)
        self.screen_render.rect_filled((20, 10, 0), Rect(0, self.camera_size[1], self.screen_size[0],
                                                         self.screen_size[1] - self.camera_size[1]))

        # EXP BAR
        self.exp_bar.render(player_state.level, player_state.exp / player_state.max_exp_in_this_level)

        # PORTRAIT
        self.portrait.render()

        # HEALTHBAR
        self.healthbar.render(player_state.health_resource.value, player_state.health_resource.max_value)

        # MANABAR
        self.manabar.render(player_state.mana_resource.value, player_state.mana_resource.max_value)

        # MONEY
        self.money_text.render("Money: " + str(player_state.money))

        # CONSUMABLES
        self.ui_render.rect_filled((60, 60, 80), self.consumable_icons_row)
        for icon in self.consumable_icons:
            hovered = self.hovered_component == icon
            recently_clicked = icon.slot_number == ui_state.highlighted_consumable_action
            icon.render(hovered, recently_clicked)

        # ABILITIES
        self.ui_render.rect_filled((60, 60, 80), self.ability_icons_row)
        for icon in self.ability_icons:
            ability_type = icon.ability_type
            if ability_type:
                ability = ABILITIES[ability_type]
                cooldown_remaining_ratio = player_state.ability_cooldowns_remaining[ability_type] / ability.cooldown
                recently_clicked = ability_type == ui_state.highlighted_ability_action
                hovered = self.hovered_component == icon
                icon.render(hovered, recently_clicked, cooldown_remaining_ratio)

        # ITEMS
        self.ui_render.rect_filled((60, 60, 80), self.inventory_icons_rect)
        for icon in self.inventory_icons:
            hovered = self.hovered_component == icon
            highlighted = mouse_drag and mouse_drag.item and mouse_drag.item.item_type \
                          and ITEMS[mouse_drag.item.item_type].item_equipment_category \
                          and icon.slot_equipment_category == ITEMS[mouse_drag.item.item_type].item_equipment_category
            icon.render(hovered, highlighted)

        # MINIMAP
        self.minimap.render(ui_state.player_minimap_relative_position)

        # DIALOG
        if self.dialog.shown:
            self.dialog.render()

        # BUFFS
        buffs = []
        for active_buff in player_state.active_buffs:
            buff_type = active_buff.buff_effect.get_buff_type()
            # Buffs that don't have description texts shouldn't be displayed. (They are typically irrelevant to the
            # player)
            if buff_type in BUFF_TEXTS:
                text = BUFF_TEXTS[buff_type]
                ratio_remaining = active_buff.get_ratio_duration_remaining()
                buffs.append((text, ratio_remaining))
        self.buffs.render(buffs)

        # TOGGLES
        if ui_state.toggle_enabled == UiToggle.STATS:
            self.stats_window.render()
        elif ui_state.toggle_enabled == UiToggle.TALENTS:
            self.talents_window.render(self.hovered_component)
        elif ui_state.toggle_enabled == UiToggle.CONTROLS:
            self.controls_window.render()

        for toggle_button in self.toggle_buttons:
            enabled = ui_state.toggle_enabled == toggle_button.toggle_id
            hovered = self.hovered_component == toggle_button
            toggle_button.render(enabled, hovered)

        self.screen_render.rect(COLOR_BORDER, self.ui_screen_area, 1)

        self.screen_render.rect_transparent(Rect(0, 0, 70, 20), 100, COLOR_BLACK)
        self.screen_render.text(self.font_debug_info, text_in_topleft_corner, (5, 3))

        if ui_state.message:
            self._message(ui_state.message)

        if self.hovered_component and self.hovered_component.tooltip and not mouse_drag:
            tooltip: TooltipGraphics = self.hovered_component.tooltip
            tooltip.render()

        if mouse_drag:
            if mouse_drag.item:
                self._render_item_being_dragged(mouse_drag.item.item_type, mouse_drag.screen_pos,
                                                mouse_drag.item.relative_mouse_pos)
            elif mouse_drag.consumable:
                self._render_consumable_being_dragged(mouse_drag.consumable.consumable_types[0], mouse_drag.screen_pos,
                                                      mouse_drag.consumable.relative_mouse_pos)

        if is_paused:
            self.screen_render.rect_transparent(Rect(0, 0, self.screen_size[0], self.screen_size[1]), 140, COLOR_BLACK)
            self._splash_screen_text("PAUSED", self.screen_size[0] / 2 - 110, self.screen_size[1] / 2 - 50)
