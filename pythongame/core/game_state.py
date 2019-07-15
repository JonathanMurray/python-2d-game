import math
from typing import List, Optional, Dict, Any, Tuple

from pygame.rect import Rect

from pythongame.core.common import *
from pythongame.core.consumable_inventory import ConsumableInventory
from pythongame.core.loot import LootTable
from pythongame.core.math import boxes_intersect, rects_intersect, get_position_from_center_position, \
    translate_in_direction, is_x_and_y_within_distance

GRID_CELL_WIDTH = 25

WALL_BUCKET_WIDTH = 100
WALL_BUCKET_HEIGHT = 100


class WorldArea:
    def __init__(self, pos: Tuple[int, int], size: Tuple[int, int]):
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]

    def get_position(self) -> Tuple[int, int]:
        return self.x, self.y

    def set_position(self, new_position):
        self.x = new_position[0]
        self.y = new_position[1]

    def rect(self) -> Tuple[int, int, int, int]:
        return self.x, self.y, self.w, self.h

    def contains_position(self, position: Tuple[int, int]) -> bool:
        return self.x <= position[0] <= self.x + self.w and self.y <= position[1] <= self.y + self.h


class WorldEntity:
    def __init__(self, pos: Tuple[int, int], size: Tuple[int, int], sprite: Sprite, direction=Direction.LEFT, speed=0):
        self.x: int = pos[0]
        self.y: int = pos[1]
        self.w: int = size[0]
        self.h: int = size[1]
        self.sprite: Sprite = sprite
        self.direction: Direction = direction
        self._speed = speed
        self.speed_multiplier = 1
        self._effective_speed = speed
        self._is_moving = True
        self.pygame_collision_rect = Rect(self.rect())
        self.movement_animation_progress: float = 0  # goes from 0 to 1 repeatedly
        self.visible = True  # Should only be used to control rendering

    def set_moving_in_dir(self, direction: Direction):
        if direction is None:
            raise Exception("Need to provide a valid direciton to move in")
        self.direction = direction
        self._is_moving = True

    def set_not_moving(self):
        self._is_moving = False

    def get_new_position_according_to_dir_and_speed(self, time_passed: Millis) -> Optional[Tuple[int, int]]:
        distance = self._effective_speed * time_passed
        if self._is_moving:
            return translate_in_direction((self.x, self.y), self.direction, distance)
        return None

    def update_movement_animation(self, time_passed: Millis):
        if self._is_moving:
            self.movement_animation_progress = (self.movement_animation_progress + float(time_passed) / 1000) % 1

    def get_new_position_according_to_other_dir_and_speed(self, direction: Direction, time_passed: Millis) \
            -> Optional[Tuple[int, int]]:
        distance = self._effective_speed * time_passed
        return translate_in_direction((self.x, self.y), direction, distance)

    def get_center_position(self) -> Tuple[int, int]:
        return int(self.x + self.w / 2), int(self.y + self.h / 2)

    def get_position(self) -> Tuple[int, int]:
        return int(self.x), int(self.y)

    def add_to_speed_multiplier(self, amount):
        self.speed_multiplier += amount
        self._effective_speed = self.speed_multiplier * self._speed

    # TODO use more
    def rect(self) -> Tuple[int, int, int, int]:
        return self.x, self.y, self.w, self.h

    def translate_x(self, amount):
        self.set_position((self.x + amount, self.y))

    def translate_y(self, amount):
        self.set_position((self.x, self.y + amount))

    def set_position(self, new_position: Tuple[int, int]):
        self.x = new_position[0]
        self.y = new_position[1]
        self.pygame_collision_rect = Rect(self.rect())

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


class LootableOnGround:
    def __init__(self, world_entity: WorldEntity):
        self.world_entity: WorldEntity = world_entity


class ConsumableOnGround(LootableOnGround):
    def __init__(self, world_entity: WorldEntity, consumable_type: ConsumableType):
        super().__init__(world_entity)
        self.consumable_type = consumable_type


class ItemOnGround(LootableOnGround):
    def __init__(self, world_entity: WorldEntity, item_type: ItemType):
        super().__init__(world_entity)
        self.item_type = item_type


class MoneyPileOnGround:
    def __init__(self, world_entity: WorldEntity, amount: int):
        self.world_entity = world_entity
        self.amount = amount


# TODO There is a cyclic dependency here between game_state and projectile_controllers
class Projectile:
    def __init__(self, world_entity: WorldEntity, projectile_controller):
        self.world_entity = world_entity
        self.has_expired = False
        self.projectile_controller = projectile_controller


class NonPlayerCharacter:
    def __init__(self, npc_type: NpcType, world_entity: WorldEntity, health: int, max_health: int,
                 health_regen: float, npc_mind, is_enemy: bool, is_neutral: bool,
                 enemy_loot_table: Optional[LootTable]):
        self.npc_type = npc_type
        self.world_entity = world_entity
        self._health_float = health
        self.health = health
        self.max_health = max_health
        self.health_regen = health_regen
        self.npc_mind = npc_mind
        self.active_buffs: List[BuffWithDuration] = []
        self.invulnerable: bool = False
        self._number_of_active_stuns = 0
        self.is_enemy = is_enemy
        self.is_neutral = is_neutral
        self.enemy_loot_table = enemy_loot_table

    def lose_health(self, amount: float):
        self._health_float = min(self._health_float - amount, self.max_health)
        self.health = int(math.floor(self._health_float))

    def lose_all_health(self):
        self._health_float = 0
        self.health = 0

    def gain_health(self, amount: float):
        self._health_float = min(self._health_float + amount, self.max_health)
        self.health = int(math.floor(self._health_float))

    # TODO There is a cyclic dependancy here between game_state and buff_effects
    def gain_buff_effect(self, buff: Any, duration: Millis):
        existing_buffs_with_this_type = [b for b in self.active_buffs
                                         if b.buff_effect.get_buff_type() == buff.get_buff_type()]
        if existing_buffs_with_this_type:
            existing_buffs_with_this_type[0].set_remaining_duration(duration)
        else:
            self.active_buffs.append(BuffWithDuration(buff, duration))

    def regenerate_health(self, time_passed: Millis):
        self.gain_health(self.health_regen / 1000.0 * float(time_passed))

    def add_stun(self):
        self._number_of_active_stuns += 1

    def remove_stun(self):
        self._number_of_active_stuns -= 1
        if self._number_of_active_stuns < 0:
            raise Exception("Number of active stuns went below 0 down to " + str(self._number_of_active_stuns))

    def is_stunned(self):
        return self._number_of_active_stuns > 0


class Wall:
    def __init__(self, wall_type: WallType, world_entity: WorldEntity):
        self.wall_type = wall_type
        self.world_entity = world_entity


# TODO There is a cyclic dependancy here between game_state and buff_effects
class BuffWithDuration:
    def __init__(self, buff_effect: Any, duration: Optional[Millis]):
        self.buff_effect = buff_effect
        self._time_until_expiration: Optional[Millis] = duration
        self.has_been_force_cancelled: bool = False
        self._total_duration: Optional[Millis] = duration
        self.has_applied_start_effect: bool = False

    def force_cancel(self):
        self.has_been_force_cancelled = True
        self._time_until_expiration = 0

    def notify_time_passed(self, time: Millis):
        self._time_until_expiration -= time

    def has_expired(self) -> bool:
        return self._time_until_expiration <= 0

    def get_ratio_duration_remaining(self) -> float:
        return self._time_until_expiration / self._total_duration

    def change_remaining_duration(self, delta: Millis):
        self._time_until_expiration = min(self._time_until_expiration + delta, self._total_duration)

    def set_remaining_duration(self, time: Millis):
        self._time_until_expiration = time

    def should_duration_be_visualized_on_enemies(self) -> bool:
        return self._total_duration > 1000


# These are sent as messages to player. They let buffs and items react to events. One buff might have its
# duration prolonged if an enemy dies for example, and an item might give mana on enemy kills.
class Event:
    pass


class EnemyDiedEvent(Event):
    pass


class PlayerUsedAbilityEvent(Event):
    def __init__(self, ability: AbilityType):
        self.ability = ability


class PlayerLostHealthEvent(Event):
    def __init__(self, amount: int, npc_attacker: Optional[NonPlayerCharacter]):
        self.amount = amount
        self.npc_attacker = npc_attacker


class PlayerDamagedEnemy(Event):
    def __init__(self, enemy_npc: NonPlayerCharacter, damage_source: Optional[str]):
        self.enemy_npc = enemy_npc
        self.damage_source = damage_source


class BuffEventOutcome:
    def __init__(self, change_remaining_duration: Optional[Millis], cancel_effect: bool):
        self.change_remaining_duration = change_remaining_duration
        self.cancel_effect = cancel_effect

    @staticmethod
    def change_remaining_duration(delta: Millis):
        return BuffEventOutcome(delta, False)

    @staticmethod
    def cancel_effect():
        return BuffEventOutcome(None, True)


class PlayerState:
    def __init__(self, health: int, max_health: int, mana: int, max_mana: int, mana_regen: float,
                 consumable_inventory: ConsumableInventory, abilities: List[AbilityType],
                 item_slots: Dict[int, Any], new_level_abilities: Dict[int, AbilityType], hero_id: HeroId, armor: int):
        self.health = health
        self._health_float = health
        self.max_health = max_health
        self.health_regen: float = 0
        self.mana = mana
        self._mana_float = mana
        self.max_mana = max_mana
        self.mana_regen: float = mana_regen
        self.consumable_inventory = consumable_inventory
        self.abilities: List[AbilityType] = abilities
        self.ability_cooldowns_remaining = {ability_type: 0 for ability_type in abilities}
        self.active_buffs: List[BuffWithDuration] = []
        self.is_invisible = False
        self._number_of_active_stuns = 0
        self.item_slots = item_slots  # Values are of type AbstractItemEffect
        self.life_steal_ratio: float = 0
        self.exp = 0
        self.level = 1
        self.max_exp_in_this_level = 60
        self.fireball_dmg_boost = 0
        self.new_level_abilities: Dict[int, AbilityType] = new_level_abilities
        self.money = 0
        self.base_damage_modifier: float = 1  # only affected by level. Changes multiplicatively
        self.damage_modifier_bonus: float = 0  # affected by items. Only allowed to change additively
        self.hero_id: HeroId = hero_id
        self.armor: int = armor

    def gain_health(self, amount: float) -> int:
        health_before = self.health
        self._health_float = min(self._health_float + amount, self.max_health)
        self.health = int(math.floor(self._health_float))
        health_gained = self.health - health_before
        return health_gained

    def lose_health(self, amount: float) -> int:
        health_before = self.health
        self._health_float = max(self._health_float - amount, 0)
        self.health = int(math.floor(self._health_float))
        health_lost = health_before - self.health
        return health_lost

    def gain_mana(self, amount: float):
        self._mana_float = min(self._mana_float + amount, self.max_mana)
        self.mana = int(math.floor(self._mana_float))

    def lose_mana(self, amount: float):
        self._mana_float -= amount
        self.mana = int(math.floor(self._mana_float))

    def gain_full_health(self):
        self._health_float = self.max_health
        self.health = self.max_health

    def gain_full_mana(self):
        self._mana_float = self.max_mana
        self.mana = self.max_mana

    def gain_max_mana(self, amount: int):
        self.max_mana += amount

    def lose_max_mana(self, amount: int):
        self.max_mana -= amount
        if self.mana > self.max_mana:
            self._mana_float = self.max_mana
            self.mana = int(math.floor(self._mana_float))

    def gain_max_health(self, amount: int):
        self.max_health += amount

    def lose_max_health(self, amount: int):
        self.max_health -= amount
        if self.health > self.max_health:
            self._health_float = self.max_health
            self.health = int(math.floor(self._health_float))

    def find_first_empty_item_slot(self) -> Optional[int]:
        empty_slots = [slot for slot in self.item_slots if not self.item_slots[slot]]
        if empty_slots:
            return empty_slots[0]
        return None

    # TODO There is a cyclic dependancy here between game_state and buff_effects
    def gain_buff_effect(self, buff: Any, duration: Millis):
        existing_buffs_with_this_type = [b for b in self.active_buffs
                                         if b.buff_effect.get_buff_type() == buff.get_buff_type()]
        if existing_buffs_with_this_type:
            existing_buffs_with_this_type[0].set_remaining_duration(duration)
        else:
            self.active_buffs.append(BuffWithDuration(buff, duration))

    def regenerate_health_and_mana(self, time_passed: Millis):
        self.gain_mana(self.mana_regen / 1000.0 * float(time_passed))
        self.gain_health(self.health_regen / 1000.0 * float(time_passed))

    def recharge_ability_cooldowns(self, time_passed: Millis):
        for ability_type in self.ability_cooldowns_remaining:
            if self.ability_cooldowns_remaining[ability_type] > 0:
                self.ability_cooldowns_remaining[ability_type] -= time_passed

    def switch_item_slots(self, slot_1: int, slot_2: int):
        item_type_1 = self.item_slots[slot_1]
        self.item_slots[slot_1] = self.item_slots[slot_2]
        self.item_slots[slot_2] = item_type_1

    # returns True if player leveled up
    def gain_exp(self, amount: int):
        self.exp += amount
        did_level_up = self.exp >= self.max_exp_in_this_level
        while self.exp >= self.max_exp_in_this_level:
            self.exp -= self.max_exp_in_this_level
            self.level += 1
            self.update_stats_for_new_level()
            if self.level in self.new_level_abilities:
                new_ability = self.new_level_abilities[self.level]
                self.gain_ability(new_ability)
        return did_level_up

    def gain_exp_worth_n_levels(self, num_levels: int):
        for i in range(num_levels):
            amount = self.max_exp_in_this_level - self.exp
            self.gain_exp(amount)

    def update_stats_for_new_level(self):
        self.max_health += 7
        self.max_mana += 5
        self.gain_full_health()
        self.gain_full_mana()
        self.max_exp_in_this_level = int(self.max_exp_in_this_level * 1.4)
        self.base_damage_modifier *= 1.1

    def gain_ability(self, ability_type: AbilityType):
        self.ability_cooldowns_remaining[ability_type] = 0
        self.abilities.append(ability_type)

    def add_stun(self):
        self._number_of_active_stuns += 1

    def remove_stun(self):
        self._number_of_active_stuns -= 1
        if self._number_of_active_stuns < 0:
            raise Exception("Number of active stuns went below 0 down to " + str(self._number_of_active_stuns))

    def is_stunned(self):
        return self._number_of_active_stuns > 0

    def notify_about_event(self, event: Event):
        for buff in self.active_buffs:
            outcome: Optional[BuffEventOutcome] = buff.buff_effect.buff_handle_event(event)
            if outcome:
                if outcome.change_remaining_duration:
                    buff.change_remaining_duration(outcome.change_remaining_duration)
                if outcome.cancel_effect:
                    buff.force_cancel()
        for item_effect in self.item_slots.values():
            if item_effect:
                item_effect.item_handle_event(event, self)


# TODO Is there a way to handle this better in the view module? This class shouldn't need to masquerade as a WorldEntity
class DecorationEntity:
    def __init__(self, pos: Tuple[int, int], sprite: Sprite):
        self.x = pos[0]
        self.y = pos[1]
        self.sprite = sprite
        # The fields below are needed for the view module to be able to handle this class the same as WorldEntity
        self.direction = Direction.DOWN  # The view module uses direction to determine which image to render
        self.movement_animation_progress: float = 0  # The view module uses this to determine which frame to render
        self.visible = True  # Should only be used to control rendering

    def rect(self):
        # Used by view module in map_editor
        return self.x, self.y, 0, 0

    def get_position(self):
        return self.x, self.y


class Portal:
    def __init__(self, world_entity: WorldEntity, portal_id: PortalId, is_enabled: bool, leads_to: Optional[PortalId]):
        self.world_entity = world_entity
        self.portal_id = portal_id
        self.is_enabled = is_enabled
        self.leads_to = leads_to


class GameState:
    def __init__(self, player_entity: WorldEntity, consumables_on_ground: List[ConsumableOnGround],
                 items_on_ground: List[ItemOnGround], money_piles_on_ground: List[MoneyPileOnGround],
                 non_player_characters: List[NonPlayerCharacter], walls: List[Wall], camera_size: Tuple[int, int],
                 game_world_size: Tuple[int, int], player_state: PlayerState,
                 decoration_entities: List[DecorationEntity], portals: List[Portal]):
        self.camera_size = camera_size
        self.camera_world_area = WorldArea((0, 0), self.camera_size)
        self.player_entity = player_entity
        self.projectile_entities: List[Projectile] = []
        # TODO: unify code for picking up stuff from the ground. The way they are rendered and picked up are similar,
        # and only the effect of picking them up is different.
        self.consumables_on_ground: List[ConsumableOnGround] = consumables_on_ground
        self.items_on_ground: List[ItemOnGround] = items_on_ground
        self.money_piles_on_ground: List[MoneyPileOnGround] = money_piles_on_ground
        self.non_player_characters: List[NonPlayerCharacter] = non_player_characters
        # overlaps with non_player_characters
        self.non_enemy_npcs: List[NonPlayerCharacter] = [npc for npc in non_player_characters if not npc.is_enemy]
        self.walls: List[Wall] = walls
        self._wall_buckets = self._put_walls_in_buckets(game_world_size, [w.world_entity for w in walls])
        self.visual_effects = []
        self.player_state: PlayerState = player_state
        self.game_world_size = game_world_size
        self.entire_world_area = WorldArea((0, 0), self.game_world_size)
        self.grid = self._setup_grid(game_world_size, [w.world_entity for w in walls])
        self.decoration_entities = decoration_entities
        self.portals: List[Portal] = portals

    @staticmethod
    def _setup_grid(game_world_size: Tuple[int, int], walls: List[WorldEntity]):
        world_w = game_world_size[0]
        world_h = game_world_size[1]
        grid_width = world_w // GRID_CELL_WIDTH
        grid_height = world_h // GRID_CELL_WIDTH
        grid = []
        for x in range(grid_width + 1):
            grid.append((grid_height + 1) * [0])
        for w in walls:
            cell_x = w.x // GRID_CELL_WIDTH
            cell_y = w.y // GRID_CELL_WIDTH
            grid[cell_x][cell_y] = 1

        return grid

    def add_non_player_character(self, npc: NonPlayerCharacter):
        self.non_player_characters.append(npc)
        if not npc.is_enemy:
            self.non_enemy_npcs.append(npc)

    def remove_all_non_enemy_npcs(self):
        self.non_player_characters = [npc for npc in self.non_player_characters if npc not in self.non_enemy_npcs]
        self.non_enemy_npcs = []

    # TODO clarify how this method should be used.
    # entities_to_remove aren't necessarily of the class WorldEntity
    def remove_entities(self, entities_to_remove: List):
        self.projectile_entities = [p for p in self.projectile_entities if p not in entities_to_remove]
        self.consumables_on_ground = [p for p in self.consumables_on_ground if p not in entities_to_remove]
        self.items_on_ground = [i for i in self.items_on_ground if i not in entities_to_remove]
        self.money_piles_on_ground = [m for m in self.money_piles_on_ground if m not in entities_to_remove]
        self.non_player_characters = [e for e in self.non_player_characters if e not in entities_to_remove]

    def get_all_entities_to_render(self) -> List[WorldEntity]:
        walls = self._get_walls_from_buckets_in_camera()
        return [self.player_entity] + \
               [p.world_entity for p in self.consumables_on_ground] + \
               [i.world_entity for i in self.items_on_ground] + \
               [m.world_entity for m in self.money_piles_on_ground] + \
               [e.world_entity for e in self.non_player_characters] + \
               walls + \
               [p.world_entity for p in self.projectile_entities] + \
               [p.world_entity for p in self.portals]

    def get_decorations_to_render(self) -> List[DecorationEntity]:
        return self.decoration_entities

    def center_camera_on_player(self):
        new_camera_pos = get_position_from_center_position(self.player_entity.get_center_position(), self.camera_size)
        new_camera_pos_within_world = self.get_within_world(new_camera_pos, (self.camera_size[0], self.camera_size[1]))
        self.camera_world_area.set_position(new_camera_pos_within_world)

    def translate_camera_position(self, translation_vector: Tuple[int, int]):
        new_camera_pos = (self.camera_world_area.x + translation_vector[0],
                          self.camera_world_area.y + translation_vector[1])
        new_camera_pos_within_world = self.get_within_world(new_camera_pos, (self.camera_size[0], self.camera_size[1]))
        self.camera_world_area.set_position(new_camera_pos_within_world)

    def get_projectiles_intersecting_with(self, entity: WorldEntity) -> List[Projectile]:
        return [p for p in self.projectile_entities if boxes_intersect(entity, p.world_entity)]

    def get_enemy_intersecting_with(self, entity: WorldEntity) -> List[NonPlayerCharacter]:
        return [e for e in self.non_player_characters if e.is_enemy and boxes_intersect(e.world_entity, entity)]

    def get_enemy_intersecting_rect(self, rect: Tuple[int, int, int, int]):
        return [e for e in self.non_player_characters if e.is_enemy and rects_intersect(e.world_entity.rect(), rect)]

    def get_enemies_within_x_y_distance_of(self, distance: int, position: Tuple[int, int]):
        return [e for e in self.non_player_characters
                if e.is_enemy
                and is_x_and_y_within_distance(e.world_entity.get_center_position(), position, distance)]

    # NOTE: Very naive brute-force collision checking
    def update_world_entity_position_within_game_world(self, entity: WorldEntity, time_passed: Millis):
        new_position = entity.get_new_position_according_to_dir_and_speed(time_passed)
        if new_position:
            new_pos_within_world = self.get_within_world(new_position, (entity.w, entity.h))
            if not self.would_entity_collide_if_new_pos(entity, new_pos_within_world):
                entity.set_position(new_pos_within_world)

    # TODO Improve the interaction between functions in here
    def would_entity_collide_if_new_pos(self, entity, new_pos_within_world):
        if not self.is_position_within_game_world(new_pos_within_world):
            raise Exception("not within game-world: " + str(new_pos_within_world))
        old_pos = entity.x, entity.y
        entity.set_position(new_pos_within_world)
        walls = self._get_walls_from_buckets_adjacent_to_entity(entity)
        other_entities = [e.world_entity for e in self.non_player_characters] + \
                         [self.player_entity] + walls + [p.world_entity for p in self.portals]
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

    def remove_dead_npcs(self) -> List[NonPlayerCharacter]:
        npcs_that_died = [e for e in self.non_player_characters if e.health <= 0]
        self.non_enemy_npcs = [npc for npc in self.non_enemy_npcs if npc.health > 0]
        self.non_player_characters = [e for e in self.non_player_characters if e.health > 0]
        return npcs_that_died

    def remove_expired_visual_effects(self):
        self.visual_effects = [v for v in self.visual_effects if not v.has_expired]

    @staticmethod
    def _entities_collide(a: WorldEntity, b: WorldEntity):
        # Optimization: collision checking done with C-code from Pygame
        return a.pygame_collision_rect.colliderect(b.pygame_collision_rect)

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

    def add_wall(self, wall: Wall):
        self.walls.append(wall)
        x_bucket = int(wall.world_entity.x) // WALL_BUCKET_WIDTH
        y_bucket = int(wall.world_entity.y) // WALL_BUCKET_HEIGHT
        self._wall_buckets[x_bucket][y_bucket].append(wall.world_entity)

    def remove_wall(self, wall: Wall):
        self.walls.remove(wall)
        x_bucket = int(wall.world_entity.x) // WALL_BUCKET_WIDTH
        y_bucket = int(wall.world_entity.y) // WALL_BUCKET_HEIGHT
        self._wall_buckets[x_bucket][y_bucket].remove(wall.world_entity)

    def does_entity_intersect_with_wall(self, entity: WorldEntity):
        nearby_walls = self._get_walls_from_buckets_adjacent_to_entity(entity)
        return any([w for w in nearby_walls if boxes_intersect(w, entity)])

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
