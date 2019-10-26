from typing import Tuple, Optional, List, Any, Dict

import pygame
from pygame.rect import Rect

from pythongame.core.common import Direction, Sprite, UiIconSprite, PortraitIconSprite


class SpriteInitializer:
    def __init__(self, image_file_path: str, scaling_size: Tuple[int, int]):
        self.image_file_path = image_file_path
        self.scaling_size = scaling_size


class SpriteSheet(object):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.sheet = None

    def _load_sheet(self):
        self.sheet = pygame.image.load(self.file_path).convert_alpha()

    def image_at(self, rect: Rect):
        if self.sheet is None:
            self._load_sheet()

        # noinspection PyArgumentList
        image = pygame.Surface(rect.size, pygame.SRCALPHA)
        destination_in_image = (0, 0)
        image.blit(self.sheet, destination_in_image, rect)
        transparent_color_in_image = (0, 0, 0)
        image.set_colorkey(transparent_color_in_image, pygame.RLEACCEL)
        return image


class SpriteMapInitializer:
    def __init__(self, sprite_sheet: SpriteSheet, original_sprite_size: Tuple[int, int], scaling_size: Tuple[int, int],
                 index_position_within_map: Tuple[int, int]):
        self.sprite_sheet = sprite_sheet
        self.original_sprite_size = original_sprite_size
        self.scaling_size = scaling_size
        self.index_position_within_map = index_position_within_map


class Animation:
    def __init__(
            self,
            sprite_initializers: Optional[List[SpriteInitializer]],
            sprite_map_initializers: Optional[List[SpriteMapInitializer]],
            position_relative_to_entity: Tuple[int, int]):
        self.sprite_initializers = sprite_initializers
        self.sprite_map_initializers = sprite_map_initializers
        self.position_relative_to_entity = position_relative_to_entity


class ImageWithRelativePosition:
    def __init__(self, image: Any, position_relative_to_entity: Tuple[int, int]):
        self.image = image
        self.position_relative_to_entity = position_relative_to_entity


def load_and_scale_sprite(sprite_initializer: SpriteInitializer):
    return _load_and_scale_sprite(sprite_initializer.image_file_path, sprite_initializer.scaling_size)


def load_and_scale_directional_sprites(
        animations_by_dir: Dict[Direction, Animation]) -> Dict[Direction, List[ImageWithRelativePosition]]:
    images: Dict[Direction, List[ImageWithRelativePosition]] = {}
    for direction in animations_by_dir:
        animation = animations_by_dir[direction]
        images_for_dir: List[ImageWithRelativePosition] = []
        if animation.sprite_initializers:
            for sprite_init in animation.sprite_initializers:
                scaled_image = load_and_scale_sprite(sprite_init)
                images_for_dir.append(ImageWithRelativePosition(scaled_image, animation.position_relative_to_entity))
        elif animation.sprite_map_initializers:
            for sprite_map_init in animation.sprite_map_initializers:
                sprite_sheet = sprite_map_init.sprite_sheet
                index_position_within_map = sprite_map_init.index_position_within_map
                original_sprite_size = sprite_map_init.original_sprite_size
                rectangle = Rect(index_position_within_map[0] * original_sprite_size[0],
                                 index_position_within_map[1] * original_sprite_size[1],
                                 original_sprite_size[0],
                                 original_sprite_size[1])
                image = sprite_sheet.image_at(rectangle)
                scaled_image = pygame.transform.scale(image, sprite_map_init.scaling_size)
                images_for_dir.append(ImageWithRelativePosition(scaled_image, animation.position_relative_to_entity))
        else:
            raise Exception("Invalid animation: " + str(animation))
        images[direction] = images_for_dir
    return images


def _load_and_scale_sprite(image_file_path: str, scaling_size: Tuple[int, int]):
    image = pygame.image.load(image_file_path).convert_alpha()
    return pygame.transform.scale(image, scaling_size)


def load_images_by_sprite(dictionary: Dict[Sprite, Dict[Direction, Animation]]) \
        -> Dict[Sprite, Dict[Direction, List[ImageWithRelativePosition]]]:
    return {sprite: load_and_scale_directional_sprites(dictionary[sprite]) for sprite in dictionary}


def load_images_by_ui_sprite(dictionary: Dict[UiIconSprite, str], icon_size: Tuple[int, int]) \
        -> Dict[UiIconSprite, Any]:
    return {sprite: load_and_scale_sprite(SpriteInitializer(dictionary[sprite], icon_size)) for sprite in dictionary
            }


def load_images_by_portrait_sprite(dictionary: Dict[PortraitIconSprite, str], icon_size: Tuple[int, int]) \
        -> Dict[PortraitIconSprite, Any]:
    return {sprite: load_and_scale_sprite(SpriteInitializer(dictionary[sprite], icon_size)) for sprite in dictionary}
