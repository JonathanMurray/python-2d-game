from pythongame.core.common import SoundId
from pythongame.core.sound_player import play_sound, stop_looping_sound


def play_or_stop_footstep_sounds(is_moving:bool):
    if is_moving:
        play_sound(SoundId.FOOTSTEPS)
    else:
        stop_looping_sound(SoundId.FOOTSTEPS)

