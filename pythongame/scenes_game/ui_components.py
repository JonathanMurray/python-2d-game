from typing import List, Tuple, Optional

from pygame.rect import Rect

from pythongame.core.common import ConsumableType, ItemType, AbilityType
from pythongame.core.game_data import CONSUMABLES, ConsumableCategory
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.render_util import DrawableArea
from pythongame.scenes_game.game_ui_state import UiToggle

COLOR_HOVERED = (200, 200, 250)
COLOR_WHITE = (250, 250, 250)
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
        self._slot_equipment_category = slot_equipment_category
        self.tooltip = tooltip
        self.item_type = item_type
        self.inventory_slot_index = inventory_slot_index

    def contains(self, point: Tuple[int, int]) -> bool:
        return self._rect.collidepoint(point[0], point[1])

    def render(self, hovered: bool):
        self._ui_render.rect_filled((40, 40, 50), self._rect)
        if self.item_type:
            if self._slot_equipment_category:
                self._ui_render.rect_filled((40, 40, 70), self._rect)
            self._ui_render.image(self._image, self._rect.topleft)
        elif self._image:
            self._ui_render.image(self._image, self._rect.topleft)
        if self.item_type and self._slot_equipment_category:
            color_outline = (250, 250, 250)
        else:
            color_outline = (100, 100, 140)
        self._ui_render.rect(color_outline, self._rect, 1)
        if hovered:
            self._ui_render.rect(COLOR_HOVERED, self._rect, 1)


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
