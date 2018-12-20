from pythongame.game_data.ability_channel_attack import register_channel_attack_ability
from pythongame.game_data.ability_entangling_roots import register_entangling_roots_ability
from pythongame.game_data.ability_fireball import register_fireball_ability
from pythongame.game_data.ability_frost_nova import register_frost_nova_ability
from pythongame.game_data.ability_heal import register_heal_ability
from pythongame.game_data.ability_teleport import register_teleport_ability
from pythongame.game_data.ability_whirlwind import register_whirlwind_ability
from pythongame.game_data.enemy_dark_reaper import register_dark_reaper_enemy
from pythongame.game_data.enemy_goblin_warlock import register_goblin_warlock_enemy
from pythongame.game_data.enemy_mummy import register_mummy_enemy
from pythongame.game_data.enemy_necromancer import register_necromancer_enemy
from pythongame.game_data.enemy_rat_1 import register_rat_1_enemy
from pythongame.game_data.enemy_rat_2 import register_rat_2_enemy
from pythongame.game_data.item_amulet_of_mana import register_amulet_of_mana_item
from pythongame.game_data.item_rod_of_lightning import register_rod_of_lightning_item
from pythongame.game_data.item_sword_of_leeching import register_sword_of_leeching_item
from pythongame.game_data.item_winged_boots import register_winged_boots_item
from pythongame.game_data.player_data import register_player_data
from pythongame.game_data.potion_health import register_health_potion
from pythongame.game_data.potion_invis import register_invis_potion
from pythongame.game_data.potion_mana import register_mana_potion
from pythongame.game_data.potion_speed import register_speed_potion


def register_all_game_data():
    register_fireball_ability()
    register_frost_nova_ability()
    register_heal_ability()
    register_channel_attack_ability()
    register_teleport_ability()
    register_health_potion()
    register_mana_potion()
    register_invis_potion()
    register_speed_potion()
    register_necromancer_enemy()
    register_player_data()
    register_rat_1_enemy()
    register_rat_2_enemy()
    register_dark_reaper_enemy()
    register_whirlwind_ability()
    register_goblin_warlock_enemy()
    register_mummy_enemy()
    register_winged_boots_item()
    register_amulet_of_mana_item()
    register_sword_of_leeching_item()
    register_rod_of_lightning_item()
    register_entangling_roots_ability()
