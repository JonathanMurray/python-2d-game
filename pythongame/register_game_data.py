from pythongame.game_data.abilities.ability_bloodlust import register_bloodlust_ability
from pythongame.game_data.abilities.ability_channel_attack import register_channel_attack_ability
from pythongame.game_data.abilities.ability_charge import register_charge_ability
from pythongame.game_data.abilities.ability_entangling_roots import register_entangling_roots_ability
from pythongame.game_data.abilities.ability_fireball import register_fireball_ability
from pythongame.game_data.abilities.ability_frost_nova import register_frost_nova_ability
from pythongame.game_data.abilities.ability_heal import register_heal_ability
from pythongame.game_data.abilities.ability_infuse_dagger import register_infuse_dagger_ability
from pythongame.game_data.abilities.ability_shiv import register_shiv_ability
from pythongame.game_data.abilities.ability_sneak import register_sneak_ability
from pythongame.game_data.abilities.ability_stomp import register_stomp_ability
from pythongame.game_data.abilities.ability_sword_slash import register_sword_slash_ability
from pythongame.game_data.abilities.ability_teleport import register_teleport_ability
from pythongame.game_data.abilities.ability_whirlwind import register_whirlwind_ability
from pythongame.game_data.buff_recovering_after_ability import register_recovering_after_ability_buff
from pythongame.game_data.coin import register_coin
from pythongame.game_data.consumables.potion_health import register_health_potion
from pythongame.game_data.consumables.potion_invis import register_invis_potion
from pythongame.game_data.consumables.potion_lesser_health import register_lesser_health_potion
from pythongame.game_data.consumables.potion_lesser_mana import register_lesser_mana_potion
from pythongame.game_data.consumables.potion_mana import register_mana_potion
from pythongame.game_data.consumables.potion_speed import register_speed_potion
from pythongame.game_data.consumables.scroll_ability_summon import register_summon_scroll
from pythongame.game_data.decorations import register_decorations
from pythongame.game_data.enemies.enemy_chest import register_chest_enemy
from pythongame.game_data.enemies.enemy_dark_reaper import register_dark_reaper_enemy
from pythongame.game_data.enemies.enemy_goblin_spearman import register_goblin_spearman_enemy
from pythongame.game_data.enemies.enemy_goblin_warlock import register_goblin_warlock_enemy
from pythongame.game_data.enemies.enemy_goblin_worker import register_goblin_worker_enemy
from pythongame.game_data.enemies.enemy_mummy import register_mummy_enemy
from pythongame.game_data.enemies.enemy_necromancer import register_necromancer_enemy
from pythongame.game_data.enemies.enemy_rat_1 import register_rat_1_enemy
from pythongame.game_data.enemies.enemy_rat_2 import register_rat_2_enemy
from pythongame.game_data.enemies.enemy_warrior import register_warrior_enemy
from pythongame.game_data.heroes.hero_mage import register_hero_mage
from pythongame.game_data.heroes.hero_rogue import register_hero_rogue
from pythongame.game_data.heroes.hero_warrior import register_hero_warrior
from pythongame.game_data.items.item_amulet_of_mana import register_amulet_of_mana_item
from pythongame.game_data.items.item_blessed_shield import register_blessed_shield_item
from pythongame.game_data.items.item_blood_amulet import register_blood_amulet
from pythongame.game_data.items.item_blue_robe import register_blue_robe_item
from pythongame.game_data.items.item_goats_ring import register_goats_ring
from pythongame.game_data.items.item_knights_armor import register_knights_armor
from pythongame.game_data.items.item_orb_of_the_magi import register_orb_of_the_magi_item
from pythongame.game_data.items.item_rod_of_lightning import register_rod_of_lightning_item
from pythongame.game_data.items.item_soldiers_helmet import register_soldiers_helmet_item
from pythongame.game_data.items.item_staff_of_fire import register_staff_of_fire_item
from pythongame.game_data.items.item_sword_of_leeching import register_sword_of_leeching_item
from pythongame.game_data.items.item_winged_boots import register_winged_boots_item
from pythongame.game_data.items.item_wizards_cowl import register_wizards_cowl
from pythongame.game_data.items.item_zuls_aegis import register_zuls_aegis
from pythongame.game_data.map_editor_icons import register_map_editor_icons
from pythongame.game_data.neutral_npcs.neutral_npc_dwarf import register_dwarf_npc
from pythongame.game_data.neutral_npcs.neutral_npc_ninja import register_ninja_npc
from pythongame.game_data.neutral_npcs.neutral_npc_nomad import register_nomad_npc
from pythongame.game_data.portals import register_portal
from pythongame.game_data.walls import register_walls


def register_all_game_data():
    register_fireball_ability()
    register_frost_nova_ability()
    register_heal_ability()
    register_channel_attack_ability()
    register_teleport_ability()
    register_sword_slash_ability()
    register_bloodlust_ability()
    register_charge_ability()
    register_whirlwind_ability()
    register_entangling_roots_ability()
    register_stomp_ability()
    register_shiv_ability()
    register_sneak_ability()
    register_infuse_dagger_ability()

    register_recovering_after_ability_buff()

    register_lesser_health_potion()
    register_health_potion()
    register_lesser_mana_potion()
    register_mana_potion()
    register_invis_potion()
    register_speed_potion()
    register_summon_scroll()

    register_chest_enemy()
    register_necromancer_enemy()
    register_rat_1_enemy()
    register_rat_2_enemy()
    register_dark_reaper_enemy()
    register_goblin_warlock_enemy()
    register_mummy_enemy()
    register_warrior_enemy()
    register_goblin_worker_enemy()
    register_goblin_spearman_enemy()

    register_hero_mage()
    register_hero_warrior()
    register_hero_rogue()

    register_dwarf_npc()
    register_nomad_npc()
    register_ninja_npc()

    register_winged_boots_item()
    register_amulet_of_mana_item()
    register_sword_of_leeching_item()
    register_rod_of_lightning_item()
    register_soldiers_helmet_item()
    register_blessed_shield_item()
    register_staff_of_fire_item()
    register_blue_robe_item()
    register_orb_of_the_magi_item()
    register_wizards_cowl()
    register_zuls_aegis()
    register_knights_armor()
    register_goats_ring()
    register_blood_amulet()

    register_decorations()
    register_map_editor_icons()
    register_walls()

    register_coin()

    register_portal()
