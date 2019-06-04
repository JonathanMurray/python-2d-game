import pygame

from pythongame.core.common import SoundId


class SoundEngine:

    def __init__(self):
        self.fireball_sound = pygame.mixer.Sound('./resources/sound/Shot01.ogg')
        self.whirlwind_sound = pygame.mixer.Sound('./resources/sound/Fire03.ogg')

    def play_sound(self, sound_id: SoundId):
        if sound_id == SoundId.ABILITY_FIREBALL:
            self.fireball_sound.play()
        elif sound_id == SoundId.ABILITY_WHIRLWIND:
            self.whirlwind_sound.play()
        else:
            raise Exception("Unhandled sound ID: " + str(sound_id))

