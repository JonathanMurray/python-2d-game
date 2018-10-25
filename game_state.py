import math
from common import *


class Potion:
    def __init__(self, world_entity, potion_type):
        self.world_entity = world_entity
        self.potion_type = potion_type


class WorldArea:
    def __init__(self, pos, size):
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]


class WorldEntity:
    def __init__(self, pos, size, color, direction=Direction.LEFT, speed=0, max_speed=0):
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]
        self.color = color
        self.direction = direction
        self.speed = speed
        self.max_speed = max_speed

    def set_moving_in_dir(self, direction):
        self.direction = direction
        self.speed = self.max_speed

    def set_not_moving(self):
        self.speed = 0

    def update_position_according_to_dir_and_speed(self):
        if self.direction == Direction.LEFT:
            self.x -= self.speed
        elif self.direction == Direction.RIGHT:
            self.x += self.speed
        elif self.direction == Direction.UP:
            self.y -= self.speed
        elif self.direction == Direction.DOWN:
            self.y += self.speed

    def get_center_x(self):
        return self.x + self.w / 2

    def get_center_y(self):
        return self.y + self.h / 2


class Projectile:
    def __init__(self, world_entity, time_until_active, time_until_expiration):
        self.world_entity = world_entity
        self.time_until_active = time_until_active
        self.time_until_expiration = time_until_expiration
        self.active = self.time_until_active <= 0
        self.has_expired = self.time_until_expiration <= 0

    def notify_time_passed(self, time_passed):
        self.time_until_active -= time_passed
        self.active = self.time_until_active <= 0
        self.time_until_expiration -= time_passed
        self.has_expired = self.time_until_expiration <= 0


class Enemy:
    def __init__(self, world_entity, health, max_health, enemy_behavior):
        self.world_entity = world_entity
        self.health = health
        self.max_health = max_health
        self.enemy_behavior = enemy_behavior


class PlayerStats:
    def __init__(self, health, max_health, mana, max_mana, mana_regen):
        self.health = health
        self.max_health = max_health
        self.mana = mana
        self._mana_float = mana
        self.max_mana = max_mana
        self.mana_regen = mana_regen
        self.potion_slots = {
            1: PotionType.HEALTH,
            2: None,
            3: PotionType.HEALTH,
            4: PotionType.MANA,
            5: PotionType.MANA
        }

    def gain_health(self, amount):
        self.health = min(self.health + amount, self.max_health)

    def lose_health(self, amount):
        self.health -= amount

    def gain_mana(self, amount):
        self._mana_float = min(self._mana_float + amount, self.max_mana)
        self.mana = int(math.floor(self._mana_float))

    def lose_mana(self, amount):
        self._mana_float -= amount
        self.mana = int(math.floor(self._mana_float))

    def try_use_potion(self, number):
        if self.potion_slots[number] == PotionType.HEALTH:
            self.gain_health(10)
        elif self.potion_slots[number] == PotionType.MANA:
            self.gain_mana(25)
        self.potion_slots[number] = None

    # Returns whether or not potion was picked up (not picked up if no space for it)
    def try_pick_up_potion(self, potion_type):
        empty_slots = [slot for slot in self.potion_slots if not self.potion_slots[slot]]
        if len(empty_slots) > 0:
            slot = empty_slots[0]
            self.potion_slots[slot] = potion_type
            return True
        else:
            return False


class GameState:
    def __init__(self, player_entity, potions, enemies, camera_size, game_world_size):
        self.camera_size = camera_size
        self.camera_world_area = WorldArea((0, 0), self.camera_size)
        self.player_entity = player_entity
        self.projectile_entities = []
        self.potions = potions
        self.enemies = enemies
        self.player_stats = PlayerStats(3, 20, 50, 100, 0.03)
        self.game_world_size = game_world_size
        self.entire_world_area = WorldArea((0, 0), self.game_world_size)

    # entities_to_remove aren't necessarily of the class WorldEntity
    def remove_entities(self, entities_to_remove):
        self.projectile_entities = [p for p in self.projectile_entities if p not in entities_to_remove]
        self.potions = [p for p in self.potions if p not in entities_to_remove]
        self.enemies = [e for e in self.enemies if e not in entities_to_remove]

    def get_all_entities(self):
        return [self.player_entity] + [p.world_entity for p in self.projectile_entities] + \
               [p.world_entity for p in self.potions] + [e.world_entity for e in self.enemies]

    def center_camera_on_player(self):
        self.camera_world_area.x = min(max(self.player_entity.x - self.camera_size[0] / 2, 0),
                                       self.game_world_size[0] - self.camera_size[0])
        self.camera_world_area.y = min(max(self.player_entity.y - self.camera_size[1] / 2, 0),
                                       self.game_world_size[1] - self.camera_size[1])

    def get_all_active_projectiles_that_intersect_with(self, entity):
        return [p for p in self.projectile_entities if boxes_intersect(entity, p.world_entity) and p.active]

    def update_world_entity_position_within_game_world(self, world_entity):
        world_entity.update_position_according_to_dir_and_speed()
        world_entity.x = min(max(world_entity.x, 0), self.game_world_size[0] - world_entity.w)
        world_entity.y = min(max(world_entity.y, 0), self.game_world_size[1] - world_entity.h)

    def is_within_game_world(self, box):
        return boxes_intersect(box, self.entire_world_area)
