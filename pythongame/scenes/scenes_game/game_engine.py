from typing import Dict

from pythongame.core.abilities import ABILITIES, allocate_input_keys_for_abilities, KEYS_BY_ABILITY_TYPE
from pythongame.core.buff_effects import AbstractBuffEffect, get_buff_effect
from pythongame.core.common import *
from pythongame.core.common import EngineEvent
from pythongame.core.entity_creation import create_money_pile_on_ground, create_item_on_ground, \
    create_consumable_on_ground
from pythongame.core.game_data import CONSUMABLES, NON_PLAYER_CHARACTERS, NpcCategory, PORTALS
from pythongame.core.game_state import GameState, ItemOnGround, ConsumableOnGround, LootableOnGround, BuffWithDuration, \
    EnemyDiedEvent, NonPlayerCharacter, Portal, PlayerLeveledUp, PlayerLearnedNewAbility, WarpPoint, Chest, \
    PlayerUnlockedNewTalent, AgentBuffsUpdate, Shrine
from pythongame.core.item_data import ITEM_ENTITY_SIZE, get_item_data_by_type
from pythongame.core.item_data import randomized_item_id, get_item_data
from pythongame.core.item_effects import create_item_effect
from pythongame.core.item_inventory import ItemWasDeactivated, ItemWasActivated, ItemActivationEvent
from pythongame.core.loot import LootEntry, MoneyLootEntry, ItemLootEntry, ConsumableLootEntry, AffixedItemLootEntry
from pythongame.core.math import boxes_intersect, rects_intersect, sum_of_vectors, \
    get_rect_with_increased_size_in_all_directions, translate_in_direction
from pythongame.core.sound_player import play_sound
from pythongame.core.visual_effects import create_visual_exp_text, create_teleport_effects, VisualRect, VisualCircle
from pythongame.game_data.loot_tables import get_loot_table
from pythongame.game_data.portals import PORTAL_DELAY
from pythongame.game_data.shrines import apply_shrine_buff_to_player
from pythongame.scenes.scenes_game.game_ui_view import InfoMessage
from pythongame.scenes.scenes_game.player_controls import PlayerControls


class GameEngine:

    def __init__(self, game_state: GameState, info_message: InfoMessage):
        self.game_state = game_state
        self.info_message = info_message
        self.talent_was_unlocked = Observable()
        self.ability_was_clicked = Observable()
        self.abilities_were_updated = Observable()
        self.consumable_was_clicked = Observable()

    def try_use_ability(self, ability_type: AbilityType):
        PlayerControls.try_use_ability(ability_type, self.game_state, self.info_message)
        self.ability_was_clicked.notify(ability_type)

    def try_use_consumable(self, slot_number: int):
        PlayerControls.try_use_consumable(slot_number, self.game_state, self.info_message)
        self.consumable_was_clicked.notify(slot_number)

    def move_in_direction(self, direction: Direction):
        if not self.game_state.player_state.stun_status.is_stunned():
            self.game_state.game_world.player_entity.set_moving_in_dir(direction)

    def stop_moving(self):
        # Don't stop moving if stunned (could be charging)
        if not self.game_state.player_state.stun_status.is_stunned():
            self.game_state.game_world.player_entity.set_not_moving()

    def drag_item_between_inventory_slots(self, slot_1: int, slot_2: int) -> bool:
        item_equip_events = self.game_state.player_state.item_inventory.switch_item_slots(slot_1, slot_2)
        for event in item_equip_events:
            self._handle_item_equip_event(event)
        did_switch_succeed = len(item_equip_events) > 0
        return did_switch_succeed

    def _handle_item_equip_event(self, event: ItemActivationEvent):
        player_state = self.game_state.player_state
        item_id = event.item_id
        item_data = get_item_data(item_id)
        if isinstance(event, ItemWasActivated):
            create_item_effect(item_id).apply_start_effect(self.game_state)
            if item_data.active_ability_type:
                player_state.set_active_item_ability(item_data.active_ability_type)
                self.on_abilities_updated()
        elif isinstance(event, ItemWasDeactivated):
            create_item_effect(item_id).apply_end_effect(self.game_state)
            if item_data.active_ability_type:
                player_state.set_active_item_ability(None)
                self.on_abilities_updated()

    def drag_consumable_between_inventory_slots(self, from_slot: int, to_slot: int):
        self.game_state.player_state.consumable_inventory.drag_consumable_between_inventory_slots(from_slot, to_slot)

    def drop_inventory_item_on_ground(self, item_slot: int, game_world_position: Tuple[int, int]):
        item_equip_event = self.game_state.player_state.item_inventory.remove_item_from_slot(item_slot)
        item_id = item_equip_event.item_id
        self._handle_item_equip_event(item_equip_event)
        item = create_item_on_ground(item_id, game_world_position)
        self.game_state.game_world.items_on_ground.append(item)

    def drop_consumable_on_ground(self, consumable_slot: int, game_world_position: Tuple[int, int]):
        consumable_type = self.game_state.player_state.consumable_inventory.remove_consumable_from_slot(consumable_slot)
        consumable = create_consumable_on_ground(consumable_type, game_world_position)
        self.game_state.game_world.consumables_on_ground.append(consumable)

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
        item_name = item.item_id.name
        did_add_item = self.try_add_item_to_inventory(item.item_id)
        if did_add_item:
            play_sound(SoundId.EVENT_PICKED_UP)
            self.game_state.game_world.items_on_ground.remove(item)
            self.info_message.set_message("You picked up " + item_name)
        else:
            self.info_message.set_message("No space for " + item_name)

    def try_add_item_to_inventory(self, item_id: ItemId) -> bool:
        item_effect = create_item_effect(item_id)
        item_type = item_id.item_type
        item_equipment_category = get_item_data_by_type(item_type).item_equipment_category
        event = self.game_state.player_state.item_inventory.try_add_item(item_id, item_effect, item_equipment_category)
        if event is not None:
            self._handle_item_equip_event(event)
        return event is not None

    def fill_item_inventory(self, items: List[ItemId]):
        for slot_number, item_id in enumerate(items):
            if item_id:
                item_effect = create_item_effect(item_id)
                item_data = get_item_data(item_id)
                item_equipment_category = item_data.item_equipment_category
                event = self.game_state.player_state.item_inventory.put_item_in_inventory_slot(
                    item_id, item_effect, item_equipment_category, slot_number)
                self._handle_item_equip_event(event)

    def clear_item_inventory(self) -> List[ItemId]:
        inventory = self.game_state.player_state.item_inventory

        # get a copy of the inventory before it was cleared, to return to caller
        slot_item_ids = []
        for slot in inventory.slots:
            item_id = slot.get_item_id() if not slot.is_empty() else None
            slot_item_ids.append(item_id)

        events = inventory.clear()
        for event in events:
            self._handle_item_equip_event(event)

        return slot_item_ids

    def _try_pick_up_consumable_from_ground(self, consumable: ConsumableOnGround):
        # TODO move some logic into ConsumableInventory class
        has_space = self.game_state.player_state.consumable_inventory.has_space_for_more()
        consumable_type = consumable.consumable_type
        consumable_name = CONSUMABLES[consumable_type].name
        if has_space:
            self.game_state.player_state.consumable_inventory.add_consumable(consumable_type)
            self.info_message.set_message("You picked up " + consumable_name)
            play_sound(SoundId.EVENT_PICKED_UP)
            self.game_state.game_world.consumables_on_ground.remove(consumable)
        else:
            self.info_message.set_message("No space for " + consumable_name)

    def interact_with_portal(self, portal: Portal):
        if portal.is_enabled:
            destination_portal_id = portal.leads_to
            sprite = portal.world_entity.sprite
            delay = PORTALS[portal.portal_id].teleport_delay
            destination_portal = self.game_state.game_world.get_portal_with_id(destination_portal_id)
            self.activate_portal(destination_portal, sprite)
            destination = translate_in_direction(destination_portal.world_entity.get_position(), Direction.DOWN, 50)
            teleport_buff_effect: AbstractBuffEffect = get_buff_effect(BuffType.TELEPORTING_WITH_PORTAL, destination)
            self.game_state.player_state.gain_buff_effect(teleport_buff_effect, delay)
        else:
            self.info_message.set_message("Hmm... Looks suspicious!")

    def handle_being_close_to_portal(self, portal: Portal):
        # When finding a new portal out on the map, it's enough to walk close to it, to activate its sibling
        if portal.is_enabled:
            destination_portal = self.game_state.game_world.get_portal_with_id(portal.leads_to)
            if not destination_portal.is_enabled:
                play_sound(SoundId.EVENT_PORTAL_ACTIVATED)
                self.info_message.set_message("Portal was activated")
                self.activate_portal(destination_portal, portal.world_entity.sprite)
                self.game_state.game_world.visual_effects += create_teleport_effects(
                    portal.world_entity.get_center_position())

    def activate_portal(self, portal: Portal, sprite: Sprite):
        portal.activate(sprite)
        self.game_state.player_state.enabled_portals[portal.portal_id] = sprite

    def interact_with_shrine(self, shrine: Shrine):
        if not shrine.has_been_used:
            shrine.has_been_used = True
            message = apply_shrine_buff_to_player(self.game_state.player_state)
            self.info_message.set_message(message)

    def use_warp_point(self, warp_point: WarpPoint):
        destination_warp_point = [w for w in self.game_state.game_world.warp_points if w != warp_point][0]
        # It's safe to teleport to warp point's position as hero and warp point entities are the exact same size
        teleport_buff_effect: AbstractBuffEffect = get_buff_effect(
            BuffType.TELEPORTING_WITH_WARP_POINT, destination_warp_point.world_entity.get_position())
        self.game_state.player_state.gain_buff_effect(teleport_buff_effect, PORTAL_DELAY)

    def open_chest(self, chest: Chest):
        increased_money_chance = self.game_state.player_state.increased_loot_money_chance
        increased_rare_or_unique_chance = self.game_state.player_state.increased_loot_rare_or_unique_chance
        loot_table = get_loot_table(chest.loot_table)
        loot = loot_table.generate_loot(increased_money_chance, increased_rare_or_unique_chance,
                                        self.game_state.is_dungeon)
        chest_position = chest.world_entity.get_position()
        self._put_loot_on_ground(chest_position, loot)
        chest.has_been_opened = True
        visual_effects = [
            VisualRect((200, 0, 200), chest.world_entity.get_center_position(), 50, 100, Millis(100), 2),
            VisualRect((200, 0, 200), chest.world_entity.get_center_position(), 50, 100, Millis(180), 3)
        ]
        self.game_state.game_world.visual_effects += visual_effects

    def gain_levels(self, num_levels: int):
        gain_exp_events = self.game_state.player_state.gain_exp_worth_n_levels(num_levels)
        self._handle_gain_exp_events(gain_exp_events)

    # Returns whether or not player died
    def run_one_frame(self, time_passed: Millis) -> List[EngineEvent]:

        events = []

        for npc in self.game_state.game_world.non_player_characters:
            # NonPlayerCharacter AI shouldn't run if enemy is too far out of sight
            if self._is_npc_close_to_camera(npc):
                npc.npc_mind.control_npc(self.game_state, npc, self.game_state.game_world.player_entity,
                                         self.game_state.player_state.is_invisible, time_passed)

        for projectile in self.game_state.game_world.projectile_entities:
            projectile.projectile_controller.notify_time_passed(self.game_state, projectile, time_passed)

        for visual_effect in self.game_state.game_world.visual_effects:
            visual_effect.notify_time_passed(time_passed)

        self.game_state.handle_camera_shake(time_passed)

        npcs_that_died = self.game_state.game_world.remove_dead_npcs()
        enemies_that_died = [e for e in npcs_that_died if e.is_enemy]
        if enemies_that_died:
            exp_gained = sum([NON_PLAYER_CHARACTERS[e.npc_type].exp_reward for e in enemies_that_died])
            self.game_state.game_world.visual_effects.append(
                create_visual_exp_text(self.game_state.game_world.player_entity, exp_gained))
            gain_exp_events = self.game_state.player_state.gain_exp(exp_gained)
            self._handle_gain_exp_events(gain_exp_events)

            for enemy_that_died in enemies_that_died:
                if enemy_that_died.death_sound_id:
                    play_sound(enemy_that_died.death_sound_id)
                else:
                    play_sound(SoundId.EVENT_ENEMY_DIED)
                increased_money_chance = self.game_state.player_state.increased_loot_money_chance
                increased_rare_or_unique_chance = self.game_state.player_state.increased_loot_rare_or_unique_chance
                loot_table = get_loot_table(enemy_that_died.enemy_loot_table)
                loot: List[LootEntry] = loot_table.generate_loot(
                    increased_money_chance, increased_rare_or_unique_chance, self.game_state.is_dungeon)
                enemy_death_position = enemy_that_died.world_entity.get_position()
                self._put_loot_on_ground(enemy_death_position, loot)
                self.game_state.player_state.notify_about_event(EnemyDiedEvent(), self.game_state)
            events.append(EngineEvent.ENEMY_DIED)

        self.game_state.game_world.remove_expired_projectiles()
        self.game_state.game_world.remove_expired_visual_effects()
        self.game_state.game_world.remove_opened_chests()

        player_buffs_update = self.game_state.player_state.handle_buffs(time_passed)
        for buff in player_buffs_update.buffs_that_started:
            buff.buff_effect.apply_start_effect(self.game_state, self.game_state.game_world.player_entity, None)
        for buff in player_buffs_update.buffs_that_were_active:
            buff_should_end = buff.buff_effect.apply_middle_effect(
                self.game_state, self.game_state.game_world.player_entity, None, time_passed)
            if buff_should_end:
                buff.force_cancel()

        for buff in player_buffs_update.buffs_that_ended:
            buff.buff_effect.apply_end_effect(self.game_state, self.game_state.game_world.player_entity, None)

        for enemy in self.game_state.game_world.non_player_characters:
            enemy.health_resource.regenerate(time_passed)
            buffs_update = _handle_buffs(enemy.active_buffs, time_passed)
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

        self.game_state.game_world.player_entity.update_movement_animation(time_passed)
        for npc in self.game_state.game_world.non_player_characters:
            npc.world_entity.update_movement_animation(time_passed)
        for projectile in self.game_state.game_world.projectile_entities:
            projectile.world_entity.update_movement_animation(time_passed)
        for warp_point in self.game_state.game_world.warp_points:
            warp_point.world_entity.update_animation(time_passed)

        for npc in self.game_state.game_world.non_player_characters:
            # Enemies shouldn't move towards player when they are out of sight
            if self._is_npc_close_to_camera(npc):
                self.game_state.game_world.update_npc_position_within_game_world(npc, time_passed)
        # player can still move when stunned (could be charging)
        self.game_state.game_world.update_world_entity_position_within_game_world(
            self.game_state.game_world.player_entity, time_passed)
        for projectile in self.game_state.game_world.projectile_entities:
            new_pos = projectile.world_entity.get_new_position_according_to_dir_and_speed(time_passed)
            projectile.world_entity.set_position(new_pos)

        for visual_effect in self.game_state.game_world.visual_effects:
            visual_effect.update_position_if_attached_to_entity()
            if visual_effect.attached_to_entity:
                npcs = [e.world_entity for e in self.game_state.game_world.non_player_characters]
                projectiles = [p.world_entity for p in self.game_state.game_world.projectile_entities]
                if visual_effect.attached_to_entity not in npcs + projectiles + [
                    self.game_state.game_world.player_entity]:
                    visual_effect.has_expired = True

        # ------------------------------------
        #          HANDLE COLLISIONS
        # ------------------------------------

        for money_pile in self.game_state.game_world.money_piles_on_ground:
            if boxes_intersect(self.game_state.game_world.player_entity.rect(), money_pile.world_entity.rect()):
                play_sound(SoundId.EVENT_PICKED_UP_MONEY)
                money_pile.has_been_picked_up_and_should_be_removed = True
                self.game_state.player_state.modify_money(money_pile.amount)

        for enemy in [e for e in self.game_state.game_world.non_player_characters if e.is_enemy]:
            for projectile in self.game_state.game_world.get_projectiles_intersecting_with(enemy.world_entity):
                if not projectile.has_collided_and_should_be_removed:
                    projectile.projectile_controller.apply_enemy_collision(enemy, self.game_state, projectile)

        for player_summon in [npc for npc in self.game_state.game_world.non_player_characters
                              if npc.npc_category == NpcCategory.PLAYER_SUMMON]:
            for projectile in self.game_state.game_world.get_projectiles_intersecting_with(player_summon.world_entity):
                if not projectile.has_collided_and_should_be_removed:
                    projectile.projectile_controller.apply_player_summon_collision(player_summon, self.game_state,
                                                                                   projectile)

        for projectile in self.game_state.game_world.get_projectiles_intersecting_with(
                self.game_state.game_world.player_entity):
            if not projectile.has_collided_and_should_be_removed:
                projectile.projectile_controller.apply_player_collision(self.game_state, projectile)

        for projectile in self.game_state.game_world.projectile_entities:
            if not projectile.has_collided_and_should_be_removed:
                if self.game_state.game_world.walls_state.does_entity_intersect_with_wall(projectile.world_entity):
                    projectile.projectile_controller.apply_wall_collision(self.game_state, projectile)

        self.game_state.game_world.remove_money_piles_that_have_been_picked_up()
        self.game_state.game_world.remove_projectiles_that_have_been_destroyed()

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
            self.game_state.game_world.visual_effects.append(
                VisualCircle((150, 150, 250), self.game_state.game_world.player_entity.get_center_position(), 9, 35,
                             Millis(150), 2))
            self.info_message.set_message("You reached level " + str(self.game_state.player_state.level))
        if new_abilities:
            self.on_abilities_updated()
        if len(new_abilities) == 1:
            self.info_message.enqueue_message("New ability: " + new_abilities[0])
        elif len(new_abilities) > 1:
            self.info_message.enqueue_message("Gained several new abilities")
        if did_unlock_new_talent:
            self.talent_was_unlocked.notify(None)
            self.info_message.enqueue_message("You can pick a talent!")

    def on_abilities_updated(self):
        abilities = self.game_state.player_state.abilities
        allocate_input_keys_for_abilities(abilities)
        ability_types_by_key_string: Dict[str, AbilityType] = {
            KEYS_BY_ABILITY_TYPE[ability_type].key_string: ability_type for ability_type in abilities}
        self.abilities_were_updated.notify(ability_types_by_key_string)

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

            if isinstance(loot_entry, MoneyLootEntry):
                money_pile_on_ground = create_money_pile_on_ground(loot_entry.amount, loot_position)
                self.game_state.game_world.money_piles_on_ground.append(money_pile_on_ground)
            elif isinstance(loot_entry, ItemLootEntry):
                item_id = randomized_item_id(loot_entry.item_type)
                item_on_ground = create_item_on_ground(item_id, loot_position)
                self.game_state.game_world.items_on_ground.append(item_on_ground)
            elif isinstance(loot_entry, AffixedItemLootEntry):
                item_id = loot_entry.item_id
                item_on_ground = create_item_on_ground(item_id, loot_position)
                self.game_state.game_world.items_on_ground.append(item_on_ground)
                loot_center_pos = (loot_position[0] + ITEM_ENTITY_SIZE[0] // 2,
                                   loot_position[1] + ITEM_ENTITY_SIZE[1] // 2)
                self.game_state.game_world.visual_effects.append(
                    VisualCircle((170, 200, 170), loot_center_pos, 30, 40, Millis(500), 2))
                self.game_state.game_world.visual_effects.append(
                    VisualCircle((70, 100, 70), loot_center_pos, 25, 35, Millis(500), 2))
            elif isinstance(loot_entry, ConsumableLootEntry):
                consumable_on_ground = create_consumable_on_ground(loot_entry.consumable_type, loot_position)
                self.game_state.game_world.consumables_on_ground.append(consumable_on_ground)


def _handle_buffs(active_buffs: List[BuffWithDuration], time_passed: Millis) -> AgentBuffsUpdate:
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
