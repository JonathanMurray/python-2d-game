import random
from typing import Optional

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, PortraitIconSprite, \
    UiIconSprite, ItemType, PeriodicTimer, HeroId, SoundId
from pythongame.core.entity_creation import create_item_on_ground
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map, \
    register_portrait_icon_sprite_path, ITEMS
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.item_effects import get_item_effect, try_add_item_to_inventory
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind, AbstractNpcAction, \
    register_npc_dialog_data, DialogData, DialogOptionData
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.sound_player import play_sound
from pythongame.core.view.image_loading import SpriteSheet

ITEM_TYPE_FROG = ItemType.FROG


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self.timer = PeriodicTimer(Millis(500))

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            if random.random() < 0.8:
                npc.world_entity.set_not_moving()
            else:
                direction = random.choice(get_all_directions())
                npc.world_entity.set_moving_in_dir(direction)


def get_reward_for_hero(hero_id: HeroId):
    if hero_id == HeroId.MAGE:
        return ItemType.STAFF_OF_FIRE
    elif hero_id == HeroId.ROGUE:
        return ItemType.THIEFS_MASK
    elif hero_id == HeroId.WARRIOR:
        # TODO use a more interesting reward
        return ItemType.ROYAL_SWORD
    else:
        return ItemType.LEATHER_ARMOR


class AcceptFrog(AbstractNpcAction):

    def act(self, game_state: GameState) -> Optional[str]:
        player_has_it = game_state.player_state.item_inventory.has_item_in_inventory(ITEM_TYPE_FROG)
        if player_has_it:
            game_state.player_state.item_inventory.lose_item_from_inventory(ITEM_TYPE_FROG)

            reward_item_type = get_reward_for_hero(game_state.player_state.hero_id)
            reward_effect = get_item_effect(reward_item_type)
            reward_data = ITEMS[reward_item_type]
            reward_equipment_category = reward_data.item_equipment_category
            did_add_item = try_add_item_to_inventory(game_state, reward_effect, reward_equipment_category)
            if not did_add_item:
                game_state.items_on_ground.append(
                    create_item_on_ground(reward_item_type, game_state.player_entity.get_position()))
            play_sound(SoundId.EVENT_COMPLETED_QUEST)
            return "Reward gained: " + reward_data.name
        else:
            return "You don't have that!"


def register_young_sorceress_npc():
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.NEUTRAL_NPC_YOUNG_SORCERESS
    npc_type = NpcType.NEUTRAL_YOUNG_SORCERESS
    ui_icon_sprite = PortraitIconSprite.YOUNG_SORCERESS
    movement_speed = 0.03
    register_npc_data(npc_type, NpcData.neutral(sprite, size, movement_speed))
    register_npc_behavior(npc_type, NpcMind)
    introduction = "Hey you! Have you seen my pet frog? I bet it was that old green mean goblin king that took it!"

    prompt = "> "
    frog_data = ITEMS[ItemType.FROG]
    dialog_options = [
        DialogOptionData(prompt + frog_data.name, "give", AcceptFrog(), UiIconSprite.ITEM_FROG, frog_data.name,
                         "If you help me get it back, I'll give you something in return!"),
        DialogOptionData("\"Good bye\"", "cancel", None)]
    dialog_data = DialogData(ui_icon_sprite, introduction, dialog_options)
    register_npc_dialog_data(npc_type, dialog_data)
    sprite_sheet = SpriteSheet("resources/graphics/manga_spritesheet.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    x = 6
    indices_by_dir = {
        Direction.DOWN: [(x, 4), (x + 1, 4), (x + 2, 4)],
        Direction.LEFT: [(x, 5), (x + 1, 5), (x + 2, 5)],
        Direction.RIGHT: [(x, 6), (x + 1, 6), (x + 2, 6)],
        Direction.UP: [(x, 7), (x + 1, 7), (x + 2, 7)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-8, -16))
    register_portrait_icon_sprite_path(ui_icon_sprite, 'resources/graphics/portrait_young_sorceress_npc.png')
