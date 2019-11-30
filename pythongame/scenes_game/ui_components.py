import math
from typing import List, Tuple, Optional, Any

import pygame
from pygame.rect import Rect

from pythongame.core.common import ConsumableType, ItemType, AbilityType, PortraitIconSprite
from pythongame.core.game_data import CONSUMABLES, ConsumableCategory, AbilityData, ConsumableData
from pythongame.core.game_state import PlayerState
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.talents import TalentsGraphics
from pythongame.core.view.render_util import DrawableArea, split_text_into_lines
from pythongame.scenes_game.game_ui_state import ToggleButtonId

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (250, 250, 250)

COLOR_HOVERED = (200, 200, 250)
COLOR_ICON_HIGHLIGHTED = (250, 250, 150)
COLOR_TOGGLE_HIGHLIGHTED = (150, 250, 200)
DIR_FONTS = './resources/fonts/'


class UiComponent:
    def __init__(self):
        self.hovered = False


class DialogOption:
    def __init__(self, summary: str, detail_action_text: str, detail_image: Optional[Any],
                 detail_header: Optional[str] = None, detail_body: Optional[str] = None):
        self.summary = summary
        self.detail_action_text = detail_action_text
        self.detail_image = detail_image
        self.detail_header = detail_header
        self.detail_body = detail_body


class Dialog:
    def __init__(self, screen_render: DrawableArea, portrait_image: PortraitIconSprite, text_body: str,
                 options: List[DialogOption], active_option_index: int, portrait_image_size: Tuple[int, int],
                 option_image_size: Tuple[int, int]):
        self.screen_render = screen_render
        self.portrait_image = portrait_image
        self.text_body = text_body
        self.options = options
        self.active_option_index = active_option_index
        self.font_dialog = pygame.font.Font(DIR_FONTS + 'Merchant Copy.ttf', 24)
        self.font_dialog_option_detail_body = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.portrait_image_size = portrait_image_size
        self.option_image_size = option_image_size
        self.shown = False

    def render(self):
        if self.shown:
            self._render()

    def _render(self):

        tall_detail_section = any(
            [o.detail_body is not None or o.detail_header is not None or o.detail_image is not None
             for o in self.options])

        h_detail_section_expansion = 82

        options_margin = 10
        option_padding = 4
        h_option_line = 20
        if tall_detail_section:
            h_dialog_container = 310 + len(self.options) * (h_option_line + 2 * option_padding)
        else:
            h_dialog_container = 310 + len(self.options) * (h_option_line + 2 * option_padding) \
                                 - h_detail_section_expansion
        rect_dialog_container = Rect(100, 35, 500, h_dialog_container)

        x_left = rect_dialog_container[0]
        x_right = rect_dialog_container[0] + rect_dialog_container[2]
        self.screen_render.rect((210, 180, 60), rect_dialog_container, 5)
        self.screen_render.rect_transparent(rect_dialog_container, 200, COLOR_BLACK)
        color_separator = (170, 140, 20)
        dialog_container_portrait_padding = 10
        rect_portrait_pos = (x_left + dialog_container_portrait_padding,
                             rect_dialog_container[1] + dialog_container_portrait_padding)
        self.screen_render.image(self.portrait_image, rect_portrait_pos)
        rect_portrait = Rect(rect_portrait_pos[0], rect_portrait_pos[1], self.portrait_image_size[0],
                             self.portrait_image_size[1])
        self.screen_render.rect((160, 160, 180), rect_portrait, 2)

        dialog_pos = (x_left + 120, rect_dialog_container[1] + 15)
        dialog_lines = split_text_into_lines(self.text_body, 35)
        for i, dialog_text_line in enumerate(dialog_lines):
            if i == 6:
                print("WARN: too long dialog for NPC!")
                break
            self.screen_render.text(self.font_dialog, dialog_text_line, (dialog_pos[0] + 5, dialog_pos[1] + 32 * i),
                                    COLOR_WHITE)

        y_above_options = dialog_pos[1] + 150
        self.screen_render.line(color_separator, (x_left, y_above_options), (x_right, y_above_options), 2)

        for i, option in enumerate(self.options):
            x_option = x_left + 8
            y_option = y_above_options + options_margin + i * (h_option_line + 2 * option_padding)
            x_option_text = x_option + option_padding + 5
            y_option_text = y_option + option_padding + 2
            color_highlight = COLOR_WHITE

            is_option_active = self.active_option_index == i
            color_option_text = COLOR_WHITE if is_option_active else (160, 160, 160)
            if is_option_active:
                rect_highlight_active_option = Rect(
                    x_option, y_option, rect_dialog_container[2] - 16, h_option_line + 2 * option_padding)
                self.screen_render.rect_transparent(rect_highlight_active_option, 120, COLOR_WHITE)
                self.screen_render.rect(color_highlight, rect_highlight_active_option, 1)
            self.screen_render.text(self.font_dialog, option.summary, (x_option_text, y_option_text), color_option_text)

        active_option = self.options[self.active_option_index]
        y_under_options = y_above_options + 2 * options_margin \
                          + len(self.options) * (h_option_line + 2 * option_padding)
        self.screen_render.line(color_separator, (x_left, y_under_options), (x_right, y_under_options), 2)

        if tall_detail_section:
            y_action_text = y_under_options + 15 + h_detail_section_expansion
        else:
            y_action_text = y_under_options + 15

        if tall_detail_section:
            if active_option.detail_image is not None:
                active_option_image = active_option.detail_image
                pos_option_image = x_left + 6, y_under_options + 7
                self.screen_render.image(active_option_image, pos_option_image)
                rect_option_image = Rect(pos_option_image[0], pos_option_image[1], self.option_image_size[0],
                                         self.option_image_size[1])
                self.screen_render.rect((150, 150, 150), rect_option_image, 1)
            if active_option.detail_header is not None:
                self.screen_render.text(self.font_dialog, active_option.detail_header,
                                        (x_left + 14 + self.option_image_size[0] + 4,
                                         y_action_text - h_detail_section_expansion))
            if active_option.detail_body is not None:
                detail_body_lines = split_text_into_lines(active_option.detail_body, 70)
                for i, line in enumerate(detail_body_lines):
                    line_pos = (x_left + 10, y_action_text - h_detail_section_expansion + 35 + 20 * i)
                    self.screen_render.text(self.font_dialog_option_detail_body, line, line_pos)
        action_text = active_option.detail_action_text
        self.screen_render.text(self.font_dialog, "[Space] : " + action_text, (x_left + 10, y_action_text))


class TooltipGraphics:
    def __init__(self, ui_render: DrawableArea, title_color: Tuple[int, int, int],
                 title: str, details: List[str], bottom_left: Optional[Tuple[int, int]] = None,
                 bottom_right: Optional[Tuple[int, int]] = None):
        self._ui_render = ui_render
        self._font_header = pygame.font.Font(DIR_FONTS + 'Herculanum.ttf', 16)
        self._font_details = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self._title_color = title_color
        self._title = title
        self._detail_lines = []
        for detail in details:
            self._detail_lines += split_text_into_lines(detail, 32)
        w = 260
        h = 60 + 17 * len(self._detail_lines)
        if bottom_left:
            self._rect = Rect(bottom_left[0], bottom_left[1] - h - 3, w, h)
        else:
            self._rect = Rect(bottom_right[0] - w, bottom_right[1] - h - 3, w, h)

    def render(self):
        self._ui_render.rect_transparent(self._rect, 200, (0, 0, 30))
        self._ui_render.rect(COLOR_WHITE, self._rect, 1)
        header_position = (self._rect.x + 20, self._rect.y + 12)
        self._ui_render.text(self._font_header, self._title, header_position, self._title_color)
        y_separator = self._rect.y + 37
        separator_start = (self._rect.x + 10, y_separator)
        separator_end = (self._rect.x + self._rect.w - 10, y_separator)
        self._ui_render.line(COLOR_WHITE, separator_start, separator_end, 1)
        for i, line in enumerate(self._detail_lines):
            self._ui_render.text(self._font_details, line, (self._rect.x + 20, self._rect.y + 47 + i * 18), COLOR_WHITE)


class AbilityIcon(UiComponent):
    def __init__(self, ui_render: DrawableArea, rect: Rect, image, label: str, font, tooltip: TooltipGraphics,
                 ability_type: AbilityType, cooldown_remaining_ratio: float):
        super().__init__()
        self._ui_render = ui_render
        self._font = font
        self.rect = rect
        self.image = image
        self.label = label
        self.tooltip = tooltip
        self.ability_type = ability_type
        self.cooldown_remaining_ratio = cooldown_remaining_ratio

    def contains(self, point: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(point[0], point[1])

    def render(self, recently_clicked: bool):
        self._ui_render.rect_filled((40, 40, 50), self.rect)
        self._ui_render.image(self.image, self.rect.topleft)
        self._ui_render.rect((150, 150, 190), self.rect, 1)
        if recently_clicked:
            self._ui_render.rect(COLOR_ICON_HIGHLIGHTED,
                                 Rect(self.rect.x - 1, self.rect.y - 1, self.rect.w + 2, self.rect.h + 2), 3)
        elif self.hovered:
            self._ui_render.rect(COLOR_HOVERED, self.rect, 1)
        self._ui_render.text(self._font, self.label, (self.rect.x + 12, self.rect.y + self.rect.h + 4))

        if self.cooldown_remaining_ratio > 0:
            cooldown_rect = Rect(self.rect.x + 1,
                                 self.rect.y + 1 + (self.rect.h - 2) * (1 - self.cooldown_remaining_ratio),
                                 self.rect.w - 2,
                                 (self.rect.h - 2) * self.cooldown_remaining_ratio + 1)
            self._ui_render.rect_filled((100, 30, 30), cooldown_rect)
            self._ui_render.rect((180, 30, 30), self.rect, 2)

    def update(self, image, label: str, ability: AbilityData, ability_type: AbilityType):
        self.image = image
        self.label = label
        tooltip_details = ["Cooldown: " + str(ability.cooldown / 1000.0) + " s",
                           "Mana: " + str(ability.mana_cost),
                           ability.description]
        self.tooltip = TooltipGraphics(self._ui_render, COLOR_WHITE, ability.name, tooltip_details,
                                       bottom_left=self.rect.topleft)
        self.ability_type = ability_type


class ConsumableIcon(UiComponent):
    def __init__(self, ui_render: DrawableArea, rect: Rect, image, label: str, font, tooltip: TooltipGraphics,
                 consumable_types: List[ConsumableType], slot_number: int):
        super().__init__()
        self._ui_render = ui_render
        self._rect = rect
        self._image = image
        self._label = label
        self._font = font
        self.consumable_types = consumable_types
        self.tooltip = tooltip
        self.slot_number = slot_number

    def get_collision_offset(self, point: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        if self._rect.collidepoint(point[0], point[1]):
            return point[0] - self._rect.x, point[1] - self._rect.y
        return None

    def render(self, recently_clicked: bool):
        self._ui_render.rect_filled((40, 40, 50), self._rect)
        if self._image:
            self._ui_render.image(self._image, self._rect.topleft)
        self._ui_render.rect((150, 150, 190), self._rect, 1)

        sub_rect_h = 3
        for i in range(len(self.consumable_types)):
            sub_consumable_type = self.consumable_types[i]
            consumable_category = CONSUMABLES[sub_consumable_type].category
            if consumable_category == ConsumableCategory.HEALTH:
                sub_rect_color = (160, 110, 110)
            elif consumable_category == ConsumableCategory.MANA:
                sub_rect_color = (110, 110, 200)
            else:
                sub_rect_color = (170, 170, 170)
            self._ui_render.rect_filled(
                sub_rect_color,
                Rect(self._rect.x, self._rect.y - 2 - (sub_rect_h + 1) * (i + 1), self._rect.w, sub_rect_h))

        if recently_clicked:
            self._ui_render.rect(COLOR_ICON_HIGHLIGHTED,
                                 Rect(self._rect.x - 1, self._rect.y - 1, self._rect.w + 2, self._rect.h + 2), 3)
        elif self.hovered:
            self._ui_render.rect(COLOR_HOVERED, self._rect, 1)
        self._ui_render.text(self._font, self._label, (self._rect.x + 12, self._rect.y + self._rect.h + 4))

    def update(self, image, top_consumable: ConsumableData, consumable_types: List[ConsumableType]):
        self._image = image
        self.consumable_types = consumable_types
        if top_consumable:
            self.tooltip = TooltipGraphics(self._ui_render, COLOR_WHITE, top_consumable.name,
                                           [top_consumable.description], bottom_left=self._rect.topleft)
        else:
            self.tooltip = None


class ItemIcon(UiComponent):
    def __init__(self, ui_render: DrawableArea, rect: Rect, image, tooltip: TooltipGraphics,
                 slot_equipment_category: ItemEquipmentCategory, item_type: ItemType, inventory_slot_index: int):
        super().__init__()
        self._ui_render = ui_render
        self.rect = rect
        self.image = image
        self.slot_equipment_category = slot_equipment_category
        self.tooltip = tooltip
        self.item_type = item_type
        self.inventory_slot_index = inventory_slot_index

    def get_collision_offset(self, point: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        if self.rect.collidepoint(point[0], point[1]):
            return point[0] - self.rect.x, point[1] - self.rect.y
        return None

    def render(self, highlighted: bool):
        self._ui_render.rect_filled((40, 40, 50), self.rect)
        if self.item_type:
            if self.slot_equipment_category:
                self._ui_render.rect_filled((40, 40, 70), self.rect)
            self._ui_render.image(self.image, self.rect.topleft)
        elif self.image:
            self._ui_render.image(self.image, self.rect.topleft)
        if self.item_type and self.slot_equipment_category:
            color_outline = (250, 250, 250)
        else:
            color_outline = (100, 100, 140)
        self._ui_render.rect(color_outline, self.rect, 1)

        if highlighted:
            self._ui_render.rect(COLOR_ICON_HIGHLIGHTED,
                                 Rect(self.rect.x - 1, self.rect.y - 1, self.rect.w + 1, self.rect.h + 1), 2)
        elif self.hovered:
            self._ui_render.rect(COLOR_HOVERED, self.rect, 1)


class TalentIcon(UiComponent):
    def __init__(self, ui_render: DrawableArea, rect: Rect, image, tooltip: TooltipGraphics, chosen: bool, text: str,
                 font, choice_index: int, option_index: int):
        super().__init__()
        self._ui_render = ui_render
        self._rect = rect
        self._image = image
        self._chosen = chosen
        self.tooltip = tooltip
        self._text = text
        self._font = font
        self.choice_index = choice_index
        self.option_index = option_index

    def contains(self, point: Tuple[int, int]) -> bool:
        return self._rect.collidepoint(point[0], point[1])

    def render(self):
        self._ui_render.text(self._font, self._text, (self._rect[0], self._rect[1] + self._rect[3] + 5), COLOR_WHITE)
        self._ui_render.rect_filled(COLOR_BLACK, self._rect)
        self._ui_render.image(self._image, self._rect.topleft)
        color_outline = COLOR_ICON_HIGHLIGHTED if self._chosen else COLOR_WHITE
        width_outline = 2 if self._chosen else 1
        self._ui_render.rect(color_outline, self._rect, width_outline)
        if self.hovered:
            self._ui_render.rect(COLOR_ICON_HIGHLIGHTED, self._rect, 1)


class StatBar:
    def __init__(self, ui_render: DrawableArea, rect: Rect, color: Tuple[int, int, int], tooltip: TooltipGraphics,
                 value: int, max_value: int, border: bool, show_numbers: bool, font):
        self.ui_render = ui_render
        self.rect = rect
        self.color = color
        self.border = border
        self.tooltip = tooltip
        self.show_numbers = show_numbers
        self.font = font
        self._value = value
        self._max_value = max_value
        self.ratio_filled = self._value / self._max_value

    def contains(self, point: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(point[0], point[1])

    def render(self):
        self.ui_render.stat_bar(
            self.rect.x, self.rect.y, self.rect.w, self.rect.h, self.ratio_filled, self.color, self.border)
        if self.show_numbers:
            text = str(self._value) + "/" + str(self._max_value)
            self.ui_render.text(self.font, text, (self.rect.x + 20, self.rect.y - 1))

    def update(self, value: int, max_value: int):
        self._value = value
        self._max_value = max_value
        self.ratio_filled = self._value / self._max_value


class UiWindow:
    def __init__(self):
        self.shown = False


class ToggleButton(UiComponent):
    def __init__(self, ui_render: DrawableArea, rect: Rect, font, text: str, toggle_id: ToggleButtonId,
                 highlighted: bool,
                 linked_window: UiWindow):
        super().__init__()
        self.ui_render = ui_render
        self.rect = rect
        self.font = font
        self.text = text
        self.toggle_id = toggle_id
        self.highlighted = highlighted
        self.tooltip = None
        self.is_open = False
        self.linked_window = linked_window

    def contains(self, point: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(point[0], point[1])

    def render(self):
        if self.is_open:
            self.ui_render.rect_filled((50, 50, 150), self.rect)
        self.ui_render.rect(COLOR_WHITE, self.rect, 1)
        self.ui_render.text(self.font, self.text, (self.rect.x + 20, self.rect.y + 2))
        if self.hovered:
            self.ui_render.rect(COLOR_HOVERED, self.rect, 1)
        if self.highlighted:
            self.ui_render.rect(COLOR_TOGGLE_HIGHLIGHTED, self.rect, 1)

    def open(self):
        self.is_open = True
        self.highlighted = False
        self.linked_window.shown = True

    def close(self):
        self.is_open = False
        self.linked_window.shown = False


class Checkbox(UiComponent):
    def __init__(self, ui_render: DrawableArea, rect: Rect, font, label: str, checked: bool):
        super().__init__()
        self.ui_render = ui_render
        self.rect = rect
        self.font = font
        self.label = label
        self.checked = checked
        self.tooltip = None

    def contains(self, point: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(point[0], point[1])

    def render(self):
        self.ui_render.rect(COLOR_WHITE, self.rect, 1)
        text = self.label + ": " + ("Y" if self.checked else "N")
        self.ui_render.text(self.font, text, (self.rect.x + 4, self.rect.y + 2))
        if self.hovered:
            self.ui_render.rect(COLOR_HOVERED, self.rect, 1)

    def on_click(self):
        self.checked = not self.checked


class Button(UiComponent):
    def __init__(self, ui_render: DrawableArea, rect: Rect, font, text: str):
        super().__init__()
        self.ui_render = ui_render
        self.rect = rect
        self.font = font
        self.text = text
        self.tooltip = None

    def contains(self, point: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(point[0], point[1])

    def render(self):
        self.ui_render.rect(COLOR_WHITE, self.rect, 1)
        self.ui_render.text(self.font, self.text, (self.rect.x + 7, self.rect.y + 2))
        if self.hovered:
            self.ui_render.rect(COLOR_HOVERED, self.rect, 1)


class ControlsWindow(UiWindow):
    def __init__(self, ui_render: DrawableArea, rect: Rect, font_header, font_details):
        super().__init__()
        self.ui_render = ui_render
        self.rect = rect
        self.font_header = font_header
        self.font_details = font_details

    def render(self):
        if self.shown:
            self._render()

    def _render(self):
        self.ui_render.rect_transparent(self.rect, 140, (0, 0, 30))
        self.ui_render.text(self.font_header, "CONTROLS:", (self.rect[0] + 35, self.rect[1] + 10))
        x = self.rect[0] + 15
        y_0 = self.rect[1] + 45
        self.ui_render.text(self.font_details, "Move: arrow-keys", (x, y_0))
        self.ui_render.text(self.font_details, "Abilities: Q W E R", (x, y_0 + 20))
        self.ui_render.text(self.font_details, "Potions: 1 2 3 4 5", (x, y_0 + 40))
        self.ui_render.text(self.font_details, "Interact: Space", (x, y_0 + 60))
        self.ui_render.text(self.font_details, "Inventory: mouse", (x, y_0 + 80))
        self.ui_render.text(self.font_details, "Dialog: arrow-keys", (x, y_0 + 100))


class StatsWindow(UiWindow):
    def __init__(self, ui_render: DrawableArea, rect: Rect, font_header, font_details, player_state: PlayerState,
                 player_speed_multiplier: float):
        super().__init__()
        self.ui_render = ui_render
        self.rect = rect
        self.font_header = font_header
        self.font_details = font_details
        self.player_state = player_state
        self.player_speed_multiplier = player_speed_multiplier

    def render(self):
        if self.shown:
            self._render()

    def _render(self):
        self.ui_render.rect_transparent(self.rect, 140, (0, 0, 30))

        self.ui_render.text(self.font_header, "STATS:", (self.rect[0] + 45, self.rect[1] + 10))

        health_regen_text = \
            "    health reg: " + "{:.1f}".format(self.player_state.health_resource.base_regen)
        if self.player_state.health_resource.regen_bonus > 0:
            health_regen_text += " +" + "{:.1f}".format(self.player_state.health_resource.regen_bonus)
        mana_regen_text = \
            "      mana reg: " + "{:.1f}".format(self.player_state.mana_resource.base_regen)
        if self.player_state.mana_resource.regen_bonus > 0:
            mana_regen_text += " +" + "{:.1f}".format(self.player_state.mana_resource.regen_bonus)
        physical_damage_stat_text = \
            " % phys damage: " + str(int(round(self.player_state.base_physical_damage_modifier * 100)))
        if self.player_state.physical_damage_modifier_bonus > 0:
            physical_damage_stat_text += " +" + str(int(round(self.player_state.physical_damage_modifier_bonus * 100)))
        magic_damage_stat_text = \
            "% magic damage: " + str(int(round(self.player_state.base_magic_damage_modifier * 100)))
        if self.player_state.magic_damage_modifier_bonus > 0:
            magic_damage_stat_text += " +" + str(int(round(self.player_state.magic_damage_modifier_bonus * 100)))
        speed_stat_text = \
            "       % speed: " + ("+" if self.player_speed_multiplier >= 1 else "") \
            + str(int(round((self.player_speed_multiplier - 1) * 100)))
        lifesteal_stat_text = \
            "  % life steal: " + str(int(round(self.player_state.life_steal_ratio * 100)))
        armor_stat_text = \
            "         armor: " + str(math.floor(self.player_state.base_armor))
        if self.player_state.armor_bonus > 0:
            armor_stat_text += " +" + str(self.player_state.armor_bonus)
        elif self.player_state.armor_bonus < 0:
            armor_stat_text += " " + str(self.player_state.armor_bonus)
        dodge_chance_text = \
            "       % dodge: " + str(int(round(self.player_state.base_dodge_chance * 100)))
        if self.player_state.dodge_chance_bonus > 0:
            dodge_chance_text += " +" + str(int(round(self.player_state.dodge_chance_bonus * 100)))
        block_chance_text = \
            "       % block: " + str(int(round(self.player_state.block_chance * 100)))
        block_reduction_text = \
            "  block amount: " + str(self.player_state.block_damage_reduction)
        x_text = self.rect[0] + 7
        y_0 = self.rect[1] + 45
        text_lines = [health_regen_text, mana_regen_text, physical_damage_stat_text, magic_damage_stat_text,
                      speed_stat_text, lifesteal_stat_text, armor_stat_text, dodge_chance_text, block_chance_text,
                      block_reduction_text]
        for i, y in enumerate(range(y_0, y_0 + len(text_lines) * 20, 20)):
            text = text_lines[i]
            self.ui_render.text(self.font_details, text, (x_text, y), COLOR_WHITE)


class TalentsWindow(UiWindow):
    def __init__(self, ui_render: DrawableArea, rect: Rect, font_header, font_details, talents: TalentsGraphics,
                 icon_rows: List[Tuple[TalentIcon, TalentIcon]]):
        super().__init__()
        self.ui_render = ui_render
        self.rect = rect
        self.font_header = font_header
        self.font_details = font_details
        self.talents = talents
        self.icon_rows = icon_rows

    def get_icon_containing(self, point: Tuple[int, int]) -> Optional[TalentIcon]:
        for (icon_1, icon_2) in self.icon_rows:
            if icon_1.contains(point):
                return icon_1
            if icon_2.contains(point):
                return icon_2
        return None

    def get_last_row_icons(self):
        if self.icon_rows:
            last_row = self.icon_rows[-1]
            return [last_row[0], last_row[1]]
        return []

    def render(self):
        if self.shown:
            self._render()

    def _render(self):
        self.ui_render.rect_transparent(self.rect, 140, (0, 0, 30))
        self.ui_render.text(self.font_header, "TALENTS:", (self.rect[0] + 35, self.rect[1] + 10))

        for row_index, (icon_1, icon_2) in enumerate(self.icon_rows):
            icon_1.render()
            icon_2.render()

        text_pos = self.rect[0] + 22, self.rect[1] + self.rect[3] - 26
        if self.talents.choice_graphics_items:
            player_can_choose = self.talents.choice_graphics_items[-1].chosen_index is None
            if player_can_choose:
                self.ui_render.text(self.font_details, "Choose a talent!", text_pos)
        else:
            self.ui_render.text(self.font_details, "No talents yet!", text_pos)

    def update(self, rect: Rect, talents: TalentsGraphics, icon_rows: List[Tuple[TalentIcon, TalentIcon]]):
        self.rect = rect
        self.talents = talents
        self.icon_rows = icon_rows


class ExpBar:
    def __init__(self, ui_render: DrawableArea, rect: Rect, font):
        self.ui_render = ui_render
        self.rect = rect
        self.font = font
        self.level = 1
        self.filled_ratio = 0

    def render(self):
        self.ui_render.text(self.font, "Level " + str(self.level), (self.rect.x, self.rect.y - 18))
        self.ui_render.stat_bar(self.rect.x, self.rect.y, self.rect.w, self.rect.h, self.filled_ratio, (200, 200, 200),
                                True)

    def update(self, level: int, filled_ratio: float):
        self.level = level
        self.filled_ratio = filled_ratio


class Portrait:
    def __init__(self, ui_render: DrawableArea, rect: Rect, image):
        self.ui_render = ui_render
        self.rect = rect
        self.image = image

    def render(self):
        self.ui_render.image(self.image, self.rect.topleft)
        self.ui_render.rect((160, 160, 180), self.rect, 2)


class Minimap:
    def __init__(self, ui_render: DrawableArea, rect: Rect):
        self.ui_render = ui_render
        self.rect = rect
        self.padding_rect = Rect(rect.x - 2, rect.y - 2, rect.w + 4, rect.h + 4)

    def render(self, player_relative_position: Tuple[float, float]):
        self.ui_render.rect_filled((60, 60, 80), self.padding_rect)
        self.ui_render.rect_filled((40, 40, 50), self.rect)
        self.ui_render.rect((150, 150, 190), self.rect, 1)
        dot_x = self.rect[0] + player_relative_position[0] * self.rect.w
        dot_y = self.rect[1] + player_relative_position[1] * self.rect.h
        dot_w = 4
        self.ui_render.rect_filled((100, 160, 100), Rect(dot_x - dot_w / 2, dot_y - dot_w / 2, dot_w, dot_w))


class Buffs:
    def __init__(self, ui_render: DrawableArea, font, bottomleft: Tuple[int, int]):
        self.ui_render = ui_render
        self.font = font
        self.bottomleft = bottomleft
        self.rect_padding = 5
        self.w = 140 + self.rect_padding * 2
        self.buffs = []
        h = len(self.buffs) * 25 + self.rect_padding * 2
        self.rect = Rect(self.bottomleft[0], self.bottomleft[1] - h, self.w, h)

    def render(self):
        if self.buffs:
            self.ui_render.rect_transparent(self.rect, 125, COLOR_BLACK)
            for i, (text, ratio_remaining) in enumerate(self.buffs):
                x = self.rect[0] + self.rect_padding
                y = self.rect[1] + self.rect_padding + i * 25
                self.ui_render.text(self.font, text, (x, y))
                self.ui_render.stat_bar(x, y + 20, 60, 2, ratio_remaining, (250, 250, 0), False)

    def update(self, buffs: List[Tuple[str, float]]):
        self.buffs = buffs
        h = len(self.buffs) * 25 + self.rect_padding * 2
        self.rect = Rect(self.bottomleft[0], self.bottomleft[1] - h, self.w, h)


class Text:
    def __init__(self, ui_render: DrawableArea, font, ui_position: Tuple[int, int], text: str):
        self.ui_render = ui_render
        self.font = font
        self.ui_position = ui_position
        self.text = text

    def render(self):
        self.ui_render.text(self.font, self.text, self.ui_position)


class Message:

    def __init__(self, screen_render: DrawableArea, font, center_x: int, y: int):
        self.screen_render = screen_render
        self.font = font
        self.center_x = center_x
        self.y = y

    def render(self, message: Optional[str]):
        if message:
            w = len(message) * 9 + 10
            text_x = self.center_x - w // 2
            rect = Rect(text_x - 10, self.y - 5, w, 28)
            self.screen_render.rect_transparent(rect, 135, (0, 0, 0))
            self.screen_render.text(self.font, message, (text_x, self.y))


class PausedSplashScreen:

    def __init__(self, screen_render: DrawableArea, font, rect: Rect):
        self._screen_render = screen_render
        self._font = font
        self._rect = rect
        self.shown = False

    def render(self):
        if self.shown:
            self._screen_render.rect_transparent(self._rect, 140, COLOR_BLACK)
            self._double_text("PAUSED", self._rect.w // 2 - 110, self._rect.h // 2 - 50)

    def _double_text(self, text, x, y):
        self._screen_render.text(self._font, text, (x, y), COLOR_WHITE)
        self._screen_render.text(self._font, text, (x + 2, y + 2), COLOR_BLACK)
