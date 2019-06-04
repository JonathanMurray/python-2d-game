import pygame

from pythongame.core.common import SoundId


class SoundEngine:

    def __init__(self):
        self.sounds = {
            SoundId.ABILITY_FIREBALL: pygame.mixer.Sound('./resources/sound/Shot01.ogg'),
            SoundId.ABILITY_WHIRLWIND: pygame.mixer.Sound('./resources/sound/Fire03.ogg'),
            SoundId.POTION: pygame.mixer.Sound('./resources/sound/PowerUp04.ogg'),
            SoundId.EVENT_PLAYER_LEVELED_UP: pygame.mixer.Sound('./resources/sound/PowerUp02.ogg')
        }

    def play_sound(self, sound_id: SoundId):
        if sound_id in self.sounds:
            self.sounds[sound_id].play()
        else:
            raise Exception("No sound defined for: " + str(sound_id))
