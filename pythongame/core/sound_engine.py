import pygame

from pythongame.core.common import SoundId


class SoundEngine:

    def __init__(self):
        self.sounds = {
            SoundId.ABILITY_FIREBALL: load_sound_file('Shot01.ogg'),
            SoundId.ABILITY_WHIRLWIND: load_sound_file('Fire03.ogg'),
            SoundId.ABILITY_TELEPORT: load_sound_file('SciFi06.ogg'),
            SoundId.ABILITY_ENTANGLING_ROOTS: load_sound_file('SciFi03.ogg'),
            SoundId.POTION: load_sound_file('PowerUp04.ogg'),
            SoundId.EVENT_PLAYER_LEVELED_UP: load_sound_file('PowerUp02.ogg'),
            SoundId.EVENT_PICKED_UP: load_sound_file('UI01.ogg'),
            SoundId.EVENT_PLAYER_DIED: load_sound_file('Death01.ogg'),
            SoundId.EVENT_ENEMY_DIED: load_sound_file('Damage02.ogg'),
            SoundId.WARNING: load_sound_file('UI06.ogg')
        }

    def play_sound(self, sound_id: SoundId):
        if sound_id in self.sounds:
            self.sounds[sound_id].play()
        else:
            raise Exception("No sound defined for: " + str(sound_id))


def load_sound_file(filename: str):
    return pygame.mixer.Sound('./resources/sound/' + filename)
