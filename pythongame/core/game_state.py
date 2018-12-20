import math
from typing import List, Optional, Dict, Any

from pygame.rect import Rect

from pythongame.core.common import *

GRID_CELL_WIDTH = 25

WALL_BUCKET_WIDTH = 100
WALL_BUCKET_HEIGHT = 100


class WorldArea:
    def __init__(self, pos: Tuple[int, int], size: Tuple[int, int]):
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]

    def get_position(self):
        return self.x, self.y

    def set_position(self, new_position):
        self.x = new_position[0]
        self.y = new_position[1]

    def rect(self):
        return self.x, self.y, self.w, self.h

    def contains_position(self, position: Tuple[int, int]) -> bool:
        return self.x <= position[0] <= self.x + self.w and self.y <= position[1] <= self.y + self.h


class WorldEntity:
    def __init__(self, pos: Tuple[int, int], size: Tuple[int, int], sprite: Sprite, direction=Direction.LEFT, speed=0):
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]
        # TODO: Rethink how collision boxes should be handled. Disabled for now.
        self.collision_w = self.w
        self.collision_h = self.h
        self.sprite = sprite
        self.direction = direction
        self._speed = speed
        self._speed_multiplier = 1
        self._effective_speed = speed
        self._is_moving = True
        self.pygame_collision_rect = Rect(self.collision_rect())
        self.movement_animation_progress: float = 0  # goes from 0 to 1 repeatedly

    def set_moving_in_dir(self, direction: Direction):
        if direction is None:
            raise Exception("Need to provide a valid direciton to move in")
        self.direction = direction
        self._is_moving = True

    def set_not_moving(self):
        self._is_moving = False

    def get_new_position_according_to_dir_and_speed(self, time_passed: Millis) -> Optional:
        distance = self._effective_speed * time_passed
        if self._is_moving:
            return translate_in_direction((self.x, self.y), self.direction, distance)
        return None

    def update_movement_animation(self, time_passed: Millis):
        if self._is_moving:
            self.movement_animation_progress = (self.movement_animation_progress + float(time_passed) / 1000) % 1
        else:
            self.movement_animation_progress = 0

    def get_new_position_according_to_other_dir_and_speed(self, direction: Direction, time_passed: Millis) -> Optional:
        distance = self._effective_speed * time_passed
        return translate_in_direction((self.x, self.y), direction, distance)

    def get_center_position(self):
        return int(self.x + self.w / 2), int(self.y + self.h / 2)

    def get_position(self):
        return self.x, self.y

    def add_to_speed_multiplier(self, amount):
        self._speed_multiplier += amount
        self._effective_speed = self._speed_multiplier * self._speed

    # TODO use more
    def rect(self):
        return self.x, self.y, self.w, self.h

    def translate_x(self, amount):
        self.set_position((self.x + amount, self.y))

    def translate_y(self, amount):
        self.set_position((self.x, self.y + amount))

    def set_position(self, new_position):
        self.x = new_position[0]
        self.y = new_position[1]
        self.pygame_collision_rect = Rect(self.collision_rect())

    def collision_rect(self):
        collision_x = self.get_center_position()[0] - self.collision_w / 2
        collision_y = self.get_center_position()[1] - self.collision_h / 2
        return collision_x, collision_y, self.collision_w, self.collision_h

    def rotate_right(self):
        dirs = {
            Direction.DOWN: Direction.LEFT,
            Direction.LEFT: Direction.UP,
            Direction.UP: Direction.RIGHT,
            Direction.RIGHT: Direction.DOWN
        }
        self.direction = dirs[self.direction]

    def rotate_left(self):
        dirs = {
            Direction.DOWN: Direction.RIGHT,
            Direction.RIGHT: Direction.UP,
            Direction.UP: Direction.LEFT,
            Direction.LEFT: Direction.DOWN
        }
        self.direction = dirs[self.direction]


class PotionOnGround:
    def __init__(self, world_entity: WorldEntity, potion_type: PotionType):
        self.world_entity = world_entity
        self.potion_type = potion_type


class ItemOnGround:
    def __init__(self, world_entity: WorldEntity, item_type: ItemType):
        self.world_entity = world_entity
        self.item_type = item_type


class Projectile:
    def __init__(self, world_entity: WorldEntity, projectile_controller):
        self.world_entity = world_entity
        self.has_expired = False
        self.projectile_controller = projectile_controller


class Enemy:
    def __init__(self, enemy_type: EnemyType, world_entity: WorldEntity, health: int, max_health: int,
                 health_regen: float, enemy_mind):
        self.enemy_type = enemy_type
        self.world_entity = world_entity
        self._health_float = health
        self.health = health
        self.max_health = max_health
        self.health_regen = health_regen
        self.enemy_mind = enemy_mind
        self.active_buffs: List[BuffWithDuration] = []
        self.invulnerable: bool = False
        self._number_of_active_stuns = 0

    def lose_health(self, amount):
        self._health_float = min(self._health_float - amount, self.max_health)
        self.health = int(math.floor(self._health_float))

    def gain_health(self, amount):
        self._health_float = min(self._health_float + amount, self.max_health)
        self.health = int(math.floor(self._health_float))

    def gain_buff_effect(self, buff: Any, duration: Millis):
        existing_buffs_with_this_type = [b for b in self.active_buffs
                                         if b.buff_effect.get_buff_type() == buff.get_buff_type()]
        if existing_buffs_with_this_type:
            existing_buffs_with_this_type[0].time_until_expiration = duration
        else:
            self.active_buffs.append(BuffWithDuration(buff, duration))

    def regenerate_health(self, time_passed: Millis):
        self.gain_health(self.health_regen * float(time_passed))

    def add_stun(self):
        self._number_of_active_stuns += 1

    def remove_stun(self):
        self._number_of_active_stuns -= 1
        if self._number_of_active_stuns < 0:
            raise Exception("Number of active stuns went below 0 down to " + str(self._number_of_active_stuns))

    def is_stunned(self):
        return self._number_of_active_stuns > 0


class BuffWithDuration:
    def __init__(self, buff_effect: Any, time_until_expiration: Millis):
        self.buff_effect = buff_effect
        self.time_until_expiration = time_until_expiration
        self.has_applied_start_effect = False


class AgentBuffsUpdate:
    def __init__(self, buffs_that_started: List[Any], buffs_that_were_active: List[Any],
                 buffs_that_ended: List[Any]):
        self.buffs_that_started = buffs_that_started
        self.buffs_that_were_active = buffs_that_were_active
        self.buffs_that_ended = buffs_that_ended


class PlayerState:
    def __init__(self, health: int, max_health: int, mana: int, max_mana: int, mana_regen: float,
                 potion_slots: Dict[int, PotionType], abilities: List[AbilityType], item_slots: Dict[int, ItemType]):
        self.health = health
        self._health_float = health
        self.max_health = max_health
        self.mana = mana
        self._mana_float = mana
        self.max_mana = max_mana
        self.mana_regen = mana_regen
        self.potion_slots = potion_slots
        self.abilities = abilities
        self.ability_cooldowns_remaining = {ability_type: 0 for ability_type in abilities}
        self.active_buffs: List[BuffWithDuration] = []
        self.is_invisible = False
        self.is_stunned = False
        self.item_slots = item_slots
        self.life_steal_ratio = 0

    def gain_health(self, amount: float):
        self._health_float = min(self._health_float + amount, self.max_health)
        self.health = int(math.floor(self._health_float))

    def lose_health(self, amount: float):
        self._health_float = min(self._health_float - amount, self.max_health)
        self.health = int(math.floor(self._health_float))

    def gain_mana(self, amount: float):
        self._mana_float = min(self._mana_float + amount, self.max_mana)
        self.mana = int(math.floor(self._mana_float))

    def lose_mana(self, amount: float):
        self._mana_float -= amount
        self.mana = int(math.floor(self._mana_float))

    def find_first_empty_potion_slot(self) -> Optional[int]:
        empty_slots = [slot for slot in self.potion_slots if not self.potion_slots[slot]]
        if empty_slots:
            return empty_slots[0]
        return None

    def find_first_empty_item_slot(self) -> Optional[int]:
        empty_slots = [slot for slot in self.item_slots if not self.item_slots[slot]]
        if empty_slots:
            return empty_slots[0]
        return None

    def gain_buff_effect(self, buff: Any, duration: Millis):
        existing_buffs_with_this_type = [b for b in self.active_buffs
                                         if b.buff_effect.get_buff_type() == buff.get_buff_type()]
        if existing_buffs_with_this_type:
            existing_buffs_with_this_type[0].time_until_expiration = duration
        else:
            self.active_buffs.append(BuffWithDuration(buff, duration))

    def regenerate_mana(self, time_passed: Millis):
        self.gain_mana(
            self.mana_regen * float(time_passed))

    def recharge_ability_cooldowns(self, time_passed: Millis):
        for ability_type in self.ability_cooldowns_remaining:
            if self.ability_cooldowns_remaining[ability_type] > 0:
                self.ability_cooldowns_remaining[ability_type] -= time_passed


def handle_buffs(active_buffs: List[BuffWithDuration], time_passed: Millis):
    copied_buffs_list = list(active_buffs)
    buffs_that_started = []
    buffs_that_were_active = [b.buff_effect for b in copied_buffs_list]
    buffs_that_ended = []
    for buff in copied_buffs_list:
        buff.time_until_expiration -= time_passed
        if not buff.has_applied_start_effect:
            buffs_that_started.append(buff.buff_effect)
            buff.has_applied_start_effect = True
        elif buff.time_until_expiration <= 0:
            active_buffs.remove(buff)
            buffs_that_ended.append(buff.buff_effect)
    return AgentBuffsUpdate(buffs_that_started, buffs_that_were_active, buffs_that_ended)


class GameState:
    def __init__(self, player_entity: WorldEntity, potions_on_ground: List[PotionOnGround],
                 items_on_ground: List[ItemOnGround], enemies: List[Enemy],
                 walls: List[WorldEntity], camera_size: Tuple[int, int], game_world_size: Tuple[int, int],
                 player_state: PlayerState):
        self.camera_size = camera_size
        self.camera_world_area = WorldArea((0, 0), self.camera_size)
        self.player_entity = player_entity
        self.projectile_entities: List[Projectile] = []
        self.potions_on_ground = potions_on_ground
        self.items_on_ground = items_on_ground
        self.enemies = enemies
        self.walls = walls
        self._wall_buckets = self._put_walls_in_buckets(game_world_size, walls)
        self.visual_effects = []
        self.player_state: PlayerState = player_state
        self.game_world_size = game_world_size
        self.entire_world_area = WorldArea((0, 0), self.game_world_size)
        self.grid = self._setup_grid(game_world_size, walls)

    @staticmethod
    def _setup_grid(game_world_size: Tuple[int, int], walls: List[WorldEntity]):
        world_w = game_world_size[0]
        world_h = game_world_size[1]
        grid_width = world_w // GRID_CELL_WIDTH
        grid_height = world_h // GRID_CELL_WIDTH
        grid = []
        for x in range(grid_width):
            grid.append(grid_height * [0])
        for w in walls:
            cell_x = w.x // GRID_CELL_WIDTH
            cell_y = w.y // GRID_CELL_WIDTH
            grid[cell_x][cell_y] = 1

        return grid

    # entities_to_remove aren't necessarily of the class WorldEntity
    def remove_entities(self, entities_to_remove: List):
        self.projectile_entities = [p for p in self.projectile_entities if p not in entities_to_remove]
        self.potions_on_ground = [p for p in self.potions_on_ground if p not in entities_to_remove]
        self.items_on_ground = [i for i in self.items_on_ground if i not in entities_to_remove]
        self.enemies = [e for e in self.enemies if e not in entities_to_remove]

    def get_all_entities_to_render(self) -> List[WorldEntity]:
        walls = self._get_walls_from_buckets_in_camera()
        return [self.player_entity] + [p.world_entity for p in self.potions_on_ground] + \
               [i.world_entity for i in self.items_on_ground] + \
               [e.world_entity for e in self.enemies] + walls + [p.world_entity for p in self.projectile_entities]

    def center_camera_on_player(self):
        new_camera_pos = get_position_from_center_position(self.player_entity.get_center_position(), self.camera_size)
        new_camera_pos_within_world = self.get_within_world(new_camera_pos, (self.camera_size[0], self.camera_size[1]))
        self.camera_world_area.set_position(new_camera_pos_within_world)

    def translate_camera_position(self, translation_vector: Tuple[int, int]):
        new_camera_pos = (self.camera_world_area.x + translation_vector[0],
                          self.camera_world_area.y + translation_vector[1])
        new_camera_pos_within_world = self.get_within_world(new_camera_pos, (self.camera_size[0], self.camera_size[1]))
        self.camera_world_area.set_position(new_camera_pos_within_world)

    def get_projectiles_intersecting_with(self, entity) -> List[Projectile]:
        return [p for p in self.projectile_entities if boxes_intersect(entity, p.world_entity)]

    def get_enemies_intersecting_with(self, entity) -> List[Enemy]:
        return [e for e in self.enemies if boxes_intersect(e.world_entity, entity)]

    def get_enemies_within_x_y_distance_of(self, distance: int, position: Tuple[int, int]):
        return [e for e in self.enemies
                if is_x_and_y_within_distance(e.world_entity.get_center_position(), position, distance)]

    # NOTE: Very naive brute-force collision checking
    def update_world_entity_position_within_game_world(self, entity: WorldEntity, time_passed: Millis):
        new_position = entity.get_new_position_according_to_dir_and_speed(time_passed)
        if new_position:
            new_pos_within_world = self.get_within_world(new_position, (entity.w, entity.h))
            if not self.would_entity_collide_if_new_pos(entity, new_pos_within_world):
                entity.set_position(new_pos_within_world)

    # TODO Improve the interaction between functions in here
    def would_entity_collide_if_new_pos(self, entity, new_pos_within_world):
        old_pos = entity.x, entity.y
        entity.set_position(new_pos_within_world)
        walls = self._get_walls_from_buckets_adjacent_to_entity(entity)
        other_entities = [e.world_entity for e in self.enemies] + [self.player_entity] + walls
        collision = any([other for other in other_entities if self._entities_collide(entity, other)
                         and entity is not other])
        entity.set_position(old_pos)
        return collision

    def get_within_world(self, pos, size):
        return (max(0, min(self.game_world_size[0] - size[0], pos[0])),
                max(0, min(self.game_world_size[1] - size[1], pos[1])))

    def is_position_within_game_world(self, position: Tuple[int, int]) -> bool:
        return self.entire_world_area.contains_position(position)

    def remove_expired_projectiles(self):
        self.projectile_entities = [p for p in self.projectile_entities if not p.has_expired]

    def remove_dead_enemies(self):
        self.enemies = [e for e in self.enemies if e.health > 0]

    def remove_expired_visual_effects(self):
        self.visual_effects = [v for v in self.visual_effects if not v.has_expired]

    @staticmethod
    def _entities_collide(r1, r2):
        # Optimization: collision checking done with C-code from Pygame
        return r1.pygame_collision_rect.colliderect(r2.pygame_collision_rect)

    # Wall buckets:
    # Optimization for only checking collision with walls that are known beforehand (through use of buckets) to be
    # somewhat close to the entity
    @staticmethod
    def _put_walls_in_buckets(game_world_size: Tuple[int, int], walls: List[WorldEntity]):
        wall_buckets = {}
        for x_bucket in range(game_world_size[0] // WALL_BUCKET_WIDTH + 1):
            wall_buckets[x_bucket] = {}
            for y_bucket in range(game_world_size[1] // WALL_BUCKET_HEIGHT + 1):
                wall_buckets[x_bucket][y_bucket] = []
        for w in walls:
            x_bucket = int(w.x) // WALL_BUCKET_WIDTH
            y_bucket = int(w.y) // WALL_BUCKET_HEIGHT
            wall_buckets[x_bucket][y_bucket].append(w)
        return wall_buckets

    def add_wall(self, wall: WorldEntity):
        self.walls.append(wall)
        x_bucket = int(wall.x) // WALL_BUCKET_WIDTH
        y_bucket = int(wall.y) // WALL_BUCKET_HEIGHT
        self._wall_buckets[x_bucket][y_bucket].append(wall)

    def remove_wall(self, wall: WorldEntity):
        self.walls.remove(wall)
        x_bucket = int(wall.x) // WALL_BUCKET_WIDTH
        y_bucket = int(wall.y) // WALL_BUCKET_HEIGHT
        self._wall_buckets[x_bucket][y_bucket].remove(wall)

    def _get_walls_from_buckets_adjacent_to_entity(self, entity: WorldEntity):
        entity_x_bucket = int(entity.x) // WALL_BUCKET_WIDTH
        entity_y_bucket = int(entity.y) // WALL_BUCKET_HEIGHT
        walls = []
        for x_bucket in range(max(0, entity_x_bucket - 1), min(len(self._wall_buckets), entity_x_bucket + 2)):
            for y_bucket in range(max(0, entity_y_bucket - 1),
                                  min(len(self._wall_buckets[x_bucket]), entity_y_bucket + 2)):
                walls += self._wall_buckets[x_bucket][y_bucket]
        return walls

    def _get_walls_from_buckets_in_camera(self):
        x0_bucket = int(self.camera_world_area.x) // WALL_BUCKET_WIDTH
        y0_bucket = int(self.camera_world_area.y) // WALL_BUCKET_HEIGHT
        x1_bucket = int(self.camera_world_area.x + self.camera_world_area.w) // WALL_BUCKET_WIDTH
        y1_bucket = int(self.camera_world_area.y + self.camera_world_area.h) // WALL_BUCKET_HEIGHT
        walls = []
        for x_bucket in range(max(0, x0_bucket), min(x1_bucket + 1, len(self._wall_buckets))):
            for y_bucket in range(max(0, y0_bucket - 1), min(y1_bucket + 1, len(self._wall_buckets[x_bucket]))):
                walls += self._wall_buckets[x_bucket][y_bucket]
        return walls
