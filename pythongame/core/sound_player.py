import random
from typing import Any, List, Dict

import pygame

from pythongame.core.common import SoundId

_sounds_by_id: Dict[SoundId, List[Any]] = {}

muted = False

LOOPING_SOUNDS = [SoundId.FOOTSTEPS]


def init_sound_player():
    global _sounds_by_id
    if _sounds_by_id:
        raise Exception("Don't initialize sound player several times!")
    _sounds_by_id = {
        SoundId.ABILITY_FIREBALL: load_sound_file('ability_fireball_1.ogg', 'ability_fireball_2.ogg',
                                                  'ability_fireball_3.ogg', volume=3),
        SoundId.ABILITY_FIREBALL_HIT: load_sound_file('ability_fireball_hit_1.ogg', 'ability_fireball_hit_2.ogg',
                                                      volume=2),
        SoundId.ABILITY_WHIRLWIND: load_sound_file('ability_whirlwind_1.ogg', 'ability_whirlwind_2.ogg',
                                                   'ability_whirlwind_3.ogg', volume=3),
        SoundId.ABILITY_TELEPORT: load_sound_file('SciFi06.ogg'),
        SoundId.ABILITY_ENTANGLING_ROOTS: load_sound_file('ability_entangling_roots.ogg', volume=4),
        SoundId.ABILITY_ENTANGLING_ROOTS_HIT: load_sound_file('SciFi03.ogg', volume=0.5),
        SoundId.ABILITY_CHARGE: load_sound_file('ability_charge_1.ogg', 'ability_charge_2.ogg', 'ability_charge_3.ogg',
                                                'ability_charge_4.ogg', volume=3),
        SoundId.ABILITY_CHARGE_HIT: load_sound_file('ability_fireball_hit_1.ogg', 'ability_fireball_hit_2.ogg',
                                                    volume=2),
        SoundId.ABILITY_SHIV: load_sound_file('dagger_1.ogg', 'dagger_2.ogg'),
        SoundId.ABILITY_SHIV_STEALTHED: load_sound_file('Slash04.ogg'),
        SoundId.ABILITY_STEALTH: load_sound_file('stealth.ogg', volume=3),
        SoundId.ABILITY_INFUSE_DAGGER: load_sound_file('poison.ogg', volume=5),
        SoundId.ABILITY_DASH: load_sound_file('dash.ogg', volume=5),
        SoundId.ABILITY_SLASH: load_sound_file('ability_slash_1.ogg', 'ability_slash_2.ogg', 'ability_slash_3.ogg',
                                               'ability_slash_4.ogg', 'ability_slash_5.ogg', volume=3),
        SoundId.ABILITY_STOMP: load_sound_file('ability_stomp_1.ogg', volume=3),
        SoundId.ABILITY_STOMP_HIT: load_sound_file('ability_stomp_hit.ogg', volume=4),
        SoundId.ABILITY_BLOODLUST: load_sound_file('bloodlust.ogg'),
        SoundId.ABILITY_ARCANE_FIRE: load_sound_file('Retro_8-Bit_Game-Alarm_Bell_07.wav'),
        SoundId.WARP: load_sound_file('Retro_8-Bit_Game-Gun_Laser_Weapon_Shoot_Beam_23.wav'),
        SoundId.CONSUMABLE_POTION: load_sound_file('PowerUp04.ogg'),
        SoundId.CONSUMABLE_BUFF: load_sound_file('Retro_8-Bit_Game-Powerup_Achievement_07.wav'),
        SoundId.CONSUMABLE_ACID_BOMB: load_sound_file('poison.ogg', volume=5),  # same as ability Infuse dagger
        SoundId.EVENT_PLAYER_LEVELED_UP: load_sound_file('PowerUp02.ogg'),
        SoundId.EVENT_PICKED_UP: load_sound_file('UI01.ogg'),
        SoundId.EVENT_PICKED_UP_MONEY: load_sound_file('Retro_8-Bit_Game-Pickup_Object_Item_Coin_08.wav'),
        SoundId.EVENT_PURCHASED_SOMETHING: load_sound_file('Retro_8-Bit_Game-Pickup_Object_Item_Coin_08.wav'),
        SoundId.EVENT_SOLD_SOMETHING: load_sound_file('Retro_8-Bit_Game-Pickup_Object_Item_Coin_08.wav'),
        SoundId.EVENT_PLAYER_DIED: load_sound_file('Death01.ogg'),
        SoundId.EVENT_ENEMY_DIED: load_sound_file('Damage02.ogg'),
        SoundId.EVENT_COMPLETED_QUEST: load_sound_file('PowerUp01.ogg'),
        SoundId.EVENT_ACCEPTED_QUEST: load_sound_file('PowerUp01.ogg'),
        SoundId.EVENT_PICKED_TALENT: load_sound_file('Retro_8-Bit_Game-Pickup_Object_Item_Coin_08.wav'),
        SoundId.EVENT_RESET_TALENT: load_sound_file('Retro_8-Bit_Game-Pickup_Object_Item_Coin_08.wav'),
        SoundId.EVENT_SAVED_GAME: load_sound_file('Retro_8-Bit_Game-Pickup_Object_Item_Coin_08.wav'),
        SoundId.DEATH_RAT: load_sound_file('rat_death.ogg', volume=2),
        SoundId.DEATH_GOBLIN: load_sound_file('goblin_1.ogg', 'goblin_2.ogg', 'goblin_3.ogg', 'goblin_4.ogg',
                                              'goblin_5.ogg', volume=2),
        SoundId.DEATH_ZOMBIE: load_sound_file('zombie_death.ogg', 'zombie_death_2.ogg', 'zombie_death_3.ogg'),
        SoundId.DEATH_BOSS: load_sound_file('Retro_8-Bit_Game-Powerup_Achievement_11.wav'),
        SoundId.DEATH_ICE_WITCH: load_sound_file('ice_witch_death_1.ogg', 'ice_witch_death_2.ogg',
                                                 'ice_witch_death_3.ogg', volume=3),
        # TODO create death sound for skeleton mage
        SoundId.DEATH_SKELETON_MAGE: load_sound_file('ice_witch_death_1.ogg', 'ice_witch_death_2.ogg',
                                                     'ice_witch_death_3.ogg', volume=3),
        SoundId.DEATH_HUMAN: load_sound_file('human_death_1.ogg', 'human_death_2.ogg', 'human_death_3.ogg', volume=3),
        SoundId.DEATH_NECRO: load_sound_file('necro_death_1.ogg', 'necro_death_2.ogg', 'necro_death_3.ogg', volume=3),
        SoundId.WARNING: load_sound_file('UI06.ogg'),
        SoundId.INVALID_ACTION: load_sound_file('invalid_action.ogg'),
        SoundId.PLAYER_PAIN: load_sound_file('pain1.ogg', 'pain2.ogg', 'pain3.ogg', 'pain4.ogg'),
        SoundId.ENEMY_ATTACK_GOBLIN_WARLOCK: load_sound_file('goblin_fireball_1.ogg', 'goblin_fireball_2.ogg',
                                                             'goblin_fireball_3.ogg', volume=4),
        # TODO create new sound for skeleton boss magic
        SoundId.ENEMY_MAGIC_SKELETON_BOSS: load_sound_file('goblin_fireball_1.ogg', 'goblin_fireball_2.ogg',
                                                           'goblin_fireball_3.ogg', volume=4),
        SoundId.ENEMY_ATTACK_ICE_WITCH: load_sound_file('enemy_icewitch_ability.ogg', volume=2),
        SoundId.ENEMY_ATTACK_SKELETON_MAGE: load_sound_file('enemy_skeleton_mage_attack_1.ogg',
                                                            'enemy_skeleton_mage_attack_2.ogg', volume=4),
        SoundId.ENEMY_SKELETON_MAGE_HEAL: load_sound_file('enemy_skeleton_mage_heal.ogg', volume=2),
        SoundId.ENEMY_ATTACK_NECRO: load_sound_file('enemy_necro_attack.ogg'),
        SoundId.ENEMY_ATTACK: load_sound_file('enemy_hit.ogg'),
        SoundId.ENEMY_ATTACK_WAS_BLOCKED: load_sound_file('enemy_hit_blocked_2.ogg', volume=0.5),
        SoundId.ENEMY_ATTACK_WAS_DODGED: load_sound_file('combat_dodge_1.ogg', volume=3),
        SoundId.MAGIC_DAMAGE_WAS_RESISTED: load_sound_file('combat_dodge_1.ogg', volume=3),
        SoundId.ENEMY_NECROMANCER_SUMMON: load_sound_file('SciFi01.ogg'),
        SoundId.ENEMY_NECROMANCER_HEAL: load_sound_file('enemy_necro_heal.ogg'),
        SoundId.UI_ITEM_WAS_MOVED: load_sound_file('ui_drag_drop.ogg', volume=3),
        SoundId.UI_ITEM_WAS_DROPPED_ON_GROUND: load_sound_file('UI06.ogg', volume=2),
        SoundId.UI_START_DRAGGING_ITEM: load_sound_file('ui_drag.ogg', volume=3),
        SoundId.UI_TOGGLE: load_sound_file('Retro_8-Bit_Game-Interface_UI_20.wav', volume=2),
        SoundId.DIALOG: load_sound_file('Menu_Select_00.ogg'),
        SoundId.EVENT_PORTAL_ACTIVATED: load_sound_file('UI06.wav'),
        SoundId.FOOTSTEPS: load_sound_file('footsteps_loop.ogg', volume=1)
    }


def play_sound(sound_id: SoundId):
    global muted
    if muted:
        return
    if not _sounds_by_id:
        raise Exception("Initialize sound player before playing sounds!")
    if sound_id in _sounds_by_id:
        sounds = _sounds_by_id[sound_id]
        randomly_chosen_sound = random.choice(sounds)
        if sound_id in LOOPING_SOUNDS:
            randomly_chosen_sound.play(-1)
        else:
            randomly_chosen_sound.play()
    else:
        raise Exception("No sound defined for: " + str(sound_id))


def stop_looping_sound(sound_id: SoundId):
    if sound_id not in LOOPING_SOUNDS:
        raise Exception("Only use this method for looping sounds!")
    if not _sounds_by_id:
        raise Exception("Initialize sound player before playing sounds!")
    if sound_id in _sounds_by_id:
        sounds = _sounds_by_id[sound_id]
        for sound in sounds:
            sound.stop()
    else:
        raise Exception("No sound defined for: " + str(sound_id))


def load_sound_file(*filenames, volume: float = 1):
    sounds = [pygame.mixer.Sound('./resources/sound/' + filename) for filename in filenames]
    for sound in sounds:
        sound.set_volume(0.1 * volume)
    return sounds


# TODO Rework sound_player into a class, to avoid global state
def toggle_muted():
    global muted
    muted = not muted
