import random

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, ConsumableType, \
    PortraitIconSprite, UiIconSprite, SoundId
from pythongame.core.game_data import register_npc_data, NpcData, SpriteSheet, register_entity_sprite_map, \
    register_portrait_icon_sprite_path
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind, AbstractNpcAction, \
    register_npc_dialog_data, DialogData, DialogOptionData
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.sound_player import play_sound


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._update_path_interval = 500
        self._time_since_updated_path = self._update_path_interval

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):
        self._time_since_updated_path += time_passed
        if self._time_since_updated_path > self._update_path_interval:
            self._time_since_updated_path = 0
            if random.random() < 0.8:
                npc.world_entity.set_not_moving()
            else:
                direction = random.choice(get_all_directions())
                npc.world_entity.set_moving_in_dir(direction)


class SellConsumable(AbstractNpcAction):
    def __init__(self, cost: int, consumable_type: ConsumableType, name: str):
        self.cost = cost
        self.consumable_type = consumable_type
        self.name = name

    def act(self, game_state: GameState):
        player_state = game_state.player_state
        can_afford = player_state.money >= self.cost
        has_space = player_state.consumable_inventory.has_space_for_more()
        if not can_afford:
            play_sound(SoundId.WARNING)
            return "Not enough gold!"
        if not has_space:
            play_sound(SoundId.WARNING)
            return "Not enough space!"
        player_state.money -= self.cost
        player_state.consumable_inventory.add_consumable(self.consumable_type)
        play_sound(SoundId.EVENT_PURCHASED_SOMETHING)
        return "Bought " + self.name


def register_ninja_npc():
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.NEUTRAL_NPC_NINJA
    portrait_icon_sprite = PortraitIconSprite.NINJA
    npc_type = NpcType.NEUTRAL_NINJA
    movement_speed = 0.03
    register_npc_data(npc_type, NpcData.neutral(sprite, size, movement_speed))
    register_npc_behavior(npc_type, NpcMind)
    # TODO Use proper icon for 'cancel' option
    dialog_options = [
        DialogOptionData("Lesser mana potion [5 gold]", "buy",
                         SellConsumable(5, ConsumableType.MANA_LESSER, "lesser mana potion"),
                         UiIconSprite.POTION_MANA_LESSER),
        DialogOptionData("Lesser health potion [5 gold]", "buy",
                         SellConsumable(5, ConsumableType.HEALTH_LESSER, "lesser health potion"),
                         UiIconSprite.POTION_HEALTH_LESSER),
        DialogOptionData("Speed potion [10 gold]", "buy",
                         SellConsumable(10, ConsumableType.SPEED, "speed potion"),
                         UiIconSprite.POTION_SPEED),
        DialogOptionData("\"Good bye\"", "cancel", None, UiIconSprite.MAP_EDITOR_TRASHCAN)]
    dialog_text_body = "Ah.. You're new here, aren't you? Interested in my stock of potions?"
    dialog_data = DialogData(portrait_icon_sprite, dialog_text_body, dialog_options)
    register_npc_dialog_data(npc_type, dialog_data)
    sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_3.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    x = 6
    indices_by_dir = {
        Direction.DOWN: [(x, 0), (x + 1, 0), (x + 2, 0)],
        Direction.LEFT: [(x, 1), (x + 1, 1), (x + 2, 1)],
        Direction.RIGHT: [(x, 2), (x + 1, 2), (x + 2, 2)],
        Direction.UP: [(x, 3), (x + 1, 3), (x + 2, 3)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-8, -16))
    register_portrait_icon_sprite_path(portrait_icon_sprite, 'resources/graphics/ninja_portrait.png')
