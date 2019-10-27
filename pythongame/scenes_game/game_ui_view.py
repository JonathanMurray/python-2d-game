from typing import List, Tuple, Optional

import pygame
from pygame.rect import Rect

from pythongame.core.common import ConsumableType, ItemType, HeroId, UiIconSprite
from pythongame.core.game_data import ABILITIES, BUFF_TEXTS, \
    KEYS_BY_ABILITY_TYPE, CONSUMABLES, ITEMS, HEROES, ConsumableCategory
from pythongame.core.game_state import PlayerState
from pythongame.core.item_inventory import ItemInventorySlot, ItemEquipmentCategory, ITEM_EQUIPMENT_CATEGORY_NAMES
from pythongame.core.math import is_point_in_rect
from pythongame.core.npc_behaviors import DialogGraphics
from pythongame.core.talents import TalentsGraphics
from pythongame.core.view.render_util import DrawableArea, split_text_into_lines
from pythongame.scenes_game.game_ui_state import GameUiState, UiToggle

COLOR_WHITE = (250, 250, 250)
COLOR_BLACK = (0, 0, 0)
COLOR_HIGHLIGHTED_ICON = (250, 250, 150)
COLOR_HOVERED_ICON_HIGHLIGHT = (200, 200, 250)
COLOR_HIGHLIGHT_HAS_UNSEEN = (150, 250, 200)
COLOR_BORDER = (139, 69, 19)
COLOR_ITEM_TOOLTIP_HEADER = (250, 250, 150)
UI_ICON_SIZE = (32, 32)
PORTRAIT_ICON_SIZE = (100, 70)

RENDER_WORLD_COORDINATES = False

DIR_FONTS = './resources/fonts/'


class MouseHoverEvent:
    def __init__(self, item_slot_number: Optional[int], consumable_slot_number: Optional[int],
                 is_over_ui: bool, ui_toggle: Optional[UiToggle],
                 talent_choice_option: Optional[Tuple[int, int]]):
        self.item_slot_number = item_slot_number
        self.consumable_slot_number = consumable_slot_number
        self.is_over_ui: bool = is_over_ui
        self.ui_toggle = ui_toggle
        self.talent_choice_option = talent_choice_option  # (choice_index, option_index)


class TooltipGraphics:
    def __init__(self, title_color: Tuple[int, int, int], title: str, details: List[str],
                 bottom_left: Optional[Tuple[int, int]] = None, bottom_right: Optional[Tuple[int, int]] = None):
        self.title_color = title_color
        self.title = title
        self.details = details
        self.bottom_left_corner: Optional[Tuple[int, int]] = bottom_left
        self.bottom_right_corner: Optional[Tuple[int, int]] = bottom_right


class GameUiView:

    def __init__(self, pygame_screen, camera_size: Tuple[int, int], screen_size: Tuple[int, int],
                 images_by_ui_sprite, images_by_portrait_sprite):
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
        self.images_by_portrait_sprite = images_by_portrait_sprite

        # This is updated every time the view is called
        self.camera_world_area = None

    def _translate_ui_position_to_screen(self, position):
        return position[0] + self.ui_screen_area.x, position[1] + self.ui_screen_area.y

    def _translate_screen_position_to_ui(self, position: Tuple[int, int]):
        return position[0] - self.ui_screen_area.x, position[1] - self.ui_screen_area.y

    def _consumable_icon_in_ui(self, x, y, size, consumable_number: int, consumable_types: List[ConsumableType],
                               weak_highlight: bool, strong_highlight: bool):
        w = size[0]
        h = size[1]
        self.ui_render.rect_filled((40, 40, 50), Rect(x, y, w, h))
        if consumable_types:
            icon_sprite = CONSUMABLES[consumable_types[0]].icon_sprite
            self.ui_render.image(self.images_by_ui_sprite[icon_sprite], (x, y))
        self.ui_render.rect((150, 150, 190), Rect(x, y, w, h), 1)
        # Render any consumables that are deeper down in the inventory
        sub_rect_h = 3
        for i in range(len(consumable_types)):
            sub_consumable_type = consumable_types[i]
            consumable_category = CONSUMABLES[sub_consumable_type].category
            if consumable_category == ConsumableCategory.HEALTH:
                sub_rect_color = (160, 110, 110)
            elif consumable_category == ConsumableCategory.MANA:
                sub_rect_color = (110, 110, 200)
            else:
                sub_rect_color = (170, 170, 170)
            self.ui_render.rect_filled(
                sub_rect_color, Rect(x, y - 2 - (sub_rect_h + 1) * (i + 1), w, sub_rect_h))

        if strong_highlight:
            self.ui_render.rect(COLOR_HIGHLIGHTED_ICON, Rect(x - 1, y - 1, w + 2, h + 2), 3)
        elif weak_highlight:
            self.ui_render.rect(COLOR_HOVERED_ICON_HIGHLIGHT, Rect(x, y, w, h), 1)

        self.ui_render.text(self.font_ui_icon_keys, str(consumable_number), (x + 12, y + h + 4))

    def _ability_icon_in_ui(self, x, y, size, ability_type, weak_highlight: bool, strong_highlight: bool,
                            ability_cooldowns_remaining):
        w = size[0]
        h = size[1]
        ability = ABILITIES[ability_type]
        ability_key = KEYS_BY_ABILITY_TYPE[ability_type]
        icon_sprite = ability.icon_sprite
        icon_rect = Rect(x, y, w, h)
        self.ui_render.rect_filled((40, 40, 50), icon_rect)
        self.ui_render.image(self.images_by_ui_sprite[icon_sprite], (x, y))
        self.ui_render.rect((150, 150, 190), icon_rect, 1)
        if strong_highlight:
            self.ui_render.rect(COLOR_HIGHLIGHTED_ICON, Rect(x - 1, y - 1, w + 2, h + 2), 3)
        elif weak_highlight:
            self.ui_render.rect(COLOR_HOVERED_ICON_HIGHLIGHT, Rect(x, y, w, h), 1)
        self.ui_render.text(self.font_ui_icon_keys, ability_key.key_string, (x + 12, y + h + 4))

        if ability_cooldowns_remaining[ability_type] > 0:
            ratio_remaining = ability_cooldowns_remaining[ability_type] / ability.cooldown
            cooldown_rect = Rect(x + 1, y + 1 + (h - 2) * (1 - ratio_remaining), w - 2, (h - 2) * ratio_remaining + 1)
            self.ui_render.rect_filled((100, 30, 30), cooldown_rect)
            self.ui_render.rect((180, 30, 30), icon_rect, 2)

    def _item_icon_in_ui(self, x, y, size, item_type: ItemType, slot_equipment_category: ItemEquipmentCategory,
                         highlight: bool):
        w = size[0]
        h = size[1]
        rect = Rect(x, y, w, h)
        self.ui_render.rect_filled((40, 40, 50), rect)
        if item_type:
            if slot_equipment_category:
                self.ui_render.rect_filled((40, 40, 70), rect)
            ui_icon_sprite = ITEMS[item_type].icon_sprite
            self.ui_render.image(self.images_by_ui_sprite[ui_icon_sprite], (x, y))
        elif slot_equipment_category:
            image = self._get_image_for_item_category(slot_equipment_category)
            self.ui_render.image(image, (x, y))
        if item_type and slot_equipment_category:
            color_outline = (250, 250, 250)
        else:
            color_outline = (100, 100, 140)
        self.ui_render.rect(color_outline, rect, 1)
        if highlight:
            self.ui_render.rect(COLOR_HOVERED_ICON_HIGHLIGHT, rect, 1)

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

    def _minimap_in_ui(self, position_in_ui, size, player_relative_position):
        rect = Rect(position_in_ui[0], position_in_ui[1], size[0], size[1])
        self.ui_render.rect_filled((40, 40, 50), rect)
        self.ui_render.rect((150, 150, 190), rect, 1)
        dot_x = rect[0] + player_relative_position[0] * size[0]
        dot_y = rect[1] + player_relative_position[1] * size[1]
        dot_w = 4
        self.ui_render.rect_filled((100, 160, 100), Rect(dot_x - dot_w / 2, dot_y - dot_w / 2, dot_w, dot_w))

    def _message(self, message):
        w_rect = len(message) * 9 + 10
        x_message = self.ui_screen_area.w / 2 - w_rect / 2
        y_message = self.ui_screen_area.y - 30
        self.screen_render.rect_transparent(Rect(x_message - 10, y_message - 5, w_rect, 28), 135, (0, 0, 0))
        self.screen_render.text(self.font_message, message, (x_message, y_message))

    def _tooltip(self, tooltip: TooltipGraphics):

        detail_lines = []
        detail_max_line_length = 32
        for detail in tooltip.details:
            detail_lines += split_text_into_lines(detail, detail_max_line_length)

        w_tooltip = 260
        h_tooltip = 60 + 17 * len(detail_lines)
        if tooltip.bottom_left_corner is not None:
            bottom_left_corner = tooltip.bottom_left_corner
        else:
            bottom_left_corner = (tooltip.bottom_right_corner[0] - w_tooltip, tooltip.bottom_right_corner[1])
        x_tooltip = bottom_left_corner[0]
        y_tooltip = bottom_left_corner[1] - h_tooltip - 3
        rect_tooltip = Rect(x_tooltip, y_tooltip, w_tooltip, h_tooltip)
        self.ui_render.rect_transparent(Rect(x_tooltip, y_tooltip, w_tooltip, h_tooltip), 200, (0, 0, 30))
        self.ui_render.rect(COLOR_WHITE, rect_tooltip, 1)
        self.ui_render.text(self.font_tooltip_header, tooltip.title, (x_tooltip + 20, y_tooltip + 15),
                            tooltip.title_color)
        y_separator = y_tooltip + 40
        self.ui_render.line(COLOR_WHITE, (x_tooltip + 10, y_separator), (x_tooltip + w_tooltip - 10, y_separator),
                            1)

        for i, line in enumerate(detail_lines):
            self.ui_render.text(self.font_tooltip_details, line, (x_tooltip + 20, y_tooltip + 50 + i * 18),
                                COLOR_WHITE)

    def _toggle_in_ui(self, x: int, y: int, text: str, enabled: bool, mouse_ui_position: Tuple[int, int],
                      highlight: bool) -> bool:
        rect = Rect(x, y, 120, 20)
        if enabled:
            self.ui_render.rect_filled((50, 50, 150), rect)
        self.ui_render.rect(COLOR_WHITE, rect, 1)
        self.ui_render.text(self.font_tooltip_details, text, (x + 20, y + 2))
        is_hovered_by_mouse = is_point_in_rect(mouse_ui_position, rect)
        if is_hovered_by_mouse:
            self.ui_render.rect(COLOR_HOVERED_ICON_HIGHLIGHT, rect, 1)
        if highlight:
            self.ui_render.rect(COLOR_HIGHLIGHT_HAS_UNSEEN, rect, 1)
        return is_hovered_by_mouse

    def _render_stats(self, player_speed_multiplier: float, player_state: PlayerState, ui_position: Tuple[int, int]):

        rect_container = Rect(ui_position[0], ui_position[1], 140, 170)
        self.ui_render.rect_transparent(rect_container, 140, (0, 0, 30))

        self.ui_render.text(self.font_tooltip_details, "STATS:", (ui_position[0] + 45, ui_position[1] + 10))

        player_life_steal = player_state.life_steal_ratio
        health_regen_text = \
            "  health reg: " + "{:.1f}".format(player_state.health_resource.base_regen)
        if player_state.health_resource.regen_bonus > 0:
            health_regen_text += " +" + "{:.1f}".format(player_state.health_resource.regen_bonus)
        mana_regen_text = \
            "    mana reg: " + "{:.1f}".format(player_state.mana_resource.base_regen)
        if player_state.mana_resource.regen_bonus > 0:
            mana_regen_text += " +" + "{:.1f}".format(player_state.mana_resource.regen_bonus)
        damage_stat_text = \
            "    % damage: " + str(int(round(player_state.base_damage_modifier * 100)))
        if player_state.damage_modifier_bonus > 0:
            damage_stat_text += " +" + str(int(round(player_state.damage_modifier_bonus * 100)))
        speed_stat_text = \
            "     % speed: " + ("+" if player_speed_multiplier >= 1 else "") \
            + str(int(round((player_speed_multiplier - 1) * 100)))
        lifesteal_stat_text = \
            "% life steal: " + str(int(round(player_life_steal * 100)))
        armor_stat_text = \
            "       armor: " + str(player_state.base_armor)
        if player_state.armor_bonus > 0:
            armor_stat_text += " +" + str(player_state.armor_bonus)
        elif player_state.armor_bonus < 0:
            armor_stat_text += " " + str(player_state.armor_bonus)
        x_text = ui_position[0] + 7
        y_0 = ui_position[1] + 45
        self.ui_render.text(self.font_stats, health_regen_text, (x_text, y_0), COLOR_WHITE)
        self.ui_render.text(self.font_stats, mana_regen_text, (x_text, y_0 + 20), COLOR_WHITE)
        self.ui_render.text(self.font_stats, damage_stat_text, (x_text, y_0 + 40), COLOR_WHITE)
        self.ui_render.text(self.font_stats, speed_stat_text, (x_text, y_0 + 60), COLOR_WHITE)
        self.ui_render.text(self.font_stats, lifesteal_stat_text, (x_text, y_0 + 80), COLOR_WHITE)
        self.ui_render.text(self.font_stats, armor_stat_text, (x_text, y_0 + 100), COLOR_WHITE)

    def _render_talents(self, talents: TalentsGraphics, ui_position: Tuple[int, int],
                        mouse_ui_position: Tuple[int, int]) -> Tuple[
        Optional[Tuple[int, int]], Optional[TooltipGraphics]]:

        tooltip_graphics: TooltipGraphics = None
        hovered_talent_option = None

        rect_container = Rect(ui_position[0], ui_position[1], 140, 260)
        self.ui_render.rect_transparent(rect_container, 140, (0, 0, 30))

        self.ui_render.text(self.font_tooltip_details, "TALENTS:", (ui_position[0] + 35, ui_position[1] + 10))

        x_text = ui_position[0] + 22
        y_0 = ui_position[1] + 35
        for i, choice_graphics in enumerate(talents.choice_graphics_items):
            y = y_0 + i * (UI_ICON_SIZE[1] + 30)
            y_icon = y + 3
            choice = choice_graphics.choice
            self.ui_render.text(self.font_stats, choice.first.name, (x_text, y_icon + UI_ICON_SIZE[1] + 5), COLOR_WHITE)
            self.ui_render.text(self.font_stats, choice.second.name, (x_text + 60, y_icon + UI_ICON_SIZE[1] + 5),
                                COLOR_WHITE)
            is_mouse_hovering_first = self._render_talent_icon(
                choice.first.ui_icon_sprite, (x_text, y_icon), choice_graphics.chosen_index == 0, mouse_ui_position)
            is_mouse_hovering_second = self._render_talent_icon(
                choice.second.ui_icon_sprite, (x_text + 60, y_icon), choice_graphics.chosen_index == 1,
                mouse_ui_position)

            if is_mouse_hovering_first:
                hovered_talent_option = (i, 0)
                tooltip_graphics = TooltipGraphics(
                    COLOR_WHITE, choice.first.name, [choice.first.description],
                    bottom_right=(x_text + UI_ICON_SIZE[0], y_icon))
            elif is_mouse_hovering_second:
                hovered_talent_option = (i, 1)
                tooltip_graphics = TooltipGraphics(
                    COLOR_WHITE, choice.second.name, [choice.second.description],
                    bottom_right=(x_text + UI_ICON_SIZE[0] + 60, y_icon))

        y_bot_text = rect_container[1] + rect_container[3] - 26

        if talents.choice_graphics_items:
            player_can_choose = talents.choice_graphics_items[-1].chosen_index is None
            if player_can_choose:
                self.ui_render.text(self.font_stats, "Choose a talent!", (x_text, y_bot_text))
        else:
            self.ui_render.text(self.font_stats, "No talents yet!", (x_text, y_bot_text))

        return hovered_talent_option, tooltip_graphics

    def _render_controls(self, ui_position: Tuple[int, int]):

        rect_container = Rect(ui_position[0], ui_position[1], 140, 170)
        self.ui_render.rect_transparent(rect_container, 140, (0, 0, 30))

        self.ui_render.text(self.font_tooltip_details, "CONTROLS:", (ui_position[0] + 35, ui_position[1] + 10))
        x_text = ui_position[0] + 15
        y_0 = ui_position[1] + 45
        self.ui_render.text(self.font_stats, "Move: arrow-keys", (x_text, y_0))
        self.ui_render.text(self.font_stats, "Abilities: Q W E R", (x_text, y_0 + 20))
        self.ui_render.text(self.font_stats, "Potions: 1 2 3 4 5", (x_text, y_0 + 40))
        self.ui_render.text(self.font_stats, "Interact: Space", (x_text, y_0 + 60))
        self.ui_render.text(self.font_stats, "Inventory: mouse", (x_text, y_0 + 80))
        self.ui_render.text(self.font_stats, "Dialog: arrow-keys", (x_text, y_0 + 100))

    def _render_talent_icon(self, ui_icon_sprite: UiIconSprite, position: Tuple[int, int], chosen: bool,
                            mouse_ui_position: Tuple[int, int]) -> bool:
        rect = Rect(position[0], position[1], UI_ICON_SIZE[0], UI_ICON_SIZE[1])
        self.ui_render.rect_filled(COLOR_BLACK, rect)
        image = self.images_by_ui_sprite[ui_icon_sprite]
        self.ui_render.image(image, position)
        color_outline = COLOR_HIGHLIGHTED_ICON if chosen else COLOR_WHITE
        width_outline = 2 if chosen else 1
        self.ui_render.rect(color_outline, rect, width_outline)
        is_hovered_by_mouse = is_point_in_rect(mouse_ui_position, rect)
        if is_hovered_by_mouse:
            self.ui_render.rect(COLOR_HOVERED_ICON_HIGHLIGHT, rect, 1)
        return is_hovered_by_mouse

    def _player_portrait(self, hero_id: HeroId, ui_position: Tuple[int, int]):
        portrait_sprite = HEROES[hero_id].portrait_icon_sprite
        player_portrait_image = self.images_by_portrait_sprite[portrait_sprite]
        self.ui_render.image(player_portrait_image, ui_position)
        rect = Rect(ui_position[0], ui_position[1], PORTRAIT_ICON_SIZE[0], PORTRAIT_ICON_SIZE[1])
        self.ui_render.rect((160, 160, 180), rect, 2)

    def _dialog(self, dialog_graphics: DialogGraphics):

        tall_detail_section = any(
            [o.detail_body is not None or o.detail_header is not None or o.detail_ui_icon_sprite is not None
             for o in dialog_graphics.options])

        h_detail_section_expansion = 82

        options_margin = 10
        option_padding = 4
        h_option_line = 20
        if tall_detail_section:
            h_dialog_container = 310 + len(dialog_graphics.options) * (h_option_line + 2 * option_padding)
        else:
            h_dialog_container = 310 + len(dialog_graphics.options) * (h_option_line + 2 * option_padding) \
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
        dialog_image = self.images_by_portrait_sprite[dialog_graphics.portrait_icon_sprite]
        self.screen_render.image(dialog_image, rect_portrait_pos)
        rect_portrait = Rect(rect_portrait_pos[0], rect_portrait_pos[1], PORTRAIT_ICON_SIZE[0], PORTRAIT_ICON_SIZE[1])
        self.screen_render.rect((160, 160, 180), rect_portrait, 2)

        dialog_pos = (x_left + 120, rect_dialog_container[1] + 15)
        dialog_lines = split_text_into_lines(dialog_graphics.text_body, 35)
        for i, dialog_text_line in enumerate(dialog_lines):
            if i == 6:
                print("WARN: too long dialog for NPC!")
                break
            self.screen_render.text(self.font_dialog, dialog_text_line, (dialog_pos[0] + 5, dialog_pos[1] + 32 * i),
                                    COLOR_WHITE)

        y_above_options = dialog_pos[1] + 150
        self.screen_render.line(color_separator, (x_left, y_above_options), (x_right, y_above_options), 2)

        for i, option in enumerate(dialog_graphics.options):
            x_option = x_left + 8
            y_option = y_above_options + options_margin + i * (h_option_line + 2 * option_padding)
            x_option_text = x_option + option_padding + 5
            y_option_text = y_option + option_padding + 2
            color_highlight = COLOR_WHITE

            is_option_active = dialog_graphics.active_option_index == i
            color_option_text = COLOR_WHITE if is_option_active else (160, 160, 160)
            if is_option_active:
                rect_highlight_active_option = Rect(
                    x_option, y_option, rect_dialog_container[2] - 16, h_option_line + 2 * option_padding)
                self.screen_render.rect_transparent(rect_highlight_active_option, 120, COLOR_WHITE)
                self.screen_render.rect(color_highlight, rect_highlight_active_option, 1)
            self.screen_render.text(self.font_dialog, option.summary, (x_option_text, y_option_text), color_option_text)

        active_option = dialog_graphics.options[dialog_graphics.active_option_index]
        y_under_options = y_above_options + 2 * options_margin \
                          + len(dialog_graphics.options) * (h_option_line + 2 * option_padding)
        self.screen_render.line(color_separator, (x_left, y_under_options), (x_right, y_under_options), 2)

        if tall_detail_section:
            y_action_text = y_under_options + 15 + h_detail_section_expansion
        else:
            y_action_text = y_under_options + 15

        if tall_detail_section:
            if active_option.detail_ui_icon_sprite is not None:
                active_option_image = self.images_by_ui_sprite[active_option.detail_ui_icon_sprite]
                pos_option_image = x_left + 6, y_under_options + 7
                self.screen_render.image(active_option_image, pos_option_image)
                rect_option_image = Rect(pos_option_image[0], pos_option_image[1], UI_ICON_SIZE[0], UI_ICON_SIZE[1])
                self.screen_render.rect((150, 150, 150), rect_option_image, 1)
            if active_option.detail_header is not None:
                self.screen_render.text(self.font_dialog, active_option.detail_header,
                                        (x_left + 14 + UI_ICON_SIZE[0] + 4, y_action_text - h_detail_section_expansion))
            if active_option.detail_body is not None:
                detail_body_lines = split_text_into_lines(active_option.detail_body, 70)
                for i, line in enumerate(detail_body_lines):
                    line_pos = (x_left + 10, y_action_text - h_detail_section_expansion + 35 + 20 * i)
                    self.screen_render.text(self.font_dialog_option_detail_body, line, line_pos)
        action_text = active_option.detail_action_text
        self.screen_render.text(self.font_dialog, "[Space] : " + action_text, (x_left + 10, y_action_text))

    def render_item_being_dragged(self, item_type: ItemType, mouse_screen_position: Tuple[int, int]):
        ui_icon_sprite = ITEMS[item_type].icon_sprite
        position = (mouse_screen_position[0] - UI_ICON_SIZE[0] // 2, mouse_screen_position[1] - UI_ICON_SIZE[1] // 2)
        self.screen_render.image(self.images_by_ui_sprite[ui_icon_sprite], position)

    def render_consumable_being_dragged(self, consumable_type: ConsumableType, mouse_screen_position: Tuple[int, int]):
        ui_icon_sprite = CONSUMABLES[consumable_type].icon_sprite
        position = (mouse_screen_position[0] - UI_ICON_SIZE[0] // 2, mouse_screen_position[1] - UI_ICON_SIZE[1] // 2)
        self.screen_render.image(self.images_by_ui_sprite[ui_icon_sprite], position)

    def _splash_screen_text(self, text, x, y):
        self.screen_render.text(self.font_splash_screen, text, (x, y), COLOR_WHITE)
        self.screen_render.text(self.font_splash_screen, text, (x + 2, y + 2), COLOR_BLACK)

    def render_ui(
            self,
            player_state: PlayerState,
            ui_state: GameUiState,
            fps_string: str,
            is_paused: bool,
            player_speed_multiplier: float,
            mouse_screen_position: Tuple[int, int],
            dialog: Optional[DialogGraphics],
            talents: TalentsGraphics) -> MouseHoverEvent:

        player_health = player_state.health_resource.value
        player_max_health = player_state.health_resource.max_value
        player_max_mana = player_state.mana_resource.max_value
        player_mana = player_state.mana_resource.value
        player_active_buffs = player_state.active_buffs
        consumable_slots = player_state.consumable_inventory.consumables_in_slots
        ability_cooldowns_remaining = player_state.ability_cooldowns_remaining
        abilities = player_state.abilities
        item_slots: List[ItemInventorySlot] = player_state.item_inventory.slots
        player_exp = player_state.exp
        player_max_exp_in_this_level = player_state.max_exp_in_this_level
        player_level = player_state.level
        player_money = player_state.money
        hero_id = player_state.hero_id

        player_minimap_relative_position = ui_state.player_minimap_relative_position
        message = ui_state.message
        highlighted_consumable_action = ui_state.highlighted_consumable_action
        highlighted_ability_action = ui_state.highlighted_ability_action

        hovered_item_slot_number = None
        hovered_consumable_slot_number = None
        hovered_ui_toggle = None
        hovered_talent_option: Optional[Tuple[int, int]] = None
        is_mouse_hovering_ui = is_point_in_rect(mouse_screen_position, self.ui_screen_area)

        mouse_ui_position = self._translate_screen_position_to_ui(mouse_screen_position)
        tooltip: Optional[TooltipGraphics] = None
        self.screen_render.rect(COLOR_BORDER, Rect(0, 0, self.camera_size[0], self.camera_size[1]), 1)
        self.screen_render.rect_filled((20, 10, 0), Rect(0, self.camera_size[1], self.screen_size[0],
                                                         self.screen_size[1] - self.camera_size[1]))

        y_0 = 5

        y_1 = 30
        y_2 = y_1 + 22
        y_3 = 90
        y_4 = y_3 + 22

        x_1 = 140

        x_exp_bar = x_1
        self.ui_render.text(self.font_level, "Level " + str(player_level), (x_exp_bar, y_0))
        self.ui_render.stat_bar(x_exp_bar, y_0 + 18, 380, 2, player_exp / player_max_exp_in_this_level,
                                (200, 200, 200),
                                True)

        x_0 = 20

        self._player_portrait(hero_id, (x_0, y_0 + 13))

        rect_healthbar = Rect(x_0, y_4 - 1, 100, 14)
        self.ui_render.stat_bar(rect_healthbar[0], rect_healthbar[1], rect_healthbar[2], rect_healthbar[3],
                                player_health / player_max_health, (200, 0, 50), True)
        if is_point_in_rect(mouse_ui_position, rect_healthbar):
            tooltip_details = [
                "regeneration: " + "{:.1f}".format(player_state.health_resource.get_effective_regen()) + "/s"]
            tooltip_bottom_left_position = (rect_healthbar[0], rect_healthbar[1])
            tooltip = TooltipGraphics(COLOR_WHITE, "Health", tooltip_details, bottom_left=tooltip_bottom_left_position)
        health_text = str(player_health) + "/" + str(player_max_health)
        self.ui_render.text(self.font_ui_stat_bar_numbers, health_text, (x_0 + 20, y_4 - 1))

        rect_manabar = Rect(x_0, y_4 + 20, 100, 14)
        self.ui_render.stat_bar(rect_manabar[0], rect_manabar[1], rect_manabar[2], rect_manabar[3],
                                player_mana / player_max_mana, (50, 0, 200), True)
        if is_point_in_rect(mouse_ui_position, rect_manabar):
            tooltip_details = [
                "regeneration: " + "{:.1f}".format(player_state.mana_resource.get_effective_regen()) + "/s"]
            tooltip_bottom_left_position = (rect_manabar[0], rect_manabar[1])
            tooltip = TooltipGraphics(COLOR_WHITE, "Mana", tooltip_details, bottom_left=tooltip_bottom_left_position)
        mana_text = str(player_mana) + "/" + str(player_max_mana)
        self.ui_render.text(self.font_ui_stat_bar_numbers, mana_text, (x_0 + 20, y_4 + 20))

        self.ui_render.text(self.font_ui_money, "Money: " + str(player_money), (x_0 + 4, y_4 + 38))

        # CONSUMABLES
        icon_space = 2
        icon_rect_padding = 2
        consumables_rect_pos = (x_1 - icon_rect_padding, y_2 - icon_rect_padding)
        consumables_rect = Rect(
            consumables_rect_pos[0], consumables_rect_pos[1],
            (UI_ICON_SIZE[0] + icon_space) * len(consumable_slots) - icon_space + icon_rect_padding * 2,
            UI_ICON_SIZE[1] + icon_rect_padding * 2)
        self.ui_render.rect_filled((60, 60, 80), consumables_rect)
        for i, slot_number in enumerate(consumable_slots):
            x = x_1 + i * (UI_ICON_SIZE[0] + icon_space)
            y = y_2
            consumable_types = consumable_slots[slot_number]
            consumable_type = consumable_types[0] if consumable_types else None
            if is_point_in_rect(mouse_ui_position, Rect(x, y, UI_ICON_SIZE[0], UI_ICON_SIZE[1])):
                hovered_consumable_slot_number = slot_number
                if consumable_type:
                    tooltip_title = CONSUMABLES[consumable_type].name
                    tooltip_details = [CONSUMABLES[consumable_type].description]
                    tooltip_bottom_left_position = (x, y)
                    tooltip = TooltipGraphics(COLOR_WHITE, tooltip_title, tooltip_details,
                                              bottom_left=tooltip_bottom_left_position)
            weak_highlight = slot_number == hovered_consumable_slot_number
            strong_highlight = slot_number == highlighted_consumable_action
            self._consumable_icon_in_ui(x, y, UI_ICON_SIZE, slot_number, consumable_types, weak_highlight,
                                        strong_highlight)

        # ABILITIES
        abilities_rect_pos = (x_1 - icon_rect_padding, y_4 - icon_rect_padding)
        max_num_abilities = 5
        abilities_rect = Rect(
            abilities_rect_pos[0], abilities_rect_pos[1],
            (UI_ICON_SIZE[0] + icon_space) * max_num_abilities - icon_space + icon_rect_padding * 2,
            UI_ICON_SIZE[1] + icon_rect_padding * 2)
        self.ui_render.rect_filled((60, 60, 80), abilities_rect)
        for i, ability_type in enumerate(abilities):
            x = x_1 + i * (UI_ICON_SIZE[0] + icon_space)
            y = y_4
            weak_highlight = False
            if is_point_in_rect(mouse_ui_position, Rect(x, y, UI_ICON_SIZE[0], UI_ICON_SIZE[1])):
                if ability_type:
                    weak_highlight = True
                    ability_data = ABILITIES[ability_type]
                    tooltip_title = ability_data.name
                    cooldown = str(ability_data.cooldown / 1000.0)
                    mana_cost = str(ability_data.mana_cost)
                    tooltip_details = ["Cooldown: " + cooldown + " s", "Mana: " + mana_cost, ability_data.description]
                    tooltip_bottom_left_position = (x, y)
                    tooltip = TooltipGraphics(COLOR_WHITE, tooltip_title, tooltip_details,
                                              bottom_left=tooltip_bottom_left_position)
            strong_highlight = ability_type == highlighted_ability_action
            self._ability_icon_in_ui(
                x, y, UI_ICON_SIZE, ability_type, weak_highlight, strong_highlight, ability_cooldowns_remaining)

        # ITEMS
        x_2 = 325
        items_rect_pos = (x_2 - icon_rect_padding, y_2 - icon_rect_padding)
        num_item_slot_rows = 3
        num_slots_per_row = 3
        items_rect = Rect(
            items_rect_pos[0], items_rect_pos[1],
            (UI_ICON_SIZE[0] + icon_space) * num_slots_per_row - icon_space + icon_rect_padding * 2,
            num_item_slot_rows * UI_ICON_SIZE[1] + (num_item_slot_rows - 1) * icon_space + icon_rect_padding * 2)
        self.ui_render.rect_filled((60, 60, 80), items_rect)
        for i in range(len(item_slots)):
            x = x_2 + (i % num_slots_per_row) * (UI_ICON_SIZE[0] + icon_space)
            y = y_2 + (i // num_slots_per_row) * (UI_ICON_SIZE[1] + icon_space)
            slot: ItemInventorySlot = item_slots[i]
            item_type = slot.get_item_type() if not slot.is_empty() else None
            slot_equipment_category = slot.enforced_equipment_category
            if is_point_in_rect(mouse_ui_position, Rect(x, y, UI_ICON_SIZE[0], UI_ICON_SIZE[1])):
                highlight = True
                hovered_item_slot_number = i
                if item_type:
                    item_data = ITEMS[item_type]
                    tooltip_title = item_data.name
                    tooltip_details = []
                    if item_data.item_equipment_category:
                        category_name = ITEM_EQUIPMENT_CATEGORY_NAMES[item_data.item_equipment_category]
                        tooltip_details.append("[" + category_name + "]")
                    tooltip_details += item_data.description_lines
                    tooltip_bottom_left_position = (x, y)
                    tooltip = TooltipGraphics(COLOR_ITEM_TOOLTIP_HEADER, tooltip_title, tooltip_details,
                                              bottom_left=tooltip_bottom_left_position)
                elif slot_equipment_category:
                    tooltip_title = "..."
                    category_name = ITEM_EQUIPMENT_CATEGORY_NAMES[slot_equipment_category]
                    tooltip_details = ["[" + category_name + "]",
                                       "You have nothing equipped. Drag an item here to equip it!"]
                    tooltip_bottom_left_position = (x, y)
                    tooltip = TooltipGraphics(COLOR_WHITE, tooltip_title, tooltip_details,
                                              bottom_left=tooltip_bottom_left_position)
            else:
                highlight = False
            self._item_icon_in_ui(x, y, UI_ICON_SIZE, item_type, slot_equipment_category, highlight)

        # MINIMAP
        x_3 = 440
        minimap_padding_rect_pos = (x_3 - 2, y_2 - 2)
        minimap_padding_rect = Rect(minimap_padding_rect_pos[0], minimap_padding_rect_pos[1], 80 + 4, 80 + 4)
        self.ui_render.rect_filled((60, 60, 80), minimap_padding_rect)
        self._minimap_in_ui((x_3, y_2), (80, 80), player_minimap_relative_position)

        if dialog:
            self._dialog(dialog)

        # BUFFS
        x_buffs = 10
        buff_texts = []
        buff_duration_ratios_remaining = []
        for active_buff in player_active_buffs:
            buff_type = active_buff.buff_effect.get_buff_type()
            # Buffs that don't have description texts shouldn't be displayed. (They are typically irrelevant to the
            # player)
            if buff_type in BUFF_TEXTS:
                buff_texts.append(BUFF_TEXTS[buff_type])
                buff_duration_ratios_remaining.append(active_buff.get_ratio_duration_remaining())
        num_buffs_to_render = len(buff_texts)
        y_buffs = -35 - (num_buffs_to_render - 1) * 25
        buffs_ui_position = (x_buffs, y_buffs)
        if num_buffs_to_render:
            rect_padding = 5
            # Note: The width of this rect is hard-coded so long buff descriptions aren't well supported
            buffs_background_rect = Rect(
                buffs_ui_position[0] - rect_padding,
                buffs_ui_position[1] - rect_padding,
                140 + rect_padding * 2,
                num_buffs_to_render * 25 + rect_padding * 2)
            self.ui_render.rect_transparent(buffs_background_rect, 125, COLOR_BLACK)
        for i, text in enumerate(buff_texts):
            y_offset_buff = i * 25
            y = y_buffs + y_offset_buff
            self.ui_render.text(self.font_buff_texts, text, (x_buffs, y))
            self.ui_render.stat_bar(x_buffs, y + 20, 60, 2, buff_duration_ratios_remaining[i],
                                    (250, 250, 0), False)

        # TOGGLES
        pos_toggled_content = (545, -300)
        x_toggles = 555
        if ui_state.toggle_enabled == UiToggle.STATS:
            self._render_stats(player_speed_multiplier, player_state, pos_toggled_content)
        elif ui_state.toggle_enabled == UiToggle.TALENTS:
            hovered_talent_option, talent_tooltip = self._render_talents(
                talents, pos_toggled_content, mouse_ui_position)
            tooltip = talent_tooltip if talent_tooltip is not None else tooltip
        elif ui_state.toggle_enabled == UiToggle.CONTROLS:
            self._render_controls(pos_toggled_content)

        is_mouse_hovering_stats_toggle = self._toggle_in_ui(
            x_toggles, y_1, "STATS", ui_state.toggle_enabled == UiToggle.STATS, mouse_ui_position, False)
        is_mouse_hovering_talents_toggle = self._toggle_in_ui(
            x_toggles, y_1 + 30, "TALENTS", ui_state.toggle_enabled == UiToggle.TALENTS,
            mouse_ui_position, ui_state.talent_toggle_has_unseen_talents)
        is_mouse_hovering_help_toggle = self._toggle_in_ui(
            x_toggles, y_1 + 60, "CONTROLS", ui_state.toggle_enabled == UiToggle.CONTROLS, mouse_ui_position, False)
        if is_mouse_hovering_stats_toggle:
            hovered_ui_toggle = UiToggle.STATS
        elif is_mouse_hovering_talents_toggle:
            hovered_ui_toggle = UiToggle.TALENTS
        elif is_mouse_hovering_help_toggle:
            hovered_ui_toggle = UiToggle.CONTROLS

        self.screen_render.rect(COLOR_BORDER, self.ui_screen_area, 1)

        self.screen_render.rect_transparent(Rect(0, 0, 50, 20), 100, COLOR_BLACK)
        self.screen_render.text(self.font_debug_info, fps_string + " fps", (5, 3))

        if message:
            self._message(message)

        if tooltip:
            self._tooltip(tooltip)

        if is_paused:
            self.screen_render.rect_transparent(Rect(0, 0, self.screen_size[0], self.screen_size[1]), 140, COLOR_BLACK)
            self._splash_screen_text("PAUSED", self.screen_size[0] / 2 - 110, self.screen_size[1] / 2 - 50)

        return MouseHoverEvent(hovered_item_slot_number, hovered_consumable_slot_number, is_mouse_hovering_ui,
                               hovered_ui_toggle, hovered_talent_option)
