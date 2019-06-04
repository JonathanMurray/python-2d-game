import pygame

from pythongame.core.common import SoundId

_sounds = {}


def init_sound_player():
    global _sounds
    if _sounds:
        raise Exception("Don't initialize sound player several times!")
    _sounds = {
        SoundId.ABILITY_FIREBALL: load_sound_file('Shot01.ogg'),
        SoundId.ABILITY_WHIRLWIND: load_sound_file('Fire03.ogg'),
        SoundId.ABILITY_TELEPORT: load_sound_file('SciFi06.ogg'),
        SoundId.ABILITY_ENTANGLING_ROOTS: load_sound_file('SciFi03.ogg'),
        SoundId.POTION: load_sound_file('PowerUp04.ogg'),
        SoundId.EVENT_PLAYER_LEVELED_UP: load_sound_file('PowerUp02.ogg'),
        SoundId.EVENT_PICKED_UP: load_sound_file('UI01.ogg'),
        SoundId.EVENT_PLAYER_DIED: load_sound_file('Death01.ogg'),
        SoundId.EVENT_ENEMY_DIED: load_sound_file('Damage02.ogg'),
        SoundId.WARNING: load_sound_file('UI06.ogg'),
        SoundId.PLAYER_PAIN: load_sound_file('pain1.ogg')
    }


def play_sound(sound_id: SoundId):
    if not _sounds:
        raise Exception("Initialize sound player before playing sounds!")
    if sound_id in _sounds:
        _sounds[sound_id].play()
    else:
        raise Exception("No sound defined for: " + str(sound_id))


def load_sound_file(filename: str):
    sound = pygame.mixer.Sound('./resources/sound/' + filename)
    sound.set_volume(0.1)
    return sound
