from pythongame.game_data.abilities.ability_arcane_fire import register_arcane_fire_ability
from pythongame.game_data.abilities.ability_bloodlust import register_bloodlust_ability
from pythongame.game_data.abilities.ability_charge import register_charge_ability
from pythongame.game_data.abilities.ability_dash import register_dash_ability
from pythongame.game_data.abilities.ability_entangling_roots import register_entangling_roots_ability
from pythongame.game_data.abilities.ability_fireball import register_fireball_ability
from pythongame.game_data.abilities.ability_frost_nova import register_frost_nova_ability
from pythongame.game_data.abilities.ability_heal import register_heal_ability
from pythongame.game_data.abilities.ability_infuse_dagger import register_infuse_dagger_ability
from pythongame.game_data.abilities.ability_shiv import register_shiv_ability
from pythongame.game_data.abilities.ability_stealth import register_stealth_ability
from pythongame.game_data.abilities.ability_stomp import register_stomp_ability
from pythongame.game_data.abilities.ability_sword_slash import register_sword_slash_ability
from pythongame.game_data.abilities.ability_teleport import register_teleport_ability
from pythongame.game_data.abilities.ability_whirlwind import register_whirlwind_ability
from pythongame.game_data.buff_hero_spawning import register_spawn_buff
from pythongame.game_data.buff_recovering_after_ability import register_recovering_after_ability_buff
from pythongame.game_data.chests import register_chest_entity
from pythongame.game_data.coin import register_coin
from pythongame.game_data.consumables.consumable_warpstone import register_warpstone_consumable
from pythongame.game_data.consumables.elixir_power import register_elixir_of_power
from pythongame.game_data.consumables.potion_brew import register_brew_potion
from pythongame.game_data.consumables.potion_health import register_health_potion
from pythongame.game_data.consumables.potion_invis import register_invis_potion
from pythongame.game_data.consumables.potion_lesser_health import register_lesser_health_potion
from pythongame.game_data.consumables.potion_lesser_mana import register_lesser_mana_potion
from pythongame.game_data.consumables.potion_mana import register_mana_potion
from pythongame.game_data.consumables.potion_speed import register_speed_potion
from pythongame.game_data.consumables.scroll_ability_summon import register_summon_scroll
from pythongame.game_data.decorations import register_decorations
from pythongame.game_data.enemies.enemy_dark_reaper import register_dark_reaper_enemy
from pythongame.game_data.enemies.enemy_goblin_spearman import register_goblin_spearman_enemy
from pythongame.game_data.enemies.enemy_goblin_spearman_elite import register_goblin_spearman_elite_enemy
from pythongame.game_data.enemies.enemy_goblin_warlock import register_goblin_warlock_enemy
from pythongame.game_data.enemies.enemy_goblin_warrior import register_goblin_warrior_enemy
from pythongame.game_data.enemies.enemy_goblin_worker import register_goblin_worker_enemy
from pythongame.game_data.enemies.enemy_ice_witch import register_ice_witch_enemy
from pythongame.game_data.enemies.enemy_mummy import register_mummy_enemy
from pythongame.game_data.enemies.enemy_necromancer import register_necromancer_enemy
from pythongame.game_data.enemies.enemy_rat_1 import register_rat_1_enemy
from pythongame.game_data.enemies.enemy_rat_2 import register_rat_2_enemy
from pythongame.game_data.enemies.enemy_veteran import register_veteran_enemy
from pythongame.game_data.enemies.enemy_warrior import register_warrior_enemy
from pythongame.game_data.enemies.enemy_warrior_king import register_warrior_king_enemy
from pythongame.game_data.enemies.enemy_zombie import register_zombie_enemy
from pythongame.game_data.heroes.generic_talents import register_generic_talents
from pythongame.game_data.heroes.hero_god import register_hero_god
from pythongame.game_data.heroes.hero_mage import register_hero_mage
from pythongame.game_data.heroes.hero_rogue import register_hero_rogue
from pythongame.game_data.heroes.hero_warrior import register_hero_warrior
from pythongame.game_data.items.item_amulet_of_mana import register_amulet_of_mana_item
from pythongame.game_data.items.item_blessed_shield import register_blessed_shield_item
from pythongame.game_data.items.item_blood_amulet import register_blood_amulet
from pythongame.game_data.items.item_blue_robe import register_blue_robe_item
from pythongame.game_data.items.item_druids_ring import register_druids_ring_item
from pythongame.game_data.items.item_elite_armor import register_elite_armor
from pythongame.game_data.items.item_elite_helmet import register_elite_helmet_item
from pythongame.game_data.items.item_elven_armor import register_elven_armor
from pythongame.game_data.items.item_freezing_gauntlet import register_freezing_gauntlet_item
from pythongame.game_data.items.item_frog import register_frog_item
from pythongame.game_data.items.item_gladiator_armor import register_gladiator_armor
from pythongame.game_data.items.item_goats_ring import register_goats_ring
from pythongame.game_data.items.item_gold_nugget import register_gold_nugget
from pythongame.game_data.items.item_hatchet import register_hatchet_item
from pythongame.game_data.items.item_healing_wand import register_healing_wand_item
from pythongame.game_data.items.item_key import register_key_item
from pythongame.game_data.items.item_knights_armor import register_knights_armor
from pythongame.game_data.items.item_leather_armor import register_leather_armor_item
from pythongame.game_data.items.item_leather_cowl import register_leather_cowl_item
from pythongame.game_data.items.item_lich_armor import register_lich_armor_item
from pythongame.game_data.items.item_messengers_hat import register_messengers_hat_item
from pythongame.game_data.items.item_molten_axe import register_molten_axe_item
from pythongame.game_data.items.item_noble_defender import register_noble_defender
from pythongame.game_data.items.item_orb_of_life import register_orb_of_life_item
from pythongame.game_data.items.item_orb_of_the_magi import register_orb_of_the_magi_item
from pythongame.game_data.items.item_orb_of_wisdom import register_orb_of_wisdom_item
from pythongame.game_data.items.item_ring_of_power import register_ring_of_power_item
from pythongame.game_data.items.item_rod_of_lightning import register_rod_of_lightning_item
from pythongame.game_data.items.item_royal_dagger import register_royal_dagger_item
from pythongame.game_data.items.item_royal_sword import register_royal_sword_item
from pythongame.game_data.items.item_saphire import register_saphire
from pythongame.game_data.items.item_skull_shield import register_skull_shield_item
from pythongame.game_data.items.item_skull_staff import register_skull_staff_item
from pythongame.game_data.items.item_soldiers_helmet import register_soldiers_helmet_item
from pythongame.game_data.items.item_staff_of_fire import register_staff_of_fire_item
from pythongame.game_data.items.item_stone_amulet import register_stone_amulet_item
from pythongame.game_data.items.item_torn_document import register_torn_document_item
from pythongame.game_data.items.item_wand import register_wand_item
from pythongame.game_data.items.item_warlocks_cowl import register_warlocks_cowl_item
from pythongame.game_data.items.item_warlords_armor import register_warlords_armor_item
from pythongame.game_data.items.item_winged_helmet import register_winged_helmet_item
from pythongame.game_data.items.item_wizards_cowl import register_wizards_cowl
from pythongame.game_data.items.item_wooden_shield import register_wooden_shield
from pythongame.game_data.items.item_wooden_sword import register_wooden_sword_item
from pythongame.game_data.items.item_zuls_aegis import register_zuls_aegis
from pythongame.game_data.map_editor_icons import register_map_editor_icons
from pythongame.game_data.neutral_npcs.neutral_npc_dwarf import register_dwarf_npc
from pythongame.game_data.neutral_npcs.neutral_npc_ninja import register_ninja_npc
from pythongame.game_data.neutral_npcs.neutral_npc_nomad import register_nomad_npc
from pythongame.game_data.neutral_npcs.neutral_npc_sorcerer import register_sorcerer_npc
from pythongame.game_data.neutral_npcs.neutral_npc_warpstone_merchant import register_warpstone_merchant_npc
from pythongame.game_data.neutral_npcs.neutral_npc_young_sorceress import register_young_sorceress_npc
from pythongame.game_data.portals import register_portal
from pythongame.game_data.ui_icons import register_ui_icons
from pythongame.game_data.walls import register_walls
from pythongame.game_data.warp_points import register_warp_point


def register_all_game_data():
    register_fireball_ability()
    register_frost_nova_ability()
    register_heal_ability()
    register_arcane_fire_ability()
    register_teleport_ability()
    register_sword_slash_ability()
    register_bloodlust_ability()
    register_charge_ability()
    register_whirlwind_ability()
    register_entangling_roots_ability()
    register_stomp_ability()
    register_shiv_ability()
    register_stealth_ability()
    register_infuse_dagger_ability()
    register_dash_ability()

    register_recovering_after_ability_buff()
    register_spawn_buff()

    register_lesser_health_potion()
    register_health_potion()
    register_lesser_mana_potion()
    register_mana_potion()
    register_invis_potion()
    register_speed_potion()
    register_summon_scroll()
    register_brew_potion()
    register_warpstone_consumable()
    register_elixir_of_power()

    register_necromancer_enemy()
    register_rat_1_enemy()
    register_rat_2_enemy()
    register_dark_reaper_enemy()
    register_goblin_warlock_enemy()
    register_zombie_enemy()
    register_mummy_enemy()
    register_warrior_enemy()
    register_veteran_enemy()
    register_ice_witch_enemy()
    register_warrior_king_enemy()
    register_goblin_worker_enemy()
    register_goblin_spearman_enemy()
    register_goblin_spearman_elite_enemy()
    register_goblin_warrior_enemy()

    register_hero_mage()
    register_hero_warrior()
    register_hero_rogue()
    register_hero_god()

    register_messengers_hat_item()
    register_amulet_of_mana_item()
    register_skull_staff_item()
    register_rod_of_lightning_item()
    register_soldiers_helmet_item()
    register_blessed_shield_item()
    register_staff_of_fire_item()
    register_blue_robe_item()
    register_orb_of_the_magi_item()
    register_orb_of_wisdom_item()
    register_orb_of_life_item()
    register_wizards_cowl()
    register_zuls_aegis()
    register_knights_armor()
    register_goats_ring()
    register_blood_amulet()
    register_wooden_shield()
    register_elven_armor()
    register_gold_nugget()
    register_saphire()
    register_leather_cowl_item()
    register_winged_helmet_item()
    register_elite_armor()
    register_ring_of_power_item()
    register_leather_armor_item()
    register_freezing_gauntlet_item()
    register_royal_dagger_item()
    register_royal_sword_item()
    register_molten_axe_item()
    register_wand_item()
    register_gladiator_armor()
    register_noble_defender()
    register_frog_item()
    register_hatchet_item()
    register_elite_helmet_item()
    register_stone_amulet_item()
    register_torn_document_item()
    register_key_item()
    register_wooden_sword_item()
    register_druids_ring_item()
    register_warlocks_cowl_item()
    register_lich_armor_item()
    register_warlords_armor_item()
    register_healing_wand_item()
    register_skull_shield_item()

    # Register items before NPCs as vendors may rely on item data

    register_dwarf_npc()
    register_nomad_npc()
    register_ninja_npc()
    register_sorcerer_npc()
    register_young_sorceress_npc()
    register_warpstone_merchant_npc()

    register_decorations()
    register_map_editor_icons()
    register_ui_icons()
    register_walls()

    register_coin()

    register_portal()

    register_warp_point()

    register_chest_entity()

    register_generic_talents()
