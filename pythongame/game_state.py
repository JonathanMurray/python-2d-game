import math
from typing import Tuple, List

from pythongame.common import *


class WorldArea:
    def __init__(self, pos: Tuple[int, int], size: Tuple[int, int]):
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]


class WorldEntity:
    def __init__(self, pos: Tuple[int, int], size: Tuple[int, int], sprite: Sprite, direction=Direction.LEFT, speed=0):
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]
        self.sprite = sprite
        self.direction = direction
        self._speed = speed
        self._speed_multiplier = 1
        self._effective_speed = speed
        self._is_moving = True

    def set_moving_in_dir(self, direction):
        self.direction = direction
        self._is_moving = True

    def set_not_moving(self):
        self._is_moving = False

    def update_position_according_to_dir_and_speed(self, time_passed):
        distance = self._effective_speed * time_passed / 25  # 25 because this was the avg. frame duration before this change
        if self._is_moving:
            if self.direction == Direction.LEFT:
                self.x -= distance
            elif self.direction == Direction.RIGHT:
                self.x += distance
            elif self.direction == Direction.UP:
                self.y -= distance
            elif self.direction == Direction.DOWN:
                self.y += distance

    def get_center_position(self):
        return self.x + self.w / 2, self.y + self.h / 2

    def add_to_speed_multiplier(self, amount):
        self._speed_multiplier += amount
        self._effective_speed = self._speed_multiplier * self._speed


class PotionOnGround:
    def __init__(self, world_entity: WorldEntity, potion_type: PotionType):
        self.world_entity = world_entity
        self.potion_type = potion_type


class Projectile:
    def __init__(self, world_entity: WorldEntity, projectile_controller):
        self.world_entity = world_entity
        self.has_expired = False
        self.projectile_controller = projectile_controller


class Enemy:
    def __init__(self, world_entity: WorldEntity, health: int, max_health: int, enemy_mind):
        self.world_entity = world_entity
        self.health = health
        self.max_health = max_health
        self.enemy_mind = enemy_mind

    def lose_health(self, amount):
        self.health = max(self.health - amount, 0)

    def gain_health(self, amount):
        self.health = min(self.health + amount, self.max_health)


class VisualLine:
    def __init__(self, color: Tuple[int, int, int], start_position: Tuple[int, int], end_position: Tuple[int, int],
                 max_age: int):
        self._age = 0
        self._max_age = max_age
        self.color = color
        self.start_position = start_position
        self.end_position = end_position
        self.has_expired = False

    def notify_time_passed(self, time_passed: int):
        self._age += time_passed
        if self._age > self._max_age:
            self.has_expired = True


class Buff:
    def __init__(self, buff_type: BuffType, time_until_expiration: int):
        self.buff_type = buff_type
        self.time_until_expiration = time_until_expiration
        self.has_applied_start_effect = False


class PlayerBuffsUpdate:
    def __init__(self, buffs_that_started: List[BuffType], active_buffs: List[BuffType],
                 buffs_that_ended: List[BuffType]):
        self.buffs_that_started = buffs_that_started
        self.active_buffs = active_buffs
        self.buffs_that_ended = buffs_that_ended


class PlayerState:
    def __init__(self, health: int, max_health: int, mana: int, max_mana: int, mana_regen: float,
                 potion_slots: List[PotionType], abilities: List[AbilityType]):
        self.health = health
        self._health_float = health
        self.max_health = max_health
        self.mana = mana
        self._mana_float = mana
        self.max_mana = max_mana
        self.mana_regen = mana_regen
        self.potion_slots = potion_slots
        self.abilities = abilities
        self.active_buffs = []
        self.is_invisible = False

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

    # Returns whether or not potion was picked up (not picked up if no space for it)
    def try_pick_up_potion(self, potion_type: PotionType):
        empty_slots = [slot for slot in self.potion_slots if not self.potion_slots[slot]]
        if len(empty_slots) > 0:
            slot = empty_slots[0]
            self.potion_slots[slot] = potion_type
            return True
        else:
            return False

    def update_and_expire_buffs(self, time_passed: int):
        copied_buffs_list = list(self.active_buffs)
        buffs_that_started = []
        buffs_that_ended = []
        for buff in copied_buffs_list:
            buff.time_until_expiration -= time_passed
            if not buff.has_applied_start_effect:
                buffs_that_started.append(buff.buff_type)
                buff.has_applied_start_effect = True
            elif buff.time_until_expiration <= 0:
                self.active_buffs.remove(buff)
                buffs_that_ended.append(buff.buff_type)
        return PlayerBuffsUpdate(buffs_that_started, [e.buff_type for e in copied_buffs_list], buffs_that_ended)

    def add_buff(self, buff_type: BuffType, duration: int):
        existing_buffs_with_this_type = [e for e in self.active_buffs if e.buff_type == buff_type]
        if existing_buffs_with_this_type:
            existing_buffs_with_this_type[0].time_until_expiration = duration
        else:
            self.active_buffs.append(Buff(buff_type, duration))

    def regenerate_mana(self, time_passed: int):
        self.gain_mana(
            self.mana_regen * time_passed / 25)  # 25 because this was the avg. frame duration before this change


class GameState:
    def __init__(self, player_entity: WorldEntity, potions_on_ground: List[PotionOnGround], enemies: List[Enemy],
                 camera_size: Tuple[int, int], game_world_size: Tuple[int, int], player_state: PlayerState):
        self.camera_size = camera_size
        self.camera_world_area = WorldArea((0, 0), self.camera_size)
        self.player_entity = player_entity
        self.projectile_entities = []
        self.potions_on_ground = potions_on_ground
        self.enemies = enemies
        self.visual_lines = []
        self.player_state = player_state
        self.game_world_size = game_world_size
        self.entire_world_area = WorldArea((0, 0), self.game_world_size)

    # entities_to_remove aren't necessarily of the class WorldEntity
    def remove_entities(self, entities_to_remove: List):
        self.projectile_entities = [p for p in self.projectile_entities if p not in entities_to_remove]
        self.potions_on_ground = [p for p in self.potions_on_ground if p not in entities_to_remove]
        self.enemies = [e for e in self.enemies if e not in entities_to_remove]

    def get_all_entities(self):
        return [self.player_entity] + [p.world_entity for p in self.projectile_entities] + \
               [p.world_entity for p in self.potions_on_ground] + [e.world_entity for e in self.enemies]

    def center_camera_on_player(self):
        player_center_position = self.player_entity.get_center_position()
        self.camera_world_area.x = min(max(player_center_position[0] - self.camera_size[0] / 2, 0),
                                       self.game_world_size[0] - self.camera_size[0])
        self.camera_world_area.y = min(max(player_center_position[1] - self.camera_size[1] / 2, 0),
                                       self.game_world_size[1] - self.camera_size[1])

    def get_projectiles_intersecting_with(self, entity):
        return [p for p in self.projectile_entities if boxes_intersect(entity, p.world_entity)]

    def update_world_entity_position_within_game_world(self, world_entity: WorldEntity, time_passed: int):
        world_entity.update_position_according_to_dir_and_speed(time_passed)
        world_entity.x = min(max(world_entity.x, 0), self.game_world_size[0] - world_entity.w)
        world_entity.y = min(max(world_entity.y, 0), self.game_world_size[1] - world_entity.h)

    def is_within_game_world(self, box):
        return boxes_intersect(box, self.entire_world_area)

    def remove_expired_projectiles(self):
        self.projectile_entities = [p for p in self.projectile_entities if not p.has_expired]

    def remove_dead_enemies(self):
        self.enemies = [e for e in self.enemies if e.health > 0]

    def remove_expired_visual_lines(self):
        self.visual_lines = [v for v in self.visual_lines if not v.has_expired]
