import random
from typing import Tuple, Optional, List

from pygame.rect import Rect

from pythongame.core.common import Millis, Sprite
from pythongame.core.game_data import ENTITY_SPRITE_SIZES
from pythongame.core.game_state import WorldEntity


class VisualEffect:
    def __init__(self, max_age: Millis, attached_to_entity: Optional[WorldEntity]):
        self._age = 0
        self._max_age = max_age
        self.has_expired = False
        self.attached_to_entity = attached_to_entity

    def notify_time_passed(self, time_passed: Millis):
        self._age += time_passed
        if self._age > self._max_age:
            self.has_expired = True

    def update_position_if_attached_to_entity(self):
        pass


class Particle:
    def __init__(self, rect: Rect, velocity: Tuple[int, int], color: Tuple[int, int, int], alpha: int,
                 time_left: Millis):
        self.rect = rect
        self.velocity = velocity
        self.color = color
        self.alpha = alpha
        self.time_left = time_left

    def notify_time_passed(self, time_passed: Millis):
        self.rect[0] += self.velocity[0] * time_passed / 30
        self.rect[1] += self.velocity[1] * time_passed / 30
        self.time_left -= time_passed


class VisualParticleSystem(VisualEffect):

    def __init__(self, num_particles: int, position: Tuple[int, int], colors: List[Tuple[int, int, int]], alpha: int,
                 duration_interval: Tuple[Millis, Millis]):
        super().__init__(Millis(250), None)
        self._particles: List[Particle] = []
        max_start_offset = 20
        for i in range(num_particles):
            w = random.randint(8, 16)
            max_speed = 20 - w
            x = position[0] + random.randint(-max_start_offset, max_start_offset) - w / 2
            y = position[1] + random.randint(-max_start_offset, max_start_offset) - w / 2
            velocity = random.randint(-max_speed, max_speed), random.randint(-max_speed, max_speed)
            particle_color = random.choice(colors)
            duration = random.randint(duration_interval[0], duration_interval[1])
            particle = Particle(Rect(x, y, w, w), velocity, particle_color, alpha, duration)
            self._particles.append(particle)

    def notify_time_passed(self, time_passed: Millis):
        super().notify_time_passed(time_passed)
        for p in self._particles:
            p.notify_time_passed(time_passed)
        self._particles = [p for p in self._particles if p.time_left > 0]

    def particles(self):
        return self._particles


class VisualLine(VisualEffect):
    def __init__(self, color: Tuple[int, int, int], start_position: Tuple[int, int], end_position: Tuple[int, int],
                 max_age: Millis, line_width: int):
        super().__init__(max_age, None)
        self.color = color
        self.start_position = start_position
        self.end_position = end_position
        self.line_width = line_width


class VisualCircle(VisualEffect):
    def __init__(self, color: Tuple[int, int, int], center_position: Tuple[int, int], start_radius: int,
                 end_radius: int, max_age: Millis, line_width: int, attached_to_entity: WorldEntity = None):
        super().__init__(max_age, attached_to_entity)
        self.color = color
        self.center_position = center_position
        self.start_radius = start_radius
        self.end_radius = end_radius
        self.line_width = line_width

    def circle(self):
        position = self.center_position[0], self.center_position[1]
        radius = self.start_radius + int(self._age / self._max_age * (self.end_radius - self.start_radius))
        return position, radius

    def update_position_if_attached_to_entity(self):
        if self.attached_to_entity:
            self.center_position = self.attached_to_entity.get_center_position()


class VisualCross(VisualEffect):
    def __init__(self, color: Tuple[int, int, int], center_position: Tuple[int, int], radius: int, max_age: Millis,
                 line_width: int, attached_to_entity: WorldEntity = None):
        super().__init__(max_age, attached_to_entity)
        self.radius = radius
        self.color = color
        self.center_position = center_position
        self.line_width = line_width

    def update_position_if_attached_to_entity(self):
        if self.attached_to_entity:
            self.center_position = self.attached_to_entity.get_center_position()

    def lines(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        left = self.center_position[0] - self.radius
        right = self.center_position[0] + self.radius
        top = self.center_position[1] - self.radius
        bot = self.center_position[1] + self.radius
        line_1 = (left, top), (right, bot)
        line_2 = (right, top), (left, bot)
        return [line_1, line_2]


class VisualRect(VisualEffect):
    def __init__(self, color: Tuple[int, int, int], center_position: Tuple[int, int], start_width: int, end_width: int,
                 max_age: Millis, line_width: int, attached_to_entity: WorldEntity = None):
        super().__init__(max_age, attached_to_entity)
        self.color = color
        self.center_position = center_position
        self.start_width = start_width
        self.end_width = end_width
        self.line_width = line_width

    def rect(self):
        width = self.start_width + int(self._age / self._max_age * (self.end_width - self.start_width))
        return self.center_position[0] - width / 2, self.center_position[1] - width / 2, width, width

    def update_position_if_attached_to_entity(self):
        if self.attached_to_entity:
            self.center_position = self.attached_to_entity.get_center_position()


class VisualText(VisualEffect):
    def __init__(self, text: str, color: Tuple[int, int, int], start_position: Tuple[int, int],
                 end_position: Tuple[int, int], max_age: Millis, emphasis: bool = False):
        super().__init__(max_age, None)
        self.text = text
        self.color = color
        self.start_position = start_position
        self.end_position = end_position
        self.emphasis = emphasis

    def position(self):
        x = self.start_position[0] + int(self._age / self._max_age * (self.end_position[0] - self.start_position[0]))
        y = self.start_position[1] + int(self._age / self._max_age * (self.end_position[1] - self.start_position[1]))
        return x, y


class VisualSprite(VisualEffect):
    def __init__(self, sprite: Sprite, position: Tuple[int, int], max_age: Millis, attached_to_entity: WorldEntity):
        super().__init__(max_age, attached_to_entity)
        self.sprite = sprite
        self.position = position
        self._animation_progress = 0
        self.max_age = max_age

    def animation_progress(self):
        return (self._animation_progress + float(self._age) / float(self.max_age)) % 1


def create_visual_stun_text(entity: WorldEntity):
    start_position, end_position = _get_entity_text_positions(entity, 10)
    return VisualText("STUN", (255, 255, 255), start_position, end_position, Millis(500))


def create_visual_block_text(entity: WorldEntity):
    start_position, end_position = _get_entity_text_positions(entity, 10)
    return VisualText("BLOCK", (255, 255, 255), start_position, end_position, Millis(500))


def create_visual_dodge_text(entity: WorldEntity):
    start_position, end_position = _get_entity_text_positions(entity, 10)
    return VisualText("DODGE", (255, 255, 255), start_position, end_position, Millis(500))


def create_visual_resist_text(entity: WorldEntity):
    start_position, end_position = _get_entity_text_positions(entity, 10)
    return VisualText("RESIST", (255, 255, 255), start_position, end_position, Millis(500))


def create_visual_damage_text(entity: WorldEntity, damage_amount: int, emphasis: bool = False):
    start_position, end_position = _get_entity_text_positions(entity, 40)
    color = (220, 50, 100) if emphasis else (220, 0, 0)
    return VisualText(str(damage_amount), color, start_position, end_position, Millis(800), emphasis=emphasis)


def create_visual_healing_text(entity: WorldEntity, healing_amount: int):
    start_position, end_position = _get_entity_text_positions(entity, 40)
    return VisualText(str(healing_amount), (0, 140, 0), start_position, end_position, Millis(800))


def create_visual_mana_text(entity: WorldEntity, healing_amount: int):
    start_position, end_position = _get_entity_text_positions(entity, 40)
    return VisualText(str(healing_amount), (0, 0, 140), start_position, end_position, Millis(800))


def create_visual_exp_text(entity: WorldEntity, exp_amount: int):
    start_position, end_position = _get_entity_text_positions(entity, 40)
    return VisualText(str(exp_amount), (255, 255, 255), start_position, end_position, Millis(800))


def create_teleport_effects(effect_position: Tuple) -> List[VisualEffect]:
    color = (140, 140, 230)
    return [VisualCircle(color, effect_position, 17, 35, Millis(150), 1),
            VisualRect(color, effect_position, 37, 50, Millis(150), 1),
            VisualCircle(color, effect_position, 25, 50, Millis(300), 2)]


def _get_entity_text_positions(entity: WorldEntity, text_y_travel_distance: int) -> Tuple[
    Tuple[int, int], Tuple[int, int]]:
    sprite_size = ENTITY_SPRITE_SIZES[entity.sprite]
    y_start = entity.y + entity.pygame_collision_rect.h - sprite_size[1]
    random_x_offset = random.randint(-10, 10)
    x = entity.get_center_position()[0] - 5 + random_x_offset
    start_position = (x, y_start)
    end_position = (x, y_start - text_y_travel_distance)
    return start_position, end_position
