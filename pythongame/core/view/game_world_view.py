from enum import Enum
from typing import Dict, List, Tuple, Optional, Union

import pygame
from pygame.rect import Rect

from pythongame.core.common import Direction, Sprite
from pythongame.core.game_data import ENTITY_SPRITE_INITIALIZERS, CHANNELING_BUFFS
from pythongame.core.game_state import DecorationEntity, NonPlayerCharacter, BuffWithDuration, \
    QuestGiverState
from pythongame.core.view.image_loading import ImageWithRelativePosition
from pythongame.core.view.render_util import DrawableArea, split_text_into_lines
from pythongame.core.visual_effects import VisualLine, VisualCircle, VisualRect, VisualText, VisualSprite, VisualCross, \
    VisualParticleSystem
from pythongame.core.world_entity import WorldEntity

COLOR_BACKGROUND = (88 + 30, 72 + 30, 40 + 30)
COLOR_BACKGROUND_LINES = (93 + 30, 77 + 30, 45 + 30)
COLOR_RED = (250, 0, 0)
RENDER_WORLD_COORDINATES = False
DIR_FONTS = './resources/fonts/'


class EntityActionTextStyle(Enum):
    PLAIN = 1
    LOOT_RARE = 2
    LOOT_UNIQUE = 3


# Used to display some text above entities (NPC's, objects, loot, etc)
# Example "[Space] Talk" or "[Space] Health potion"
class EntityActionText:
    def __init__(self, entity: WorldEntity, text: str, details: List[str],
                 style: EntityActionTextStyle = EntityActionTextStyle.PLAIN):
        self.entity: WorldEntity = entity
        self.text: str = text
        self.details: List[str] = details
        self.style = style


class GameWorldView:

    def __init__(self, pygame_screen, camera_size: Tuple[int, int], screen_size: Tuple[int, int],
                 images_by_sprite: Dict[Sprite, Dict[Direction, List[ImageWithRelativePosition]]]):
        pygame.font.init()
        self.screen_render = DrawableArea(pygame_screen)
        self.ui_render = DrawableArea(pygame_screen, self._translate_ui_position_to_screen)
        self.world_render = DrawableArea(pygame_screen, self._translate_world_position_to_screen)

        self.ui_screen_area = Rect(0, camera_size[1], screen_size[0], screen_size[1] - camera_size[1])
        self.camera_size = camera_size
        self.screen_size = screen_size

        self.font_npc_action = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_debug_info = pygame.font.Font(DIR_FONTS + 'Arial Rounded Bold.ttf', 19)
        self.font_visual_text_small = pygame.font.Font(DIR_FONTS + 'Courier New Bold.ttf', 12)
        self.font_visual_text = pygame.font.Font(DIR_FONTS + 'Courier New Bold.ttf', 14)
        self.font_visual_text_large = pygame.font.Font(DIR_FONTS + 'Courier New Bold.ttf', 16)
        self.font_quest_giver_mark = pygame.font.Font(DIR_FONTS + 'Courier New Bold.ttf', 28)

        self.images_by_sprite: Dict[Sprite, Dict[Direction, List[ImageWithRelativePosition]]] = images_by_sprite

        # This is updated every time the view is called
        self.camera_world_area = None

    # ------------------------------------
    #         TRANSLATING COORDINATES
    # ------------------------------------

    def _translate_world_position_to_screen(self, world_position):
        return (self._translate_world_x_to_screen(world_position[0]),
                self._translate_world_y_to_screen(world_position[1]))

    def _translate_screen_position_to_world(self, screen_position):
        return int(screen_position[0] + self.camera_world_area.x), int(screen_position[1] + self.camera_world_area.y)

    def _translate_world_x_to_screen(self, world_x):
        return int(world_x - self.camera_world_area.x)

    def _translate_world_y_to_screen(self, world_y):
        return int(world_y - self.camera_world_area.y)

    def _translate_ui_position_to_screen(self, position):
        return position[0] + self.ui_screen_area.x, position[1] + self.ui_screen_area.y

    def _translate_screen_position_to_ui(self, position: Tuple[int, int]):
        return position[0] - self.ui_screen_area.x, position[1] - self.ui_screen_area.y

    # ------------------------------------
    #       DRAWING THE GAME WORLD
    # ------------------------------------

    def _world_ground(self, entire_world_area: Rect):
        grid_width = 35
        # TODO num squares should depend on map size. Ideally this dumb looping logic should change.
        num_squares = 200
        column_screen_y_0 = self._translate_world_y_to_screen(self.camera_world_area.y)
        column_screen_y_1 = self._translate_world_y_to_screen(
            min(entire_world_area.y + entire_world_area.h, self.camera_world_area.y + self.camera_world_area.h))
        for i_col in range(num_squares):
            world_x = entire_world_area.x + i_col * grid_width
            if entire_world_area.x < world_x < entire_world_area.x + entire_world_area.w:
                screen_x = self._translate_world_x_to_screen(world_x)
                self.screen_render.line(COLOR_BACKGROUND_LINES, (screen_x, column_screen_y_0),
                                        (screen_x, column_screen_y_1),
                                        1)
        row_screen_x_0 = self._translate_world_x_to_screen(self.camera_world_area.x)
        row_screen_x_1 = self._translate_world_x_to_screen(
            min(entire_world_area.x + entire_world_area.w, self.camera_world_area.x + self.camera_world_area.w))
        for i_row in range(num_squares):
            world_y = entire_world_area.y + i_row * grid_width
            if entire_world_area.y < world_y < entire_world_area.y + entire_world_area.h:
                screen_y = self._translate_world_y_to_screen(world_y)
                self.screen_render.line(COLOR_BACKGROUND_LINES, (row_screen_x_0, screen_y), (row_screen_x_1, screen_y),
                                        1)

        if RENDER_WORLD_COORDINATES:
            for i_col in range(num_squares):
                for i_row in range(num_squares):
                    if i_col % 4 == 0 and i_row % 4 == 0:
                        world_x = entire_world_area.x + i_col * grid_width
                        screen_x = self._translate_world_x_to_screen(world_x)
                        world_y = entire_world_area.y + i_row * grid_width
                        screen_y = self._translate_world_y_to_screen(world_y)
                        self.screen_render.text(self.font_debug_info, str(world_x) + "," + str(world_y),
                                                (screen_x, screen_y),
                                                (250, 250, 250))

    def _world_entity(self, entity: Union[WorldEntity, DecorationEntity]):
        if not entity.visible:
            return
        if entity.sprite is None:
            raise Exception("Entity has no sprite value: " + str(entity))
        elif entity.sprite in self.images_by_sprite:
            image_with_relative_position = self._get_image_for_sprite(
                entity.sprite, entity.direction, entity.movement_animation_progress)
            self.world_render.image_with_relative_pos(image_with_relative_position, entity.get_position())
        elif entity.sprite == Sprite.NONE:
            # This value is used by entities that don't use sprites. They might have other graphics (like VisualEffects)
            pass
        else:
            raise Exception("Unhandled sprite: " + str(entity.sprite))

    def _get_image_for_sprite(self, sprite: Sprite, direction: Direction,
                              animation_progress: float) -> ImageWithRelativePosition:

        images: Dict[Direction, List[ImageWithRelativePosition]] = self.images_by_sprite[sprite]
        if direction in images:
            images_for_this_direction = images[direction]
        else:
            images_for_this_direction = next(iter(images.values()))

        animation_frame_index = int(len(images_for_this_direction) * animation_progress)
        return images_for_this_direction[animation_frame_index]

    def _visual_effect(self, visual_effect):
        if isinstance(visual_effect, VisualLine):
            self._visual_line(visual_effect)
        elif isinstance(visual_effect, VisualCircle):
            self._visual_circle(visual_effect)
        elif isinstance(visual_effect, VisualRect):
            self._visual_rect(visual_effect)
        elif isinstance(visual_effect, VisualCross):
            self._visual_cross(visual_effect)
        elif isinstance(visual_effect, VisualText):
            self._visual_text(visual_effect)
        elif isinstance(visual_effect, VisualSprite):
            self._visual_sprite(visual_effect)
        elif isinstance(visual_effect, VisualParticleSystem):
            self._visual_particle_system(visual_effect)
        else:
            raise Exception("Unhandled visual effect: " + str(visual_effect))

    def _visual_line(self, line: VisualLine):
        self.world_render.line(line.color, line.start_position, line.end_position, line.line_width)

    def _visual_circle(self, visual_circle: VisualCircle):
        position = visual_circle.circle()[0]
        radius = visual_circle.circle()[1]
        self.world_render.circle(visual_circle.color, position, radius, visual_circle.line_width)

    def _visual_rect(self, visual_rect: VisualRect):
        self.world_render.rect(visual_rect.color, visual_rect.rect(), visual_rect.line_width)

    def _visual_cross(self, visual_cross: VisualCross):
        for start_pos, end_pos in visual_cross.lines():
            self.world_render.line(visual_cross.color, start_pos, end_pos, visual_cross.line_width)

    def _visual_text(self, visual_text: VisualText):
        text = visual_text.text
        position = visual_text.position()
        # Adjust position so that long texts don't appear too far to the right
        translated_position = (position[0] - 3 * len(text), position[1])
        # limit the space long texts claim on the screen (example "BLOCK" and "DODGE")
        if len(text) >= 4:
            font = self.font_visual_text_small
        elif visual_text.emphasis:
            font = self.font_visual_text_large
        else:
            font = self.font_visual_text
        self.world_render.text(font, text, translated_position, visual_text.color)

    def _visual_sprite(self, visual_sprite: VisualSprite):
        position = visual_sprite.position
        animation_progress = visual_sprite.animation_progress()
        sprite = visual_sprite.sprite
        if sprite in self.images_by_sprite:
            image_with_relative_position = self._get_image_for_sprite(
                sprite, Direction.DOWN, animation_progress)
            self.world_render.image_with_relative_pos(image_with_relative_position, position)
        else:
            raise Exception("Unhandled sprite: " + str(sprite))

    def _visual_particle_system(self, visual_particle_system: VisualParticleSystem):
        for particle in visual_particle_system.particles():
            self.world_render.rect_transparent(particle.rect, particle.alpha, particle.color)

    def _stat_bar_for_world_entity(self, world_entity, h, relative_y, ratio, color, border_color=None):
        self.world_render.stat_bar(world_entity.x + 1, world_entity.y + relative_y,
                                   world_entity.pygame_collision_rect.w - 2, h, ratio, color, border_color=border_color)

    def _entity_action_text(self, entity_action_text: EntityActionText):
        entity_center_pos = entity_action_text.entity.get_center_position()
        header_prefix = "[Space] "
        header_line = header_prefix + entity_action_text.text
        detail_lines = []
        for detail_entry in entity_action_text.details:
            detail_lines += split_text_into_lines(detail_entry, 30)
        if detail_lines:
            line_length = max(max([len(line) for line in detail_lines]), len(header_line))
        else:
            line_length = len(header_line)
        rect_width = line_length * 8
        rect_height = 16 + len(detail_lines) * 16
        rect_pos = (entity_center_pos[0] - rect_width // 2, entity_center_pos[1] - 60)
        self.world_render.rect_transparent(Rect(rect_pos[0], rect_pos[1], rect_width, rect_height), 150, (0, 0, 0))
        if entity_action_text.style == EntityActionTextStyle.LOOT_RARE:
            color = (190, 150, 250)
        elif entity_action_text.style == EntityActionTextStyle.LOOT_UNIQUE:
            color = (250, 250, 150)
        else:
            color = (255, 255, 255)
        self.world_render.text(self.font_npc_action, header_prefix, (rect_pos[0] + 4, rect_pos[1]))
        prefix_w = self.font_npc_action.size(header_prefix)[0]
        self.world_render.text(self.font_npc_action, entity_action_text.text, (rect_pos[0] + 4 + prefix_w, rect_pos[1]),
                               color)
        for i, detail_line in enumerate(detail_lines):
            self.world_render.text(self.font_npc_action, detail_line, (rect_pos[0] + 4, rect_pos[1] + (i + 1) * 16))

    def _quest_giver_mark(self, npc: NonPlayerCharacter):
        entity_pos = npc.world_entity.get_center_position()
        if npc.quest_giver_state == QuestGiverState.CAN_GIVE_NEW_QUEST:
            color = (255, 215, 0)
            mark = "!"
        elif npc.quest_giver_state == QuestGiverState.WAITING_FOR_PLAYER:
            color = (192, 192, 192)
            mark = "?"
        else:
            color = (255, 215, 0)
            mark = "?"
        self.world_render.text(self.font_quest_giver_mark, mark, (entity_pos[0] - 8, entity_pos[1] - 64), (0, 0, 0))
        self.world_render.text(self.font_quest_giver_mark, mark, (entity_pos[0] - 9, entity_pos[1] - 65), color)

    def render_world(self, all_entities_to_render: List[WorldEntity], decorations_to_render: List[DecorationEntity],
                     camera_world_area, non_player_characters: List[NonPlayerCharacter], is_player_invisible: bool,
                     player_active_buffs: List[BuffWithDuration],
                     player_entity: WorldEntity, visual_effects, render_hit_and_collision_boxes, player_health,
                     player_max_health, entire_world_area: Rect, entity_action_text: Optional[EntityActionText]):
        self.camera_world_area = camera_world_area

        self.screen_render.fill(COLOR_BACKGROUND)
        self._world_ground(entire_world_area)

        all_entities_to_render.sort(key=lambda entry: (-entry.view_z, entry.y))

        for decoration_entity in decorations_to_render:
            self._world_entity(decoration_entity)

        for entity in all_entities_to_render:
            self._world_entity(entity)
            if entity == player_entity and is_player_invisible:
                self.world_render.rect((200, 100, 250), player_entity.rect(), 2)

        player_sprite_y_relative_to_entity = \
            ENTITY_SPRITE_INITIALIZERS[player_entity.sprite][Direction.DOWN].position_relative_to_entity[1]
        if player_entity.visible:
            self._stat_bar_for_world_entity(player_entity, 5, player_sprite_y_relative_to_entity - 5,
                                            player_health / player_max_health, (100, 200, 0))

        # Buffs related to channeling something are rendered above player's head with progress from left to right
        for buff in player_active_buffs:
            if buff.buff_effect.get_buff_type() in CHANNELING_BUFFS:
                ratio = 1 - buff.get_ratio_duration_remaining()
                self._stat_bar_for_world_entity(player_entity, 3, player_sprite_y_relative_to_entity - 11, ratio,
                                                (150, 150, 250))

        if render_hit_and_collision_boxes:
            for entity in all_entities_to_render:
                self.world_render.rect((250, 250, 250), entity.rect(), 1)

        for npc in non_player_characters:
            if npc.is_enemy:
                if npc.is_boss:
                    healthbar_color = (255, 215, 0)
                    border_color = COLOR_RED
                else:
                    healthbar_color = COLOR_RED
                    border_color = None
            else:
                healthbar_color = (250, 250, 0)
                border_color = None
                if npc.quest_giver_state is not None:
                    self._quest_giver_mark(npc)

            npc_sprite_y_relative_to_entity = \
                ENTITY_SPRITE_INITIALIZERS[npc.world_entity.sprite][Direction.DOWN].position_relative_to_entity[1]
            if not npc.is_neutral:
                self._stat_bar_for_world_entity(npc.world_entity, 3, npc_sprite_y_relative_to_entity - 5,
                                                npc.health_resource.get_partial(), healthbar_color, border_color)
            if npc.active_buffs:
                buff = npc.active_buffs[0]
                if buff.should_duration_be_visualized_on_enemies():
                    self._stat_bar_for_world_entity(npc.world_entity, 2, npc_sprite_y_relative_to_entity - 9,
                                                    buff.get_ratio_duration_remaining(), (250, 250, 250))
        for visual_effect in visual_effects:
            self._visual_effect(visual_effect)

        if entity_action_text:
            self._entity_action_text(entity_action_text)
