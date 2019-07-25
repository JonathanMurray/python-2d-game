import random
from typing import Any, List, Dict

import pygame

from pythongame.core.common import SoundId

_sounds_by_id: Dict[SoundId, List[Any]] = {}


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
        SoundId.ABILITY_SNEAK: load_sound_file('stealth.ogg', volume=3),
        SoundId.ABILITY_INFUSE_DAGGER: load_sound_file('poison.ogg', volume=5),
        SoundId.ABILITY_DASH: load_sound_file('dash.ogg', volume=5),
        SoundId.POTION: load_sound_file('PowerUp04.ogg'),
        SoundId.EVENT_PLAYER_LEVELED_UP: load_sound_file('PowerUp02.ogg'),
        SoundId.EVENT_PICKED_UP: load_sound_file('UI01.ogg'),
        SoundId.EVENT_PICKED_UP_MONEY: load_sound_file('Retro_8-Bit_Game-Pickup_Object_Item_Coin_08.wav'),
        SoundId.EVENT_PURCHASED_SOMETHING: load_sound_file('Retro_8-Bit_Game-Pickup_Object_Item_Coin_08.wav'),
        SoundId.EVENT_PLAYER_DIED: load_sound_file('Death01.ogg'),
        SoundId.EVENT_ENEMY_DIED: load_sound_file('Damage02.ogg'),
        SoundId.DEATH_RAT: load_sound_file('rat_death.ogg', volume=2),
        SoundId.DEATH_ZOMBIE: load_sound_file('zombie_death.ogg', 'zombie_death_2.ogg'),
        SoundId.WARNING: load_sound_file('UI06.ogg'),
        SoundId.INVALID_ACTION: load_sound_file('invalid_action.ogg'),
        SoundId.PLAYER_PAIN: load_sound_file('pain1.ogg', 'pain2.ogg', 'pain3.ogg', 'pain4.ogg'),
        SoundId.ENEMY_ATTACK_GOBLIN_WARLOCK: load_sound_file('Shot08.ogg'),
        SoundId.ENEMY_ATTACK: load_sound_file('enemy_hit.ogg'),
        SoundId.ENEMY_ATTACK_WAS_BLOCKED: load_sound_file('enemy_hit_blocked_2.ogg', volume=0.5)
    }


def play_sound(sound_id: SoundId):
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
