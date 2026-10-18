"""The audio layers, on SDL's dummy sound driver: nothing here is ever heard."""
import _quiet  # noqa: F401  first, before any of the game

import os
import tempfile
import time

import pygame

from codenamecygnus.game.recordings import Recording, Recordings
from codenamecygnus.platform.audio import (BACKGROUND, DECISION, Audio, mp3_length, percent_gain)
from codenamecygnus.platform.settings import Settings

MENU = Recordings()


def sound(name):
    return MENU.menu_sound(name)


def make():
    settings = Settings(os.path.join(tempfile.mkdtemp(dir=_quiet.FOLDER), 'settings.json'))
    return Audio(settings, pygame)


def wait_for(audio, seconds):
    end = time.perf_counter() + seconds
    while time.perf_counter() < end:
        audio.update()
        time.sleep(0.02)


def test_the_sound_device_opens_on_the_dummy_driver():
    assert make().ok


def test_an_mp3s_length_is_read_from_its_headers():
    for name in ('Sound A', '1930Radio A', 'PushButton D'):
        rec = sound(name)
        with open(rec.path, 'rb') as f:
            data = f.read()
        decoded = pygame.mixer.Sound(rec.path).get_length()
        assert abs(mp3_length(data) - decoded) < 0.1, (name, mp3_length(data), decoded)


def test_something_that_is_not_an_mp3_has_no_length():
    assert mp3_length(b'not a sound at all') is None


def test_a_voice_tells_the_story_when_it_ends():
    audio = make()
    ended = []
    audio.play_voice(sound('Sound A'), on_end=lambda: ended.append(1))
    wait_for(audio, 2.0)
    assert ended == [1] and audio.voice is None


def test_a_paused_voice_never_counts_as_ended():
    audio = make()
    ended = []
    audio.play_voice(sound('Sound A'), on_end=lambda: ended.append(1))
    audio.pause()
    wait_for(audio, 1.5)
    assert ended == [], 'a pause was taken for the end'
    position = audio.position()
    audio.resume()
    assert abs(audio.position() - position) < 0.05
    wait_for(audio, 2.0)
    assert ended == [1]


def test_skipping_past_the_end_ends_the_voice_as_reaching_it_does():
    audio = make()
    ended = []
    audio.play_voice(sound('1930Radio A'), on_end=lambda: ended.append(1))
    audio.seek(5.0)
    assert ended == [1]


def test_skipping_back_before_the_start_goes_to_the_start():
    audio = make()
    audio.play_voice(sound('Sound A'))
    audio.seek(-5.0)
    assert audio.position() < 0.1


def test_a_missing_voice_ends_at_once_so_the_story_never_waits():
    audio = make()
    ended = []
    audio.play_voice(None, on_end=lambda: ended.append(1))
    audio.update()
    assert ended == [1]


def test_the_same_background_carries_on_and_another_cuts_over():
    audio = make()
    a, b = sound('1930Radio A'), sound('1930Radio B')
    audio.set_background(a)
    channel = pygame.mixer.Channel(BACKGROUND)
    first = channel.get_sound()
    audio.set_background(Recording(a.name, path=a.path))   # the next state, same file
    assert channel.get_sound() is first, 'the same background restarted'
    audio.set_background(b)
    assert audio.background == b.name and channel.get_sound() is not first
    audio.set_background(None)
    assert audio.background is None and not channel.get_busy()


def test_the_decision_loop_starts_and_stops():
    audio = make()
    audio.start_decision(sound('Sound A'))
    assert audio.decision and pygame.mixer.Channel(DECISION).get_busy()
    audio.stop_decision()
    assert audio.decision is None and not pygame.mixer.Channel(DECISION).get_busy()


def test_volumes_step_by_ten_say_their_level_and_stop_at_the_ends():
    audio = make()
    assert audio.step_volume('ambience_volume', -1) == 'Ambience 90 percent'
    assert audio.settings.get('ambience_volume') == 90
    for _ in range(12):
        audio.step_volume('ambience_volume', -1)
    assert audio.step_volume('ambience_volume', -1) == 'Ambience 0 percent'
    assert audio.step_volume('master_volume', 1) == 'Master volume 100 percent'


def test_master_moves_everything_and_the_others_only_their_own():
    audio = make()
    audio.settings.set('master_volume', 50)
    audio.settings.set('ambience_volume', 50)
    audio.apply_volumes()
    assert abs(audio.gain(None) - 0.25) < 1e-9
    assert abs(audio.gain(BACKGROUND) - 0.0625) < 1e-9
    assert abs(audio.gain(DECISION) - 0.25) < 1e-9
    assert percent_gain(0) == 0 and percent_gain(100) == 1


def test_stop_all_stops_every_layer():
    audio = make()
    audio.play_voice(sound('Sound A'))
    audio.set_background(sound('1930Radio A'))
    audio.start_decision(sound('1930Radio B'))
    audio.stop_all()
    assert audio.voice is None and audio.background is None and audio.decision is None


if __name__ == '__main__':
    _quiet.run_tests(globals())
