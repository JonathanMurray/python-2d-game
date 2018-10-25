import math
from common import Direction, boxes_intersect


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


class Enemy:
    def __init__(self, world_entity, health, max_health):
        self.world_entity = world_entity
        self.health = health
        self.max_health = max_health


class PlayerStats:
    def __init__(self, health, max_health, mana, max_mana, mana_regen):
        self.health = health
        self.max_health = max_health
        self.mana = mana
        self._mana_float = mana
        self.max_mana = max_mana
        self.mana_regen = mana_regen
        self.health_potion_slots = {
            1: True,
            2: False,
            3: True,
            4: True,
            5: True
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

    def try_use_health_potion(self, number):
        if self.health_potion_slots[number]:
            self.health_potion_slots[number] = False
            self.gain_health(10)

    # Returns whether or not potion was picked up (not picked up if no space for it)
    def try_pick_up_potion(self):
        empty_slots = [slot for slot in self.health_potion_slots if not self.health_potion_slots[slot]]
        if len(empty_slots) > 0:
            slot = empty_slots[0]
            self.health_potion_slots[slot] = True
            return True
        else:
            return False


class PlayerAbilityStats:
    def __init__(self, heal_ability_mana_cost, heal_ability_amount, attack_ability_mana_cost, attack_projectile_size,
                 attack_projectile_color, attack_projectile_speed):
        self.heal_ability_mana_cost = heal_ability_mana_cost
        self.heal_ability_amount = heal_ability_amount
        self.attack_ability_mana_cost = attack_ability_mana_cost
        self.attack_projectile_size = attack_projectile_size
        self.attack_projectile_color = attack_projectile_color
        self.attack_projectile_speed = attack_projectile_speed


class GameState:
    def __init__(self, player_entity, potion_entities, enemies, camera_size, game_world_size, player_ability_stats):
        self.camera_size = camera_size
        self.camera_world_area = WorldArea((0, 0), self.camera_size)
        self.player_entity = player_entity
        self.projectile_entities = []
        self.potion_entities = potion_entities
        self.enemies = enemies
        self.player_stats = PlayerStats(3, 20, 50, 100, 0.03)
        self.game_world_size = game_world_size
        self.player_ability_stats = player_ability_stats
        self.entire_world_area = WorldArea((0, 0), self.game_world_size)

    def remove_entities(self, entities_to_remove):
        self.projectile_entities = [p for p in self.projectile_entities if p not in entities_to_remove]
        self.potion_entities = [p for p in self.potion_entities if p not in entities_to_remove]
        self.enemies = [e for e in self.enemies if e not in entities_to_remove]

    def try_use_heal_ability(self):
        if self.player_stats.mana >= self.player_ability_stats.heal_ability_mana_cost:
            self.player_stats.lose_mana(self.player_ability_stats.heal_ability_mana_cost)
            self.player_stats.gain_health(self.player_ability_stats.heal_ability_amount)

    def try_use_attack_ability(self):
        if self.player_stats.mana >= self.player_ability_stats.attack_ability_mana_cost:
            self.player_stats.lose_mana(self.player_ability_stats.attack_ability_mana_cost)
            proj_pos = (self.player_entity.get_center_x() - self.player_ability_stats.attack_projectile_size[0] / 2,
                        self.player_entity.get_center_y() - self.player_ability_stats.attack_projectile_size[1] / 2)
            self.projectile_entities.append(WorldEntity(
                proj_pos, self.player_ability_stats.attack_projectile_size,
                self.player_ability_stats.attack_projectile_color, self.player_entity.direction,
                self.player_ability_stats.attack_projectile_speed, self.player_ability_stats.attack_projectile_speed))

    def get_all_entities(self):
        return [self.player_entity] + self.projectile_entities + self.potion_entities + [e.world_entity for e in
                                                                                         self.enemies]

    def center_camera_on_player(self):
        self.camera_world_area.x = min(max(self.player_entity.x - self.camera_size[0] / 2, 0),
                                       self.game_world_size[0] - self.camera_size[0])
        self.camera_world_area.y = min(max(self.player_entity.y - self.camera_size[1] / 2, 0),
                                       self.game_world_size[1] - self.camera_size[1])

    def get_all_projectiles_that_intersect_with(self, entity):
        return [p for p in self.projectile_entities if boxes_intersect(entity, p)]

    def update_world_entity_position_within_game_world(self, world_entity):
        world_entity.update_position_according_to_dir_and_speed()
        world_entity.x = min(max(world_entity.x, 0), self.game_world_size[0] - world_entity.w)
        world_entity.y = min(max(world_entity.y, 0), self.game_world_size[1] - world_entity.h)

    def is_within_game_world(self, box):
        return boxes_intersect(box, self.entire_world_area)
