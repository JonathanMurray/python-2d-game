from pythongame.core.abilities import apply_ability_effect
from pythongame.core.buffs import get_buff_effect
from pythongame.core.common import *
from pythongame.core.game_state import GameState
from pythongame.core.player_controls import TryUseAbilityResult, PlayerControls
from pythongame.core.potions import try_consume_potion, PotionWasConsumed, PotionFailedToBeConsumed
from pythongame.core.view_state import ViewState


class GameEngine:

    def __init__(self, game_state: GameState, view_state: ViewState):
        self.game_state = game_state
        self.player_controls = PlayerControls()
        self.view_state = view_state

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

        copied_buffs_list = list(self.game_state.player_state.active_buffs)
        buffs_that_started = []
        buffs_that_were_active = [b.buff_type for b in copied_buffs_list]
        buffs_that_ended = []
        for buff in copied_buffs_list:
            buff.time_until_expiration -= time_passed
            if not buff.has_applied_start_effect:
                buffs_that_started.append(buff.buff_type)
                buff.has_applied_start_effect = True
            elif buff.time_until_expiration <= 0:
                self.game_state.player_state.active_buffs.remove(buff)
                buffs_that_ended.append(buff.buff_type)

        for buff_type in buffs_that_started:
            get_buff_effect(buff_type).apply_start_effect(self.game_state)
        for buff_type in buffs_that_were_active:
            get_buff_effect(buff_type).apply_middle_effect(self.game_state, time_passed)
        for buff_type in buffs_that_ended:
            get_buff_effect(buff_type).apply_end_effect(self.game_state)

        self.game_state.player_state.regenerate_mana(time_passed)
        self.game_state.player_state.recharge_ability_cooldowns(time_passed)

        self.game_state.player_entity.update_movement_animation(time_passed)
        for e in self.game_state.enemies:
            e.world_entity.update_movement_animation(time_passed)
        for projectile in self.game_state.projectile_entities:
            projectile.world_entity.update_movement_animation(time_passed)

        for e in self.game_state.enemies:
            # Enemies shouldn't move towards player when they are out of sight
            if self._is_enemy_close_to_camera(e):
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
                    entities_to_remove.append(potion)
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