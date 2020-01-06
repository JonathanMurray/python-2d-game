from typing import Tuple

from pythongame.core.buff_effects import AbstractBuffEffect, get_buff_effect
from pythongame.core.common import *
from pythongame.core.entity_creation import create_money_pile_on_ground, create_item_on_ground, \
    create_consumable_on_ground
from pythongame.core.game_data import CONSUMABLES, ITEMS, NON_PLAYER_CHARACTERS, allocate_input_keys_for_abilities, \
    NpcCategory, PORTALS, ABILITIES
from pythongame.core.game_state import GameState, ItemOnGround, ConsumableOnGround, LootableOnGround, BuffWithDuration, \
    EnemyDiedEvent, NonPlayerCharacter, Portal, PlayerLeveledUp, PlayerLearnedNewAbility, WarpPoint, Chest, \
    PlayerUnlockedNewTalent, AgentBuffsUpdate
from pythongame.core.item_effects import get_item_effect, try_add_item_to_inventory
from pythongame.core.item_inventory import ItemWasDeactivated, ItemWasActivated
from pythongame.core.loot import LootEntry
from pythongame.core.math import boxes_intersect, rects_intersect, sum_of_vectors, \
    get_rect_with_increased_size_in_all_directions, translate_in_direction
from pythongame.core.sound_player import play_sound
from pythongame.core.visual_effects import create_visual_exp_text, create_teleport_effects, VisualRect, VisualCircle
from pythongame.game_data.portals import PORTAL_DELAY
from pythongame.scenes_game.game_ui_view import InfoMessage
from pythongame.scenes_game.player_controls import PlayerControls


class EngineEvent(Enum):
    PLAYER_DIED = 1
    ENEMY_DIED = 2


class GameEngine:

    def __init__(self, game_state: GameState, info_message: InfoMessage):
        self.game_state = game_state
        self.info_message = info_message
        self.talent_was_unlocked = Observable()
        self.ability_was_clicked = Observable()
        self.consumable_was_clicked = Observable()

    def try_use_ability(self, ability_type: AbilityType):
        PlayerControls.try_use_ability(ability_type, self.game_state, self.info_message)
        self.ability_was_clicked.notify(ability_type)

    def try_use_consumable(self, slot_number: int):
        PlayerControls.try_use_consumable(slot_number, self.game_state, self.info_message)
        self.consumable_was_clicked.notify(slot_number)

    def move_in_direction(self, direction: Direction):
        if not self.game_state.player_state.stun_status.is_stunned():
            self.game_state.player_entity.set_moving_in_dir(direction)

    def stop_moving(self):
        # Don't stop moving if stunned (could be charging)
        if not self.game_state.player_state.stun_status.is_stunned():
            self.game_state.player_entity.set_not_moving()

    def drag_item_between_inventory_slots(self, slot_1: int, slot_2: int) -> bool:
        item_equip_events = self.game_state.player_state.item_inventory.switch_item_slots(slot_1, slot_2)
        for event in item_equip_events:
            self._handle_item_equip_event(event)
        did_switch_succeed = len(item_equip_events) > 0
        return did_switch_succeed

    def _handle_item_equip_event(self, event):
        if isinstance(event, ItemWasDeactivated):
            get_item_effect(event.item_type).apply_end_effect(self.game_state)
        elif isinstance(event, ItemWasActivated):
            get_item_effect(event.item_type).apply_start_effect(self.game_state)

    def drag_consumable_between_inventory_slots(self, from_slot: int, to_slot: int):
        self.game_state.player_state.consumable_inventory.drag_consumable_between_inventory_slots(from_slot, to_slot)

    def drop_inventory_item_on_ground(self, item_slot: int, game_world_position: Tuple[int, int]):
        item_equip_event = self.game_state.player_state.item_inventory.remove_item_from_slot(item_slot)
        item_type = item_equip_event.item_type
        self._handle_item_equip_event(item_equip_event)
        item = create_item_on_ground(item_type, game_world_position)
        self.game_state.items_on_ground.append(item)

    def drop_consumable_on_ground(self, consumable_slot: int, game_world_position: Tuple[int, int]):
        consumable_type = self.game_state.player_state.consumable_inventory.remove_consumable_from_slot(consumable_slot)
        consumable = create_consumable_on_ground(consumable_type, game_world_position)
        self.game_state.consumables_on_ground.append(consumable)

    def try_switch_item_at_slot(self, item_slot: int) -> bool:
        item_equip_events = self.game_state.player_state.item_inventory.try_switch_item_at_slot(item_slot)
        for event in item_equip_events:
            self._handle_item_equip_event(event)
        did_switch_succeed = len(item_equip_events) > 0
        return did_switch_succeed

    def try_pick_up_loot_from_ground(self, loot: LootableOnGround):
        if isinstance(loot, ConsumableOnGround):
            self._try_pick_up_consumable_from_ground(loot)
        elif isinstance(loot, ItemOnGround):
            self._try_pick_up_item_from_ground(loot)
        else:
            raise Exception("Unhandled type of loot: " + str(loot))

    def _try_pick_up_item_from_ground(self, item: ItemOnGround):
        item_effect = get_item_effect(item.item_type)
        item_data = ITEMS[item.item_type]
        item_equipment_category = item_data.item_equipment_category
        did_add_item = try_add_item_to_inventory(self.game_state, item_effect, item_equipment_category)
        if did_add_item:
            play_sound(SoundId.EVENT_PICKED_UP)
            self.game_state.items_on_ground.remove(item)
            self.info_message.set_message("You picked up " + item_data.name)
        else:
            self.info_message.set_message("No space for " + item_data.name)

    def set_item_inventory(self, items: List[ItemType]):
        for slot_number, item_type in enumerate(items):
            if item_type:
                item_effect = get_item_effect(item_type)
                item_data = ITEMS[item_type]
                item_equipment_category = item_data.item_equipment_category
                event = self.game_state.player_state.item_inventory.put_item_in_inventory_slot(
                    item_effect, item_equipment_category, slot_number)
                self._handle_item_equip_event(event)

    def _try_pick_up_consumable_from_ground(self, consumable: ConsumableOnGround):
        # TODO move some logic into ConsumableInventory class
        has_space = self.game_state.player_state.consumable_inventory.has_space_for_more()
        consumable_type = consumable.consumable_type
        consumable_name = CONSUMABLES[consumable_type].name
        if has_space:
            self.game_state.player_state.consumable_inventory.add_consumable(consumable_type)
            self.info_message.set_message("You picked up " + consumable_name)
            play_sound(SoundId.EVENT_PICKED_UP)
            self.game_state.consumables_on_ground.remove(consumable)
        else:
            self.info_message.set_message("No space for " + consumable_name)

    def interact_with_portal(self, portal: Portal):
        if portal.is_enabled:
            destination_portal = [p for p in self.game_state.portals if p.portal_id == portal.leads_to][0]
            destination_portal.activate(portal.world_entity.sprite)
            destination = translate_in_direction(destination_portal.world_entity.get_position(), Direction.DOWN, 50)
            teleport_buff_effect: AbstractBuffEffect = get_buff_effect(BuffType.TELEPORTING_WITH_PORTAL, destination)
            delay = PORTALS[portal.portal_id].teleport_delay
            self.game_state.player_state.gain_buff_effect(teleport_buff_effect, delay)
        else:
            self.info_message.set_message("Hmm... Looks suspicious!")

    def handle_being_close_to_portal(self, portal: Portal):
        # When finding a new portal out on the map, it's enough to walk close to it, to activate its sibling
        if portal.is_enabled:
            destination_portal = [p for p in self.game_state.portals if p.portal_id == portal.leads_to][0]
            if not destination_portal.is_enabled:
                play_sound(SoundId.EVENT_PORTAL_ACTIVATED)
                self.info_message.set_message("Portal was activated")
                destination_portal.activate(portal.world_entity.sprite)
                self.game_state.visual_effects += create_teleport_effects(portal.world_entity.get_center_position())

    def use_warp_point(self, warp_point: WarpPoint):
        destination_warp_point = [w for w in self.game_state.warp_points if w != warp_point][0]
        # It's safe to teleport to warp point's position as hero and warp point entities are the exact same size
        teleport_buff_effect: AbstractBuffEffect = get_buff_effect(
            BuffType.TELEPORTING_WITH_WARP_POINT, destination_warp_point.world_entity.get_position())
        self.game_state.player_state.gain_buff_effect(teleport_buff_effect, PORTAL_DELAY)

    def open_chest(self, chest: Chest):
        loot = chest.loot_table.generate_loot()
        chest_position = chest.world_entity.get_position()
        self._put_loot_on_ground(chest_position, loot)
        chest.has_been_opened = True
        visual_effects = [
            VisualRect((200, 0, 200), chest.world_entity.get_center_position(), 50, 100, Millis(100), 2),
            VisualRect((200, 0, 200), chest.world_entity.get_center_position(), 50, 100, Millis(180), 3)
        ]
        self.game_state.visual_effects += visual_effects

    def gain_levels(self, num_levels: int):
        gain_exp_events = self.game_state.player_state.gain_exp_worth_n_levels(num_levels)
        self._handle_gain_exp_events(gain_exp_events)

    # Returns whether or not player died
    def run_one_frame(self, time_passed: Millis) -> List[EngineEvent]:

        events = []

        for npc in self.game_state.non_player_characters:
            # NonPlayerCharacter AI shouldn't run if enemy is too far out of sight
            if self._is_npc_close_to_camera(npc) and not npc.stun_status.is_stunned():
                npc.npc_mind.control_npc(self.game_state, npc, self.game_state.player_entity,
                                         self.game_state.player_state.is_invisible, time_passed)

        for projectile in self.game_state.projectile_entities:
            projectile.projectile_controller.notify_time_passed(self.game_state, projectile, time_passed)

        for visual_effect in self.game_state.visual_effects:
            visual_effect.notify_time_passed(time_passed)

        self.game_state.handle_camera_shake(time_passed)

        npcs_that_died = self.game_state.remove_dead_npcs()
        enemies_that_died = [e for e in npcs_that_died if e.is_enemy]
        if enemies_that_died:
            exp_gained = sum([NON_PLAYER_CHARACTERS[e.npc_type].exp_reward for e in enemies_that_died])
            self.game_state.visual_effects.append(create_visual_exp_text(self.game_state.player_entity, exp_gained))
            gain_exp_events = self.game_state.player_state.gain_exp(exp_gained)
            self._handle_gain_exp_events(gain_exp_events)

            for enemy_that_died in enemies_that_died:
                if enemy_that_died.death_sound_id:
                    play_sound(enemy_that_died.death_sound_id)
                else:
                    play_sound(SoundId.EVENT_ENEMY_DIED)
                loot = enemy_that_died.enemy_loot_table.generate_loot()
                enemy_death_position = enemy_that_died.world_entity.get_position()
                self._put_loot_on_ground(enemy_death_position, loot)
                self.game_state.player_state.notify_about_event(EnemyDiedEvent(), self.game_state)
            events.append(EngineEvent.ENEMY_DIED)

        self.game_state.remove_expired_projectiles()
        self.game_state.remove_expired_visual_effects()
        self.game_state.remove_opened_chests()

        player_buffs_update = self.game_state.player_state.handle_buffs(time_passed)
        for buff in player_buffs_update.buffs_that_started:
            buff.buff_effect.apply_start_effect(self.game_state, self.game_state.player_entity, None)
        for buff in player_buffs_update.buffs_that_were_active:
            buff_should_end = buff.buff_effect.apply_middle_effect(
                self.game_state, self.game_state.player_entity, None, time_passed)
            if buff_should_end:
                buff.force_cancel()

        for buff in player_buffs_update.buffs_that_ended:
            buff.buff_effect.apply_end_effect(self.game_state, self.game_state.player_entity, None)

        for enemy in self.game_state.non_player_characters:
            enemy.health_resource.regenerate(time_passed)
            buffs_update = handle_buffs(enemy.active_buffs, time_passed)
            for buff in buffs_update.buffs_that_started:
                buff.buff_effect.apply_start_effect(self.game_state, enemy.world_entity, enemy)
            for buff in buffs_update.buffs_that_were_active:
                buff.buff_effect.apply_middle_effect(self.game_state, enemy.world_entity, enemy, time_passed)
            for buff in buffs_update.buffs_that_ended:
                buff.buff_effect.apply_end_effect(self.game_state, enemy.world_entity, enemy)

        for item_effect in self.game_state.player_state.item_inventory.get_all_active_item_effects():
            item_effect.apply_middle_effect(self.game_state, time_passed)

        self.game_state.player_state.health_resource.regenerate(time_passed)
        self.game_state.player_state.mana_resource.regenerate(time_passed)
        self.game_state.player_state.recharge_ability_cooldowns(time_passed)

        self.game_state.player_entity.update_movement_animation(time_passed)
        for npc in self.game_state.non_player_characters:
            npc.world_entity.update_movement_animation(time_passed)
        for projectile in self.game_state.projectile_entities:
            projectile.world_entity.update_movement_animation(time_passed)
        for warp_point in self.game_state.warp_points:
            warp_point.world_entity.update_animation(time_passed)

        for npc in self.game_state.non_player_characters:
            # Enemies shouldn't move towards player when they are out of sight
            if self._is_npc_close_to_camera(npc) and not npc.stun_status.is_stunned():
                self.game_state.update_npc_position_within_game_world(npc, time_passed)
        # player can still move when stunned (could be charging)
        self.game_state.update_world_entity_position_within_game_world(self.game_state.player_entity, time_passed)
        for projectile in self.game_state.projectile_entities:
            new_pos = projectile.world_entity.get_new_position_according_to_dir_and_speed(time_passed)
            projectile.world_entity.set_position(new_pos)

        for visual_effect in self.game_state.visual_effects:
            visual_effect.update_position_if_attached_to_entity()
            if visual_effect.attached_to_entity:
                npcs = [e.world_entity for e in self.game_state.non_player_characters]
                projectiles = [p.world_entity for p in self.game_state.projectile_entities]
                if not visual_effect.attached_to_entity in npcs + projectiles + [self.game_state.player_entity]:
                    visual_effect.has_expired = True

        # ------------------------------------
        #          HANDLE COLLISIONS
        # ------------------------------------

        for money_pile in self.game_state.money_piles_on_ground:
            if boxes_intersect(self.game_state.player_entity.rect(), money_pile.world_entity.rect()):
                play_sound(SoundId.EVENT_PICKED_UP_MONEY)
                money_pile.has_been_picked_up_and_should_be_removed = True
                self.game_state.player_state.modify_money(money_pile.amount)

        for enemy in [e for e in self.game_state.non_player_characters if e.is_enemy]:
            for projectile in self.game_state.get_projectiles_intersecting_with(enemy.world_entity):
                if not projectile.has_collided_and_should_be_removed:
                    projectile.projectile_controller.apply_enemy_collision(enemy, self.game_state, projectile)

        for player_summon in [npc for npc in self.game_state.non_player_characters
                              if npc.npc_category == NpcCategory.PLAYER_SUMMON]:
            for projectile in self.game_state.get_projectiles_intersecting_with(player_summon.world_entity):
                if not projectile.has_collided_and_should_be_removed:
                    projectile.projectile_controller.apply_player_summon_collision(player_summon, self.game_state,
                                                                                   projectile)

        for projectile in self.game_state.get_projectiles_intersecting_with(self.game_state.player_entity):
            if not projectile.has_collided_and_should_be_removed:
                projectile.projectile_controller.apply_player_collision(self.game_state, projectile)

        for projectile in self.game_state.projectile_entities:
            if not projectile.has_collided_and_should_be_removed:
                if self.game_state.walls_state.does_entity_intersect_with_wall(projectile.world_entity):
                    projectile.projectile_controller.apply_wall_collision(self.game_state, projectile)

        self.game_state.remove_money_piles_that_have_been_picked_up()
        self.game_state.remove_projectiles_that_have_been_destroyed()

        # ------------------------------------
        #       UPDATE CAMERA POSITION
        # ------------------------------------

        self.game_state.center_camera_on_player()

        if self.game_state.player_state.health_resource.is_at_or_below_zero():
            events.append(EngineEvent.PLAYER_DIED)

        return events

    def _handle_gain_exp_events(self, gain_exp_events):
        did_level_up = False
        new_abilities: List[str] = []
        did_unlock_new_talent = False
        for event in gain_exp_events:
            if isinstance(event, PlayerLeveledUp):
                did_level_up = True
            if isinstance(event, PlayerLearnedNewAbility):
                new_abilities.append(ABILITIES[event.ability_type].name)
            if isinstance(event, PlayerUnlockedNewTalent):
                did_unlock_new_talent = True

        if did_level_up:
            play_sound(SoundId.EVENT_PLAYER_LEVELED_UP)
            self.game_state.visual_effects.append(
                VisualCircle((150, 150, 250), self.game_state.player_entity.get_center_position(), 9, 35,
                             Millis(150), 2))
            self.info_message.set_message("You reached level " + str(self.game_state.player_state.level))
        if new_abilities:
            allocate_input_keys_for_abilities(self.game_state.player_state.abilities)
        if len(new_abilities) == 1:
            self.info_message.enqueue_message("New ability: " + new_abilities[0])
        elif len(new_abilities) > 1:
            self.info_message.enqueue_message("Gained several new abilities")
        if did_unlock_new_talent:
            self.talent_was_unlocked.notify(None)
            self.info_message.enqueue_message("You can pick a talent!")

    def _is_npc_close_to_camera(self, npc: NonPlayerCharacter):
        camera_rect_with_margin = get_rect_with_increased_size_in_all_directions(
            self.game_state.camera_world_area, 100)
        return rects_intersect(npc.world_entity.rect(), camera_rect_with_margin)

    def _put_loot_on_ground(self, enemy_death_position: Tuple[int, int], loot: List[LootEntry]):
        for loot_entry in loot:
            if len(loot) > 1:
                position_offset = (random.randint(-20, 20), random.randint(-20, 20))
            else:
                position_offset = (0, 0)
            loot_position = sum_of_vectors(enemy_death_position, position_offset)

            if loot_entry.money_amount:
                money_pile_on_ground = create_money_pile_on_ground(loot_entry.money_amount, loot_position)
                self.game_state.money_piles_on_ground.append(money_pile_on_ground)
            elif loot_entry.item_type:
                item_on_ground = create_item_on_ground(loot_entry.item_type, loot_position)
                self.game_state.items_on_ground.append(item_on_ground)
            elif loot_entry.consumable_type:
                consumable_on_ground = create_consumable_on_ground(loot_entry.consumable_type, loot_position)
                self.game_state.consumables_on_ground.append(consumable_on_ground)


def handle_buffs(active_buffs: List[BuffWithDuration], time_passed: Millis) -> AgentBuffsUpdate:
    # NOTE: duplication between NPC's and player's buff handling
    copied_buffs_list = list(active_buffs)
    buffs_that_started = []
    buffs_that_ended = []
    buffs_that_were_active = []
    for buff in copied_buffs_list:
        buff.notify_time_passed(time_passed)
        if not buff.has_been_force_cancelled:
            buffs_that_were_active.append(buff)
        if not buff.has_applied_start_effect:
            buffs_that_started.append(buff)
            buff.has_applied_start_effect = True
        elif buff.has_expired():
            active_buffs.remove(buff)
            buffs_that_ended.append(buff)
    return AgentBuffsUpdate(buffs_that_started, buffs_that_were_active, buffs_that_ended)
