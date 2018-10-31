from abilities import apply_ability_effect
from buffs import BUFF_EFFECTS
from common import boxes_intersect
from player_controls import TryUseAbilityResult, PlayerControls
from potions import try_consume_potion, PotionWasConsumed, PotionFailedToBeConsumed


class GameEngine:

    def __init__(self, game_state, view_state):
        self.game_state = game_state
        self.player_controls = PlayerControls()
        self.view_state = view_state

    def try_use_ability(self, action):
        self.view_state.notify_ability_was_clicked(action.ability_type)
        result = self.player_controls.try_use_ability(self.game_state.player_state, action.ability_type)
        if result == TryUseAbilityResult.SUCCESS:
            apply_ability_effect(self.game_state, action.ability_type)
        elif result == TryUseAbilityResult.NOT_ENOUGH_MANA:
            self.view_state.set_message("Not enough mana!")

    def try_use_potion(self, action):
        self.view_state.notify_potion_was_clicked(action.slot_number)
        potion_type_in_this_slot = self.game_state.player_state.potion_slots[action.slot_number]
        if potion_type_in_this_slot:
            result = try_consume_potion(potion_type_in_this_slot, self.game_state)
            if isinstance(result, PotionWasConsumed):
                self.game_state.player_state.potion_slots[action.slot_number] = None
            elif isinstance(result, PotionFailedToBeConsumed):
                self.view_state.set_message(result.reason)
        else:
            self.view_state.set_message("No potion to use!")

    def move_in_direction(self, action):
        self.game_state.player_entity.set_moving_in_dir(action.direction)

    def stop_moving(self):
        self.game_state.player_entity.set_not_moving()

    def run_one_frame(self, time_passed):
        for e in self.game_state.enemies:
            # Enemy AI shouldn't run if enemy is out of sight
            if boxes_intersect(e.world_entity, self.game_state.camera_world_area):
                e.enemy_mind.control_enemy(self.game_state, e, self.game_state.player_entity,
                                           self.game_state.player_state.is_invisible, time_passed)

        self.view_state.notify_player_entity_center_position(self.game_state.player_entity.get_center_position())

        self.player_controls.notify_time_passed(time_passed)

        self.view_state.notify_time_passed(time_passed)

        for projectile in self.game_state.projectile_entities:
            projectile.projectile_controller.notify_time_passed(projectile, time_passed)

        for visual_line in self.game_state.visual_lines:
            visual_line.notify_time_passed(time_passed)

        self.game_state.remove_dead_enemies()
        self.game_state.remove_expired_projectiles()
        self.game_state.remove_expired_visual_lines()

        buffs_update = self.game_state.player_state.update_and_expire_buffs(time_passed)
        for buff_type in buffs_update.buffs_that_started:
            BUFF_EFFECTS[buff_type].apply_start_effect(self.game_state)
        for buff_type in buffs_update.active_buffs:
            BUFF_EFFECTS[buff_type].apply_middle_effect(self.game_state, time_passed)
        for buff_type in buffs_update.buffs_that_ended:
            BUFF_EFFECTS[buff_type].apply_end_effect(self.game_state)

        self.game_state.player_state.regenerate_mana(time_passed)

        for e in self.game_state.enemies:
            # Enemies shouldn't move towards player when they are out of sight
            if boxes_intersect(e.world_entity, self.game_state.camera_world_area):
                self.game_state.update_world_entity_position_within_game_world(e.world_entity, time_passed)
        self.game_state.update_world_entity_position_within_game_world(self.game_state.player_entity, time_passed)
        for projectile in self.game_state.projectile_entities:
            projectile.world_entity.update_position_according_to_dir_and_speed(time_passed)

        # ------------------------------------
        #          HANDLE COLLISIONS
        # ------------------------------------

        entities_to_remove = []
        for potion in self.game_state.potions_on_ground:
            if boxes_intersect(self.game_state.player_entity, potion.world_entity):
                did_pick_up = self.game_state.player_state.try_pick_up_potion(potion.potion_type)
                if did_pick_up:
                    entities_to_remove.append(potion)
        for enemy in self.game_state.enemies:
            for projectile in self.game_state.get_projectiles_intersecting_with(enemy.world_entity):
                should_remove_projectile = projectile.projectile_controller.apply_enemy_collision(enemy)
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
