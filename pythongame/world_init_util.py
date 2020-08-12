from pythongame.core.common import Observable
from pythongame.core.footsteps import play_or_stop_footstep_sounds
from pythongame.core.game_state import PlayerState, GameState
from pythongame.scenes.scenes_game.game_engine import GameEngine
from pythongame.scenes.scenes_game.game_ui_view import GameUiView


def register_game_engine_observers(game_engine: GameEngine, ui_view: GameUiView):
    game_engine.talent_was_unlocked.register_observer(ui_view.on_talent_was_unlocked)
    game_engine.ability_was_clicked.register_observer(ui_view.on_ability_was_clicked)
    game_engine.consumable_was_clicked.register_observer(ui_view.on_consumable_was_clicked)
    game_engine.abilities_were_updated.register_observer(ui_view.on_abilities_updated)


def register_game_state_observers(game_state: GameState, ui_view: GameUiView, include_player_state: bool):
    game_state.game_world.player_movement_speed_was_updated.register_observer(ui_view.on_player_movement_speed_updated)
    game_state.game_world.notify_movement_speed_observers()  # Must notify the initial state
    game_state.game_world.player_entity.movement_changed = Observable()
    game_state.game_world.player_entity.movement_changed.register_observer(play_or_stop_footstep_sounds)
    game_state.game_world.player_entity.position_changed = Observable()
    game_state.game_world.player_entity.position_changed.register_observer(ui_view.on_player_position_updated)
    game_state.game_world.player_entity.position_changed.register_observer(
        lambda _: ui_view.on_walls_seen([w.get_position() for w in game_state.get_walls_in_sight_of_player()]))
    game_state.game_world.player_entity.notify_position_observers()  # Must notify the initial state

    if include_player_state:
        _register_player_state_observers(game_state.player_state, ui_view)


def _register_player_state_observers(player_state: PlayerState, ui_view: GameUiView):
    player_state.exp_was_updated.register_observer(ui_view.on_player_exp_updated)
    player_state.talents_were_updated.register_observer(ui_view.on_talents_updated)
    player_state.notify_talent_observers()  # Must notify the initial state
    player_state.stats_were_updated.register_observer(ui_view.on_player_stats_updated)
    player_state.notify_stats_observers()  # Must notify the initial state
    player_state.money_was_updated.register_observer(ui_view.on_money_updated)
    player_state.notify_money_observers()  # Must notify the initial state

    player_state.cooldowns_were_updated.register_observer(ui_view.on_cooldowns_updated)
    player_state.health_resource.value_was_updated.register_observer(ui_view.on_health_updated)
    player_state.mana_resource.value_was_updated.register_observer(ui_view.on_mana_updated)
    player_state.buffs_were_updated.register_observer(ui_view.on_buffs_updated)
    player_state.quests_were_updated.register_observer(ui_view.on_player_quests_updated)
    player_state.item_inventory.was_updated.register_observer(ui_view.on_inventory_updated)
    player_state.item_inventory.notify_observers()  # Must notify the initial state
    player_state.consumable_inventory.was_updated.register_observer(ui_view.on_consumables_updated)
    player_state.consumable_inventory.notify_observers()  # Must notify the initial state
