from pythongame.core.ability_learning import player_learn_new_ability
from pythongame.core.common import *
from pythongame.core.entity_creation import create_money_pile_on_ground, create_item_on_ground, \
    create_consumable_on_ground
from pythongame.core.game_data import CONSUMABLES, ITEMS, NON_PLAYER_CHARACTERS
from pythongame.core.game_state import GameState, handle_buffs
from pythongame.core.item_effects import get_item_effect
from pythongame.core.player_controls import PlayerControls
from pythongame.core.sound_player import play_sound
from pythongame.core.view_state import ViewState
from pythongame.core.visual_effects import create_visual_exp_text


class GameEngine:

    def __init__(self, game_state: GameState, view_state: ViewState):
        self.game_state = game_state
        self.player_controls = PlayerControls()
        self.view_state = view_state

    def initialize(self):
        for item_type in self.game_state.player_state.item_slots.values():
            if item_type:
                item_effect = get_item_effect(item_type)
                item_effect.apply_start_effect(self.game_state)

    def try_use_ability(self, ability_type: AbilityType):
        self.player_controls.try_use_ability(ability_type, self.game_state, self.view_state)

    def try_use_consumable(self, slot_number: int):
        self.player_controls.try_use_consumable(slot_number, self.game_state, self.view_state)

    def move_in_direction(self, direction: Direction):
        if not self.game_state.player_state.is_stunned:
            self.game_state.player_entity.set_moving_in_dir(direction)

    def stop_moving(self):
        self.game_state.player_entity.set_not_moving()

    def switch_inventory_items(self, slot_1: int, slot_2: int):
        self.game_state.player_state.switch_item_slots(slot_1, slot_2)

    def switch_consumable_slots(self, slot_1: int, slot_2):
        self.game_state.player_state.switch_consumable_slots(slot_1, slot_2)

    def drop_inventory_item_on_ground(self, item_slot: int, game_world_position: Tuple[int, int]):
        item_type = self.game_state.player_state.item_slots[item_slot]
        item = create_item_on_ground(item_type, game_world_position)
        self.game_state.items_on_ground.append(item)
        get_item_effect(item_type).apply_end_effect(self.game_state)
        self.game_state.player_state.item_slots[item_slot] = None

    def drop_consumable_on_ground(self, consumable_slot: int, game_world_position: Tuple[int, int]):
        consumable_type = self.game_state.player_state.consumable_slots[consumable_slot]
        consumable = create_consumable_on_ground(consumable_type, game_world_position)
        self.game_state.consumables_on_ground.append(consumable)
        self.game_state.player_state.consumable_slots[consumable_slot] = None

    def _is_enemy_close_to_camera(self, enemy):
        camera_rect_with_margin = get_rect_with_increased_size_in_all_directions(
            self.game_state.camera_world_area.rect(), 100)
        return rects_intersect(enemy.world_entity.rect(), camera_rect_with_margin)

    # Returns True if player died
    def run_one_frame(self, time_passed: Millis):
        for e in self.game_state.non_player_characters:
            # NonPlayerCharacter AI shouldn't run if enemy is too far out of sight
            if self._is_enemy_close_to_camera(e):
                e.npc_mind.control_npc(self.game_state, e, self.game_state.player_entity,
                                       self.game_state.player_state.is_invisible, time_passed)

        self.view_state.notify_player_entity_center_position(self.game_state.player_entity.get_center_position())

        self.player_controls.notify_time_passed(time_passed)

        self.view_state.notify_time_passed(time_passed)

        for projectile in self.game_state.projectile_entities:
            projectile.projectile_controller.notify_time_passed(self.game_state, projectile, time_passed)

        for visual_effect in self.game_state.visual_effects:
            visual_effect.notify_time_passed(time_passed)

        npcs_that_died = self.game_state.remove_dead_npcs()
        enemies_that_died = [e for e in npcs_that_died if e.is_enemy]
        if enemies_that_died:
            play_sound(SoundId.EVENT_ENEMY_DIED)
            exp_gained = sum([NON_PLAYER_CHARACTERS[e.npc_type].exp_reward for e in enemies_that_died])
            self.game_state.visual_effects.append(create_visual_exp_text(self.game_state.player_entity, exp_gained))
            did_player_level_up = self.game_state.player_state.gain_exp(exp_gained)
            if did_player_level_up:
                play_sound(SoundId.EVENT_PLAYER_LEVELED_UP)
                self.view_state.set_message("You reached level " + str(self.game_state.player_state.level))
                self.game_state.player_state.update_stats_for_new_level()
                if self.game_state.player_state.level in self.game_state.player_state.new_level_abilities:
                    new_ability = self.game_state.player_state.new_level_abilities[self.game_state.player_state.level]
                    player_learn_new_ability(self.game_state.player_state, new_ability)
            for enemy_that_died in enemies_that_died:
                for loot_entry in enemy_that_died.enemy_loot_picker.loot_entries:
                    if random.random() < loot_entry.chance_to_drop:
                        loot_pos_offset = (random.randint(-20, 20), random.randint(-20, 20))
                        loot_position = sum_of_vectors(enemy_that_died.world_entity.get_position(), loot_pos_offset)

                        if loot_entry.money_amount:
                            money_pile_on_ground = create_money_pile_on_ground(1, loot_position)
                            self.game_state.money_piles_on_ground.append(money_pile_on_ground)
                        elif loot_entry.item_type:
                            item_on_ground = create_item_on_ground(loot_entry.item_type, loot_position)
                            self.game_state.items_on_ground.append(item_on_ground)
                        elif loot_entry.consumable_type:
                            consumable_on_ground = create_consumable_on_ground(loot_entry.consumable_type,
                                                                               loot_position)
                            self.game_state.consumables_on_ground.append(consumable_on_ground)

        self.game_state.remove_expired_projectiles()
        self.game_state.remove_expired_visual_effects()

        player_buffs_update = handle_buffs(self.game_state.player_state.active_buffs, time_passed)
        for buff_effect in player_buffs_update.buffs_that_started:
            buff_effect.apply_start_effect(self.game_state, self.game_state.player_entity, None)
        for buff_effect in player_buffs_update.buffs_that_were_active:
            buff_effect.apply_middle_effect(self.game_state, self.game_state.player_entity, None, time_passed)
        for buff_effect in player_buffs_update.buffs_that_ended:
            buff_effect.apply_end_effect(self.game_state, self.game_state.player_entity, None)

        for enemy in self.game_state.non_player_characters:
            enemy.regenerate_health(time_passed)
            buffs_update = handle_buffs(enemy.active_buffs, time_passed)
            for buff_effect in buffs_update.buffs_that_started:
                buff_effect.apply_start_effect(self.game_state, enemy.world_entity, enemy)
            for buff_effect in buffs_update.buffs_that_were_active:
                buff_effect.apply_middle_effect(self.game_state, enemy.world_entity, enemy, time_passed)
            for buff_effect in buffs_update.buffs_that_ended:
                buff_effect.apply_end_effect(self.game_state, enemy.world_entity, enemy)

        for item_type in self.game_state.player_state.item_slots.values():
            if item_type:
                get_item_effect(item_type).apply_middle_effect(self.game_state, time_passed)

        self.game_state.player_state.regenerate_health_and_mana(time_passed)
        self.game_state.player_state.recharge_ability_cooldowns(time_passed)

        self.game_state.player_entity.update_movement_animation(time_passed)
        for e in self.game_state.non_player_characters:
            e.world_entity.update_movement_animation(time_passed)
        for projectile in self.game_state.projectile_entities:
            projectile.world_entity.update_movement_animation(time_passed)

        for e in self.game_state.non_player_characters:
            # Enemies shouldn't move towards player when they are out of sight
            if self._is_enemy_close_to_camera(e) and not e.is_stunned():
                self.game_state.update_world_entity_position_within_game_world(e.world_entity, time_passed)
        if not self.game_state.player_state.is_stunned:
            self.game_state.update_world_entity_position_within_game_world(self.game_state.player_entity, time_passed)
        for projectile in self.game_state.projectile_entities:
            new_pos = projectile.world_entity.get_new_position_according_to_dir_and_speed(time_passed)
            projectile.world_entity.set_position(new_pos)

        for visual_effect in self.game_state.visual_effects:
            visual_effect.update_position_if_attached_to_entity()
            if visual_effect.attached_to_entity \
                    and not visual_effect.attached_to_entity in [e.world_entity for e in
                                                                 self.game_state.non_player_characters] \
                    and visual_effect.attached_to_entity != self.game_state.player_entity:
                visual_effect.has_expired = True

        # ------------------------------------
        #          HANDLE COLLISIONS
        # ------------------------------------

        entities_to_remove = []
        for consumable in self.game_state.consumables_on_ground:
            if boxes_intersect(self.game_state.player_entity, consumable.world_entity):
                empty_consumable_slots = self.game_state.player_state.find_first_empty_consumable_slot()
                consumable_name = CONSUMABLES[consumable.consumable_type].name
                if empty_consumable_slots:
                    self.game_state.player_state.consumable_slots[empty_consumable_slots] = consumable.consumable_type
                    self.view_state.set_message("You picked up " + consumable_name)
                    play_sound(SoundId.EVENT_PICKED_UP)
                    entities_to_remove.append(consumable)
                else:
                    self.view_state.set_message("No space for " + consumable_name)
        for item in self.game_state.items_on_ground:
            if boxes_intersect(self.game_state.player_entity, item.world_entity):
                empty_item_slot = self.game_state.player_state.find_first_empty_item_slot()
                item_name = ITEMS[item.item_type].name
                if empty_item_slot:
                    self.game_state.player_state.item_slots[empty_item_slot] = item.item_type
                    item_effect = get_item_effect(item.item_type)
                    item_effect.apply_start_effect(self.game_state)
                    self.view_state.set_message("You picked up " + item_name)
                    play_sound(SoundId.EVENT_PICKED_UP)
                    entities_to_remove.append(item)
                else:
                    self.view_state.set_message("No space for " + item_name)
        for money_pile in self.game_state.money_piles_on_ground:
            if boxes_intersect(self.game_state.player_entity, money_pile.world_entity):
                play_sound(SoundId.EVENT_PICKED_UP)
                entities_to_remove.append(money_pile)
                self.game_state.player_state.money += money_pile.amount

        for enemy in [e for e in self.game_state.non_player_characters if e.is_enemy]:
            for projectile in self.game_state.get_projectiles_intersecting_with(enemy.world_entity):
                should_remove_projectile = projectile.projectile_controller.apply_enemy_collision(
                    enemy, self.game_state)
                if should_remove_projectile:
                    entities_to_remove.append(projectile)

        for non_enemy_npc in self.game_state.non_enemy_npcs:
            for projectile in self.game_state.get_projectiles_intersecting_with(non_enemy_npc.world_entity):
                should_remove_projectile = projectile.projectile_controller.apply_non_enemy_npc_collision(
                    non_enemy_npc, self.game_state)
                if should_remove_projectile:
                    entities_to_remove.append(projectile)

        for projectile in self.game_state.get_projectiles_intersecting_with(self.game_state.player_entity):
            should_remove_projectile = projectile.projectile_controller.apply_player_collision(self.game_state)
            if should_remove_projectile:
                entities_to_remove.append(projectile)

        for projectile in self.game_state.projectile_entities:
            if self.game_state.does_entity_intersect_with_wall(projectile.world_entity):
                should_remove_projectile = projectile.projectile_controller.apply_wall_collision(self.game_state)
                if should_remove_projectile:
                    entities_to_remove.append(projectile)

        self.game_state.remove_entities(entities_to_remove)

        # ------------------------------------
        #       UPDATE CAMERA POSITION
        # ------------------------------------

        self.game_state.center_camera_on_player()

        if self.game_state.player_state.health <= 0:
            return True  # Game over
