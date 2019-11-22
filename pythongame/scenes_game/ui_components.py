import math
from typing import List, Tuple, Optional, Any

from pygame.rect import Rect

from pythongame.core.common import ConsumableType, ItemType, AbilityType
from pythongame.core.game_data import CONSUMABLES, ConsumableCategory
from pythongame.core.game_state import PlayerState
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.talents import TalentsGraphics
from pythongame.core.view.render_util import DrawableArea
from pythongame.scenes_game.game_ui_state import UiToggle

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (250, 250, 250)

COLOR_HOVERED = (200, 200, 250)
COLOR_ICON_HIGHLIGHTED = (250, 250, 150)
COLOR_TOGGLE_HIGHLIGHTED = (150, 250, 200)


class TooltipGraphics:
    def __init__(self, title_color: Tuple[int, int, int], title: str, details: List[str],
                 bottom_left: Optional[Tuple[int, int]] = None, bottom_right: Optional[Tuple[int, int]] = None):
        self.title_color = title_color
        self.title = title
        self.details = details
        self.bottom_left_corner: Optional[Tuple[int, int]] = bottom_left
        self.bottom_right_corner: Optional[Tuple[int, int]] = bottom_right


class AbilityIcon:
    def __init__(self, ui_render: DrawableArea, rect: Rect, image, label: str, font, tooltip: TooltipGraphics,
                 ability_type: AbilityType):
        self._ui_render = ui_render
        self._rect = rect
        self._image = image
        self._label = label
        self._font = font
        self.tooltip = tooltip
        self.ability_type = ability_type

    def contains(self, point: Tuple[int, int]) -> bool:
        return self._rect.collidepoint(point[0], point[1])

    def render(self, hovered: bool, recently_clicked: bool, cooldown_remaining_ratio: float):
        self._ui_render.rect_filled((40, 40, 50), self._rect)
        self._ui_render.image(self._image, self._rect.topleft)
        self._ui_render.rect((150, 150, 190), self._rect, 1)
        if recently_clicked:
            self._ui_render.rect(COLOR_ICON_HIGHLIGHTED,
                                 Rect(self._rect.x - 1, self._rect.y - 1, self._rect.w + 2, self._rect.h + 2), 3)
        elif hovered:
            self._ui_render.rect(COLOR_HOVERED, self._rect, 1)
        self._ui_render.text(self._font, self._label, (self._rect.x + 12, self._rect.y + self._rect.h + 4))

        if cooldown_remaining_ratio > 0:
            cooldown_rect = Rect(self._rect.x + 1,
                                 self._rect.y + 1 + (self._rect.h - 2) * (1 - cooldown_remaining_ratio),
                                 self._rect.w - 2,
                                 (self._rect.h - 2) * cooldown_remaining_ratio + 1)
            self._ui_render.rect_filled((100, 30, 30), cooldown_rect)
            self._ui_render.rect((180, 30, 30), self._rect, 2)


class ConsumableIcon:
    def __init__(self, ui_render: DrawableArea, rect: Rect, image, label: str, font, tooltip: TooltipGraphics,
                 consumable_types: List[ConsumableType], slot_number: int):
        self._ui_render = ui_render
        self._rect = rect
        self._image = image
        self._label = label
        self._font = font
        self._consumable_types = consumable_types
        self.tooltip = tooltip
        self.slot_number = slot_number

    def contains(self, point: Tuple[int, int]) -> bool:
        return self._rect.collidepoint(point[0], point[1])

    def render(self, hovered: bool, recently_clicked: bool):
        self._ui_render.rect_filled((40, 40, 50), self._rect)
        if self._image:
            self._ui_render.image(self._image, self._rect.topleft)
        self._ui_render.rect((150, 150, 190), self._rect, 1)

        sub_rect_h = 3
        for i in range(len(self._consumable_types)):
            sub_consumable_type = self._consumable_types[i]
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
        elif hovered:
            self._ui_render.rect(COLOR_HOVERED, self._rect, 1)
        self._ui_render.text(self._font, self._label, (self._rect.x + 12, self._rect.y + self._rect.h + 4))


class ItemIcon:
    def __init__(self, ui_render: DrawableArea, rect: Rect, image, tooltip: TooltipGraphics,
                 slot_equipment_category: ItemEquipmentCategory, item_type: ItemType, inventory_slot_index: int):
        self._ui_render = ui_render
        self._rect = rect
        self._image = image
        self.slot_equipment_category = slot_equipment_category
        self.tooltip = tooltip
        self.item_type = item_type
        self.inventory_slot_index = inventory_slot_index

    def contains(self, point: Tuple[int, int]) -> bool:
        return self._rect.collidepoint(point[0], point[1])

    def render(self, hovered: bool, highlighted: bool):
        self._ui_render.rect_filled((40, 40, 50), self._rect)
        if self.item_type:
            if self.slot_equipment_category:
                self._ui_render.rect_filled((40, 40, 70), self._rect)
            self._ui_render.image(self._image, self._rect.topleft)
        elif self._image:
            self._ui_render.image(self._image, self._rect.topleft)
        if self.item_type and self.slot_equipment_category:
            color_outline = (250, 250, 250)
        else:
            color_outline = (100, 100, 140)
        self._ui_render.rect(color_outline, self._rect, 1)

        if highlighted:
            self._ui_render.rect(COLOR_ICON_HIGHLIGHTED,
                                 Rect(self._rect.x - 1, self._rect.y - 1, self._rect.w + 1, self._rect.h + 1), 2)
        elif hovered:
            self._ui_render.rect(COLOR_HOVERED, self._rect, 1)


class TalentIcon:
    def __init__(self, ui_render: DrawableArea, rect: Rect, image, tooltip: TooltipGraphics, chosen: bool, text: str,
                 font, choice_index: int, option_index: int):
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

    def render(self, hovered: bool):
        self._ui_render.text(self._font, self._text, (self._rect[0], self._rect[1] + self._rect[3] + 5), COLOR_WHITE)
        self._ui_render.rect_filled(COLOR_BLACK, self._rect)
        self._ui_render.image(self._image, self._rect.topleft)
        color_outline = COLOR_ICON_HIGHLIGHTED if self._chosen else COLOR_WHITE
        width_outline = 2 if self._chosen else 1
        self._ui_render.rect(color_outline, self._rect, width_outline)
        if hovered:
            self._ui_render.rect(COLOR_ICON_HIGHLIGHTED, self._rect, 1)


class StatBar:
    def __init__(self, ui_render: DrawableArea, rect: Rect, color: Tuple[int, int, int], tooltip: TooltipGraphics,
                 border: bool, show_numbers: bool, font):
        self.ui_render = ui_render
        self.rect = rect
        self.color = color
        self.border = border
        self.tooltip = tooltip
        self.show_numbers = show_numbers
        self.font = font

    def contains(self, point: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(point[0], point[1])

    def render(self, value: int, max_value: int):
        self.ui_render.stat_bar(self.rect.x, self.rect.y, self.rect.w, self.rect.h, value / max_value, self.color,
                                self.border)
        if self.show_numbers:
            text = str(value) + "/" + str(max_value)
            self.ui_render.text(self.font, text, (self.rect.x + 20, self.rect.y - 1))


class ToggleButton:
    def __init__(self, ui_render: DrawableArea, rect: Rect, font, text: str, toggle_id: UiToggle, highlighted: bool):
        self.ui_render = ui_render
        self.rect = rect
        self.font = font
        self.text = text
        self.toggle_id = toggle_id
        self.highlighted = highlighted
        self.tooltip = None

    def contains(self, point: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(point[0], point[1])

    def render(self, enabled: bool, hovered: bool):
        if enabled:
            self.ui_render.rect_filled((50, 50, 150), self.rect)
        self.ui_render.rect(COLOR_WHITE, self.rect, 1)
        self.ui_render.text(self.font, self.text, (self.rect.x + 20, self.rect.y + 2))
        if hovered:
            self.ui_render.rect(COLOR_HOVERED, self.rect, 1)
        if self.highlighted:
            self.ui_render.rect(COLOR_TOGGLE_HIGHLIGHTED, self.rect, 1)


class ControlsWindow:
    def __init__(self, ui_render: DrawableArea, rect: Rect, font_header, font_details):
        self.ui_render = ui_render
        self.rect = rect
        self.font_header = font_header
        self.font_details = font_details

    def render(self):
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


class StatsWindow:
    def __init__(self, ui_render: DrawableArea, rect: Rect, font_header, font_details, player_state: PlayerState,
                 player_speed_multiplier: float):
        self.ui_render = ui_render
        self.rect = rect
        self.font_header = font_header
        self.font_details = font_details
        self.player_state = player_state
        self.player_speed_multiplier = player_speed_multiplier

    def render(self):
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


class TalentsWindow:
    def __init__(self, ui_render: DrawableArea, rect: Rect, font_header, font_details, talents: TalentsGraphics,
                 icon_rows: List[Tuple[TalentIcon, TalentIcon]]):
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

    def render(self, hovered_component: Optional[Any]):
        self.ui_render.rect_transparent(self.rect, 140, (0, 0, 30))
        self.ui_render.text(self.font_header, "TALENTS:", (self.rect[0] + 35, self.rect[1] + 10))

        for row_index, (icon_1, icon_2) in enumerate(self.icon_rows):
            icon_1.render(icon_1 == hovered_component)
            icon_2.render(icon_2 == hovered_component)

        text_pos = self.rect[0] + 22, self.rect[1] + self.rect[3] - 26
        if self.talents.choice_graphics_items:
            player_can_choose = self.talents.choice_graphics_items[-1].chosen_index is None
            if player_can_choose:
                self.ui_render.text(self.font_details, "Choose a talent!", text_pos)
        else:
            self.ui_render.text(self.font_details, "No talents yet!", text_pos)
