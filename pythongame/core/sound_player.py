import random
from typing import Any, List, Dict

import pygame

from pythongame.core.common import SoundId

_sounds_by_id: Dict[SoundId, List[Any]] = {}

muted = False


def init_sound_player():
    global _sounds_by_id
    if _sounds_by_id:
        raise Exception("Don't initialize sound player several times!")
    _sounds_by_id = {
        SoundId.ABILITY_FIREBALL: load_sound_file('Shot01.ogg'),
        SoundId.ABILITY_WHIRLWIND: load_sound_file('Fire03.ogg'),
        SoundId.ABILITY_TELEPORT: load_sound_file('SciFi06.ogg'),
        SoundId.ABILITY_ENTANGLING_ROOTS: load_sound_file('SciFi03.ogg'),
        SoundId.ABILITY_CHARGE: load_sound_file('Retro_8-Bit_Game-Misc_Noise_12.wav'),
        SoundId.ABILITY_SHIV: load_sound_file('dagger_1.ogg', 'dagger_2.ogg'),
        SoundId.ABILITY_SHIV_STEALTHED: load_sound_file('Slash04.ogg'),
        SoundId.ABILITY_STEALTH: load_sound_file('stealth.ogg', volume=3),
        SoundId.ABILITY_INFUSE_DAGGER: load_sound_file('poison.ogg', volume=5),
        SoundId.ABILITY_DASH: load_sound_file('dash.ogg', volume=5),
        SoundId.ABILITY_SLASH: load_sound_file('Retro_8-Bit_Game-Gun_Laser_Weapon_Shoot_Beam_01.wav',
                                               'Retro_8-Bit_Game-Gun_Laser_Weapon_Shoot_Beam_02.wav'),
        SoundId.ABILITY_STOMP: load_sound_file('Slash01.ogg'),
        SoundId.ABILITY_BLOODLUST: load_sound_file('bloodlust.ogg'),
        SoundId.ABILITY_ARCANE_FIRE: load_sound_file('Retro_8-Bit_Game-Alarm_Bell_07.wav'),
        SoundId.WARP: load_sound_file('Retro_8-Bit_Game-Gun_Laser_Weapon_Shoot_Beam_23.wav'),
        SoundId.CONSUMABLE_POTION: load_sound_file('PowerUp04.ogg'),
        SoundId.CONSUMABLE_BUFF: load_sound_file('Retro_8-Bit_Game-Powerup_Achievement_07.wav'),
        SoundId.EVENT_PLAYER_LEVELED_UP: load_sound_file('PowerUp02.ogg'),
        SoundId.EVENT_PICKED_UP: load_sound_file('UI01.ogg'),
        SoundId.EVENT_PICKED_UP_MONEY: load_sound_file('Retro_8-Bit_Game-Pickup_Object_Item_Coin_08.wav'),
        SoundId.EVENT_PURCHASED_SOMETHING: load_sound_file('Retro_8-Bit_Game-Pickup_Object_Item_Coin_08.wav'),
        SoundId.EVENT_PLAYER_DIED: load_sound_file('Death01.ogg'),
        SoundId.EVENT_ENEMY_DIED: load_sound_file('Damage02.ogg'),
        SoundId.EVENT_COMPLETED_QUEST: load_sound_file('PowerUp01.ogg'),
        SoundId.EVENT_PICKED_TALENT: load_sound_file('Retro_8-Bit_Game-Pickup_Object_Item_Coin_08.wav'),
        SoundId.DEATH_RAT: load_sound_file('rat_death.ogg', volume=2),
        SoundId.DEATH_ZOMBIE: load_sound_file('zombie_death.ogg', 'zombie_death_2.ogg'),
        SoundId.DEATH_BOSS: load_sound_file('Retro_8-Bit_Game-Powerup_Achievement_11.wav'),
        SoundId.WARNING: load_sound_file('UI06.ogg'),
        SoundId.INVALID_ACTION: load_sound_file('invalid_action.ogg'),
        SoundId.PLAYER_PAIN: load_sound_file('pain1.ogg', 'pain2.ogg', 'pain3.ogg', 'pain4.ogg'),
        SoundId.ENEMY_ATTACK_GOBLIN_WARLOCK: load_sound_file('Shot08.ogg'),
        SoundId.ENEMY_ATTACK: load_sound_file('enemy_hit.ogg'),
        SoundId.ENEMY_ATTACK_WAS_BLOCKED: load_sound_file('enemy_hit_blocked_2.ogg', volume=0.5),
        SoundId.ENEMY_NECROMANCER_SUMMON: load_sound_file('SciFi01.ogg'),
        SoundId.UI_ITEM_WAS_MOVED: load_sound_file('UI04.ogg'),
        SoundId.UI_ITEM_WAS_DROPPED_ON_GROUND: load_sound_file('UI06.ogg', volume=2),
        SoundId.UI_START_DRAGGING_ITEM: load_sound_file('drag.ogg'),
        SoundId.UI_TOGGLE: load_sound_file('Retro_8-Bit_Game-Interface_UI_20.wav', volume=2),
        SoundId.DIALOG: load_sound_file('UI04.ogg'),
        SoundId.EVENT_PORTAL_ACTIVATED: load_sound_file('UI06.wav')
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
        randomly_chosen_sound.play()
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
