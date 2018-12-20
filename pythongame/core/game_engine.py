from pythongame.core.ability_effects import apply_ability_effect
from pythongame.core.common import *
from pythongame.core.game_data import POTIONS, ITEMS
from pythongame.core.game_state import GameState, handle_buffs
from pythongame.core.item_effects import get_item_effect
from pythongame.core.player_controls import TryUseAbilityResult, PlayerControls
from pythongame.core.potion_effects import try_consume_potion, PotionWasConsumed, PotionFailedToBeConsumed
from pythongame.core.view_state import ViewState


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
        if not self.game_state.player_state.is_stunned:
            self.view_state.notify_ability_was_clicked(ability_type)
            result = self.player_controls.try_use_ability(self.game_state.player_state, ability_type)
            if result == TryUseAbilityResult.SUCCESS:
                apply_ability_effect(self.game_state, ability_type)
            elif result == TryUseAbilityResult.NOT_ENOUGH_MANA:
                self.view_state.set_message("Not enough mana!")

    def try_use_potion(self, slot_number: int):
        if not self.game_state.player_state.is_stunned:
            self.view_state.notify_potion_was_clicked(slot_number)
            potion_type_in_this_slot = self.game_state.player_state.potion_slots[slot_number]
            if potion_type_in_this_slot:
                result = try_consume_potion(potion_type_in_this_slot, self.game_state)
                if isinstance(result, PotionWasConsumed):
                    self.game_state.player_state.potion_slots[slot_number] = None
                elif isinstance(result, PotionFailedToBeConsumed):
                    self.view_state.set_message(result.reason)
            else:
                self.view_state.set_message("No potion to use!")

    def move_in_direction(self, direction: Direction):
        if not self.game_state.player_state.is_stunned:
            self.game_state.player_entity.set_moving_in_dir(direction)

    def stop_moving(self):
        self.game_state.player_entity.set_not_moving()

    def _is_enemy_close_to_camera(self, enemy):
        camera_rect_with_margin = get_rect_with_increased_size_in_all_directions(
            self.game_state.camera_world_area.rect(), 250)
        return rects_intersect(enemy.world_entity.rect(), camera_rect_with_margin)

    # Returns True if player died
    def run_one_frame(self, time_passed: Millis):
        for e in self.game_state.enemies:
            # Enemy AI shouldn't run if enemy is too far out of sight
            if self._is_enemy_close_to_camera(e):
                e.enemy_mind.control_enemy(self.game_state, e, self.game_state.player_entity,
                                           self.game_state.player_state.is_invisible, time_passed)

        self.view_state.notify_player_entity_center_position(self.game_state.player_entity.get_center_position())

        self.player_controls.notify_time_passed(time_passed)

        self.view_state.notify_time_passed(time_passed)

        for projectile in self.game_state.projectile_entities:
            projectile.projectile_controller.notify_time_passed(self.game_state, projectile, time_passed)

        for visual_effect in self.game_state.visual_effects:
            visual_effect.notify_time_passed(time_passed)

        self.game_state.remove_dead_enemies()
        self.game_state.remove_expired_projectiles()
        self.game_state.remove_expired_visual_effects()

        player_buffs_update = handle_buffs(self.game_state.player_state.active_buffs, time_passed)
        for buff_effect in player_buffs_update.buffs_that_started:
            buff_effect.apply_start_effect(self.game_state, self.game_state.player_entity, None)
        for buff_effect in player_buffs_update.buffs_that_were_active:
            buff_effect.apply_middle_effect(self.game_state, self.game_state.player_entity, None, time_passed)
        for buff_effect in player_buffs_update.buffs_that_ended:
            buff_effect.apply_end_effect(self.game_state, self.game_state.player_entity, None)

        for enemy in self.game_state.enemies:
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

        self.game_state.player_state.regenerate_mana(time_passed)
        self.game_state.player_state.recharge_ability_cooldowns(time_passed)

        self.game_state.player_entity.update_movement_animation(time_passed)
        for e in self.game_state.enemies:
            e.world_entity.update_movement_animation(time_passed)
        for projectile in self.game_state.projectile_entities:
            projectile.world_entity.update_movement_animation(time_passed)

        for e in self.game_state.enemies:
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

        # ------------------------------------
        #          HANDLE COLLISIONS
        # ------------------------------------

        entities_to_remove = []
        for potion in self.game_state.potions_on_ground:
            if boxes_intersect(self.game_state.player_entity, potion.world_entity):
                empty_potion_slot = self.game_state.player_state.find_first_empty_potion_slot()
                if empty_potion_slot:
                    self.game_state.player_state.potion_slots[empty_potion_slot] = potion.potion_type
                    self.view_state.set_message("You picked up " + POTIONS[potion.potion_type].name)
                    entities_to_remove.append(potion)
        for item in self.game_state.items_on_ground:
            if boxes_intersect(self.game_state.player_entity, item.world_entity):
                empty_item_slot = self.game_state.player_state.find_first_empty_item_slot()
                if empty_item_slot:
                    self.game_state.player_state.item_slots[empty_item_slot] = item.item_type
                    item_effect = get_item_effect(item.item_type)
                    item_effect.apply_start_effect(self.game_state)
                    self.view_state.set_message("You picked up " + ITEMS[item.item_type].name)
                    entities_to_remove.append(item)

        for enemy in self.game_state.enemies:
            for projectile in self.game_state.get_projectiles_intersecting_with(enemy.world_entity):
                should_remove_projectile = projectile.projectile_controller.apply_enemy_collision(
                    enemy, self.game_state)
                if should_remove_projectile:
                    entities_to_remove.append(projectile)

        for projectile in self.game_state.get_projectiles_intersecting_with(self.game_state.player_entity):
            should_remove_projectile = projectile.projectile_controller.apply_player_collision(self.game_state)
            if should_remove_projectile:
                entities_to_remove.append(projectile)

        self.game_state.remove_entities(entities_to_remove)

        # ------------------------------------
        #       UPDATE CAMERA POSITION
        # ------------------------------------

        self.game_state.center_camera_on_player()

        if self.game_state.player_state.health <= 0:
            return True  # Game over
