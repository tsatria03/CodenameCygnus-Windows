"""Playing an episode, by what is said and played: nothing is heard, and no window opens.

The audio here is a stand-in that notes what it was asked to play. A voice ends only when
a test says so, so every step of the story can be checked in order; a state with no voice
ends on the next frame, as with the real audio.
"""
import _quiet  # noqa: F401  first, before any of the game

import importlib.util
import os
import tempfile
import types

import pygame

from codenamecygnus.app import App
from codenamecygnus.game.episode_screen import (EpisodeScreen, PauseMenu, choices_text,
                                                heading_text, script_line)
from codenamecygnus.game.heard import Heard
from codenamecygnus.game.stand_in_menu import StandInMainMenu
from codenamecygnus.game.story import Story
from codenamecygnus.platform import runloop
from codenamecygnus.platform.keymap import KeyMap
from codenamecygnus.platform.runloop import RunLoop
from codenamecygnus.platform.settings import Settings

STORY = Story()


class Ear:
    def __init__(self):
        self.heard = []
        self.last = ''

    def speak(self, text, interrupt=True):
        self.heard.append((text, interrupt))
        self.last = text
        return True

    @property
    def said(self):
        return [t for t, _i in self.heard]


class FakeAudio:
    """Notes what the story asks for; ``end_voice()`` ends the voice playing."""

    def __init__(self, settings):
        self.settings = settings
        self.ok = True
        self.paused = False
        self.voice = self.background = self.decision = None
        self.on_end = None
        self.voices = []            # every voice started, replays included
        self.seeks = []
        self.menu_sounds = []

    def open(self, pygame):
        pass

    def close(self):
        pass

    def update(self):
        """As the real audio does: a state with no voice ends on the next frame."""
        while self.voice is None and self.on_end is not None and not self.paused:
            self.end_voice()

    def play_voice(self, recording, start=0.0, on_end=None):
        self.voice, self.on_end = recording, on_end
        if recording is not None:
            self.voices.append(recording)

    def end_voice(self):
        assert not self.paused, 'a paused voice cannot end'
        callback, self.on_end, self.voice = self.on_end, None, None
        callback()

    def replay(self):
        self.voices.append(self.voice)

    def stop_voice(self):
        self.voice = self.on_end = None

    def play_menu(self, recording):
        self.menu_sounds.append(recording)

    def seek(self, delta):
        self.seeks.append(delta)

    def set_background(self, recording):
        self.background = recording

    def start_decision(self, recording):
        self.decision = recording

    def stop_decision(self):
        self.decision = None

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop_all(self):
        self.voice = self.background = self.decision = self.on_end = None
        self.paused = False

    def step_volume(self, key, step):
        return '%s %+d' % (key, step)


class Names:
    """Stands in for the recordings: a story file name is its own recording."""

    def find(self, file_name):
        return file_name

    def menu_sound(self, name):
        return name


def fresh_heard():
    return Heard(os.path.join(tempfile.mkdtemp(dir=_quiet.FOLDER), 'heard.json'))


def make_app(debug=False, episode=None):
    folder = tempfile.mkdtemp(dir=_quiet.FOLDER)
    settings = Settings(os.path.join(folder, 'settings.json'))
    options = types.SimpleNamespace(debug=debug, episode=episode, state=None, verbose=False,
                                    exit_after=None)
    return App(options, speech=Ear(), settings=settings,
               keymap=KeyMap(os.path.join(folder, 'keys.json')), loop=RunLoop(),
               audio=FakeAudio(settings))


def start(episode_id='1.1.1', menu=True, heard=None):
    app = make_app()
    if menu:
        app.stack.push(StandInMainMenu(app))
    screen = EpisodeScreen(app, STORY.episodes[episode_id], story=STORY, recordings=Names(),
                           heard=heard if heard is not None else fresh_heard())
    app.stack.push(screen)
    app.audio.update()
    return app, screen


def until_choices(app, screen):
    """End voices until a choice is offered or the episode is complete."""
    for _ in range(500):
        if screen.offered or screen.complete:
            return
        app.audio.end_voice()
        app.audio.update()
    raise AssertionError('no choice came')


def jump(app, screen, name):
    """Play from any state, as the story would on reaching it."""
    screen.play(screen.run.enter(name))
    app.audio.update()


def end_voice(app):
    app.audio.end_voice()
    app.audio.update()


def key(app, name, mods=()):
    app.key_down(name, list(mods))
    app.audio.update()


def test_the_prologue_starts_with_its_first_scene():
    app, screen = start()
    first = STORY.state('001introOpen')
    assert app.audio.voice == first.voice and app.audio.background == first.background
    assert app.audio.decision is None, 'the decision loop came before the question'


def test_the_choices_come_after_the_question_with_the_decision_loop():
    app, screen = start()
    until_choices(app, screen)
    assert screen.run.current.name == '001introOpen'
    assert app.audio.decision == STORY.state('001introOpen').decision
    assert app.speech.heard[-1] == ('Two cards.', False)


def test_choices_are_read_together_by_their_words():
    assert choices_text(STORY.choices('012introRejectPrompt')) == 'Charismatic or Hostile.'
    assert choices_text(STORY.choices('027myraTacticPrompt_m1e8')).count(',') == 1


def test_up_and_down_say_each_choice_without_its_place_and_wrap():
    app, screen = start()
    jump(app, screen, '012introRejectPrompt')
    end_voice(app)
    key(app, 'down')
    key(app, 'down')
    key(app, 'down')
    key(app, 'up')
    assert app.speech.said[-4:] == ['Charismatic', 'Hostile', 'Charismatic', 'Hostile']


def test_enter_chooses_the_one_moved_to_and_says_it():
    app, screen = start()
    jump(app, screen, '012introRejectPrompt')
    end_voice(app)
    key(app, 'up')                                  # from nothing, Up is the last
    key(app, 'return')
    assert app.speech.said[-1] == 'Hostile'
    hostile = next(c for c in STORY.choices('012introRejectPrompt') if c.text == 'HOSTILE')
    assert screen.run.current.name == hostile.destination
    assert app.audio.decision is None and screen.offered == []


def test_enter_before_moving_says_the_choices_rather_than_guessing():
    app, screen = start()
    jump(app, screen, '012introRejectPrompt')
    end_voice(app)
    key(app, 'return')
    assert screen.run.current.name == '012introRejectPrompt'
    assert app.speech.heard[-1] == ('Charismatic or Hostile.', True)


def test_the_number_keys_choose_directly():
    app, screen = start()
    jump(app, screen, '012introRejectPrompt')
    end_voice(app)
    key(app, '3')
    assert app.speech.said[-1] == 'There are only 2.'
    key(app, '2')
    assert screen.run.current.name == STORY.choices('012introRejectPrompt')[1].destination


def test_c_says_the_choices_again_and_choice_keys_wait_for_a_question():
    app, screen = start()
    key(app, 'c')
    key(app, 'down')
    key(app, '1')
    assert app.speech.said[-3:] == ['No choices yet.'] * 3
    until_choices(app, screen)
    key(app, 'c')
    assert app.speech.heard[-1] == ('Two cards.', True)


def test_space_pauses_and_resumes_and_says_so():
    app, screen = start()
    key(app, 'space')
    assert app.audio.paused and app.speech.said[-1] == 'Paused.'
    key(app, 'space')
    assert not app.audio.paused and app.speech.said[-1] == 'Resumed.'


def test_r_replays_and_left_and_right_skip_5_seconds():
    app, screen = start()
    key(app, 'r')
    key(app, 'left')
    key(app, 'right')
    assert app.audio.voices == [STORY.state('001introOpen').voice] * 2
    assert app.audio.seeks == [-5.0, 5.0]


def test_r_at_a_choice_asks_the_question_again_then_offers_the_choices():
    app, screen = start()
    jump(app, screen, '012introRejectPrompt')
    end_voice(app)
    key(app, 'r')
    assert screen.offered == [] and app.audio.decision is None
    assert app.audio.voice == STORY.state('012introRejectPrompt').voice
    end_voice(app)
    assert screen.offered and app.audio.decision is not None
    assert app.speech.said[-1] == 'Charismatic or Hostile.'


def test_h_says_the_scene_heading_in_plain_words():
    assert heading_text('CONSULATE - BOMB ROOM') == 'Consulate, bomb room'
    app, screen = start()
    key(app, 'h')
    assert app.speech.said[-1] == 'Casino, back room, card table'


def test_the_volume_keys_say_the_new_level():
    app, screen = start()
    key(app, 'page down')
    key(app, 'home', ['shift'])
    key(app, 'page up', ['shift'])
    assert app.speech.said[-3:] == ['ambience_volume -1', 'master_volume +1', 'decision_volume +1']


def test_a_timed_choice_moves_on_by_itself_after_7_seconds():
    app, screen = start('1.8.1')
    jump(app, screen, '009drinkPrompt_m1e8')
    end_voice(app)
    app.loop.pump(runloop.clock() + 6.5)
    assert screen.run.current.name == '009drinkPrompt_m1e8'
    app.loop.pump(runloop.clock() + 7.5)
    assert screen.run.current.name == '010Ctimeout_m1e8'


def test_a_timed_choice_keeps_its_seconds_while_paused():
    app, screen = start('1.8.1')
    jump(app, screen, '009drinkPrompt_m1e8')
    end_voice(app)
    key(app, 'space')
    app.loop.pump(runloop.clock() + 60)
    assert screen.run.current.name == '009drinkPrompt_m1e8', 'it ran out while paused'
    key(app, 'space')
    app.loop.pump(runloop.clock() + 7.5)
    assert screen.run.current.name == '010Ctimeout_m1e8'


def test_choosing_in_time_stops_the_clock():
    app, screen = start('1.8.1')
    jump(app, screen, '009drinkPrompt_m1e8')
    end_voice(app)
    key(app, '1')
    chosen = screen.run.current.name
    app.loop.pump(runloop.clock() + 8)
    assert screen.run.current.name == chosen == '010AmartiniDrink_m1e8'


def test_escape_opens_the_pause_menu_and_resume_carries_on():
    app, screen = start()
    key(app, 'escape')
    assert isinstance(app.stack.top, PauseMenu) and app.audio.paused
    assert app.speech.said[-2:] == ['Paused.', 'Resume']
    key(app, 'return')
    assert app.stack.top is screen and not app.audio.paused


def test_escape_in_the_pause_menu_resumes_too():
    app, screen = start()
    key(app, 'escape')
    key(app, 'escape')
    assert app.stack.top is screen and not app.audio.paused


def test_return_to_menu_stops_the_story_and_opens_the_menu():
    app, screen = start()
    key(app, 'escape')
    key(app, 'end')
    assert app.speech.said[-1] == 'Return to menu'
    key(app, 'return')
    assert isinstance(app.stack.top, StandInMainMenu)
    assert app.audio.voice is None and app.audio.background is None
    assert app.speech.said[-2] == 'Codename Cygnus. Main menu.'


def test_settings_from_the_pause_menu_keeps_the_story_paused():
    app, screen = start()
    key(app, 'escape')
    key(app, 'down')
    key(app, 'down')
    assert app.speech.said[-1] == 'Settings'
    key(app, 'return')
    assert app.stack.top.name == 'settings' and app.audio.paused
    key(app, 'escape')
    assert isinstance(app.stack.top, PauseMenu) and app.audio.paused


def test_f1_pauses_the_story_until_it_closes():
    app, screen = start()
    key(app, 'f1')
    assert app.audio.paused
    key(app, 'escape')
    assert app.stack.top is screen and not app.audio.paused


def test_a_story_paused_with_space_stays_paused_after_f1():
    app, screen = start()
    key(app, 'space')
    key(app, 'f1')
    key(app, 'escape')
    assert app.audio.paused


def test_losing_the_window_pauses_and_coming_back_carries_on():
    app, screen = start()
    screen.focus_lost()
    assert app.audio.paused
    screen.focus_gained()
    assert not app.audio.paused


def test_the_end_says_episode_complete_and_enter_returns_to_the_menu():
    app, screen = start()
    episode = STORY.episodes['1.1.1']
    jump(app, screen, episode.end)
    if app.audio.voice is not None:                 # the Prologue's end has none
        end_voice(app)
    assert screen.complete
    said = app.speech.said
    assert said[-2].startswith('Episode complete!') and episode.completion_text.strip() in said[-2]
    key(app, 'down')
    assert screen.run.current.name == episode.end
    key(app, 'return')
    assert isinstance(app.stack.top, StandInMainMenu)


def test_the_prologue_plays_through_by_its_keys():
    app, screen = start()
    for _ in range(200):
        until_choices(app, screen)
        if screen.complete:
            break
        key(app, '1')
    assert screen.complete and screen.run.current.name == STORY.episodes['1.1.1'].end


def test_the_window_shows_the_script_without_its_pacing_marks():
    line = STORY.state('001introOpen').script[3]
    assert script_line(line).startswith('Miss Honeybourne: (VIA EARPIECE) Is your earpiece')
    app, screen = start()
    until_choices(app, screen)
    text = '\n'.join(screen.lines())
    assert '#' not in text and 'Episode 1: Prologue' in text and '1. Two cards' in text


def test_left_right_home_and_end_move_through_a_waiting_choice():
    app, screen = start('1.8.1')
    jump(app, screen, '027myraTacticPrompt_m1e8')
    end_voice(app)
    words = [c.spoken for c in screen.offered]
    key(app, 'right')
    key(app, 'right')
    key(app, 'left')
    key(app, 'end')
    key(app, 'home')
    assert app.speech.said[-5:] == [words[0], words[1], words[0], words[-1], words[0]]
    assert app.audio.seeks == [], 'a choice key skipped through a recording'


def test_left_and_right_still_skip_while_the_story_plays():
    app, screen = start()
    before = len(app.speech.said)
    key(app, 'right')
    key(app, 'home')                                # nothing to move through yet
    assert app.audio.seeks == [5.0] and len(app.speech.said) == before


def test_the_pause_menu_has_restart_after_resume():
    app, screen = start()
    key(app, 'escape')
    assert [r.text for r in app.stack.top.rows()] == ['Resume', 'Restart episode', 'Settings',
                                                      'Return to menu']


def test_restart_asks_first_and_no_keeps_the_place():
    app, screen = start()
    until_choices(app, screen)
    key(app, 'escape')
    key(app, 'down')
    key(app, 'return')
    assert app.speech.said[-2:] == ['Restart episode?', 'No']
    key(app, 'return')                              # No
    assert isinstance(app.stack.top, PauseMenu)
    key(app, 'down')
    key(app, 'return')
    key(app, 'escape')                              # Escape is No too
    assert isinstance(app.stack.top, PauseMenu)
    key(app, 'escape')
    assert app.stack.top is screen and screen.offered


def test_yes_restarts_the_episode_from_its_start():
    app, screen = start()
    screen.run.variables['event.m1e1_cardsWin'] = 1     # as if the cards had been won
    jump(app, screen, '012introRejectPrompt')
    key(app, 'escape')
    key(app, 'down')
    key(app, 'return')
    key(app, 'down')
    key(app, 'return')                              # Yes
    again = app.stack.top
    assert isinstance(again, EpisodeScreen) and again is not screen
    assert again.run.current.name == '001introOpen'
    assert 'event.m1e1_cardsWin' not in again.run.variables
    assert not app.audio.paused and app.audio.voice == STORY.state('001introOpen').voice
    assert app.speech.said[-1] == 'Restarting Prologue.'
    key(app, 'escape')
    key(app, 'end')
    key(app, 'return')                              # Return to menu still goes to the menu
    assert isinstance(app.stack.top, StandInMainMenu)


def test_holding_a_skip_key_repeats_it_until_it_is_let_go():
    app, screen = start()
    t = runloop.clock()
    app.key_down('right', [], now=t)
    app.repeat_keys(now=t + 0.2)                    # not held long enough yet
    app.repeat_keys(now=t + 0.45)
    app.repeat_keys(now=t + 0.5)                    # too soon after the last
    app.repeat_keys(now=t + 0.65)
    assert app.audio.seeks == [5.0, 5.0, 5.0]
    app.key_up('right')
    app.repeat_keys(now=t + 2)
    assert app.audio.seeks == [5.0, 5.0, 5.0]


def test_holding_a_volume_key_repeats_it_with_its_modifier():
    app, screen = start()
    before = len(app.speech.said)
    t = runloop.clock()
    app.key_down('home', ['shift'], now=t)
    app.repeat_keys(now=t + 0.45)
    assert app.speech.said[before:] == ['master_volume +1'] * 2
    app.key_up('left shift')                        # letting go of Shift stops it
    app.repeat_keys(now=t + 2)
    assert len(app.speech.said) == before + 2


def test_space_enter_and_the_choice_keys_never_repeat():
    app, screen = start()
    before = len(app.speech.said)
    t = runloop.clock()
    app.key_down('space', [], now=t)
    app.repeat_keys(now=t + 2)
    assert app.speech.said[before:] == ['Paused.']
    key(app, 'space')
    jump(app, screen, '012introRejectPrompt')
    end_voice(app)
    for name in ('right', 'down', 'return'):
        app.key_down(name, [], now=t)
        assert app.held is None, name


def test_a_held_skip_stops_repeating_when_a_choice_comes():
    app, screen = start()
    t = runloop.clock()
    app.key_down('right', [], now=t)
    until_choices(app, screen)
    app.repeat_keys(now=t + 1)
    assert app.audio.seeks == [5.0] and app.held is None


def test_a_recording_heard_to_its_end_is_remembered_for_good():
    heard = fresh_heard()
    app, screen = start(heard=heard)
    assert '001introOpen.m4a' not in heard, 'starting it was taken for hearing it'
    until_choices(app, screen)
    assert '001introOpen.m4a' in heard
    assert '001INTROOPEN.mp3' in Heard(heard.file.path), 'not kept in the file by its name'


def test_s_on_a_recording_not_heard_yet_does_nothing():
    app, screen = start()
    key(app, 's')
    assert app.speech.said[-1] == 'Not heard yet.'
    assert screen.run.current.name == '001introOpen' and not screen.offered
    assert app.audio.menu_sounds == []


def test_s_at_the_choices_says_so():
    app, screen = start()
    until_choices(app, screen)
    key(app, 's')
    assert app.speech.said[-1] == 'Already at the choices.'


def test_s_skips_across_every_heard_recording_to_the_next_choice():
    heard = fresh_heard()
    first, first_screen = start(heard=heard)        # a first time through, heard in full
    until_choices(first, first_screen)
    key(first, '1')
    until_choices(first, first_screen)
    played = dict(first_screen.run.variables)
    waiting_at = first_screen.run.current.name

    app, screen = start(heard=heard)                # and again, skipping
    key(app, 's')                                   # the question at the card table
    assert screen.offered and screen.run.current.name == '001introOpen'
    assert app.audio.menu_sounds == ['PushButton D']
    key(app, '1')
    key(app, 's')
    assert screen.run.current.name == waiting_at and screen.offered
    assert app.audio.voice is None and app.audio.decision == STORY.state(waiting_at).decision
    assert app.audio.background == STORY.state(waiting_at).background
    assert screen.run.variables == played, 'skipping changed how the story turned out'
    assert app.speech.said[-1] == choices_text(screen.offered)


def test_s_stops_at_a_recording_not_heard_yet_and_plays_it_from_its_start():
    # In Art Show, the response to calling out the artist goes on by itself to the crowd
    # dispersing, two recordings in a row.
    first, then = STORY.state('021M_callouttheartistResponse'), STORY.state('022disperseCrowdAccomplished')
    assert STORY.next_state(first.name, {}) == then.name and then.voice
    heard = fresh_heard()
    heard.add(first.voice)
    app, screen = start('1.2.1', heard=heard)
    jump(app, screen, first.name)
    key(app, 's')
    assert screen.run.current.name == then.name and not screen.offered
    assert app.audio.voice == then.voice and app.audio.voices[-1] == then.voice


def test_the_heard_recordings_last_through_a_restart():
    heard = fresh_heard()
    app, screen = start(heard=heard)
    until_choices(app, screen)
    screen.restart()
    app.audio.update()
    again = app.stack.top
    assert again.heard is heard
    key(app, 's')
    assert again.offered


def entry():
    spec = importlib.util.spec_from_file_location('cygnus_entry',
                                                  os.path.join(_quiet.ROOT, 'CodenameCygnus.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_episode_on_the_command_line_starts_it_past_the_menu():
    e = entry()
    app = make_app(episode='1.3.1')
    screen = e.episode_from_options(app, app.options)
    assert isinstance(screen, EpisodeScreen) and screen.episode.title == "Neptune's Lair"
    app.options.episode = '1.9.1'
    assert e.episode_from_options(app, app.options) is None


def test_the_menu_waits_silently_under_an_episode_started_at_once():
    app = make_app(episode='1.1.1')
    app.options.exit_after = 0.2
    screen = EpisodeScreen(app, STORY.episodes['1.1.1'], story=STORY, recordings=Names())
    app.run(StandInMainMenu(app), pygame, on_top=screen)
    assert 'Codename Cygnus. Main menu.' not in app.speech.said
    assert app.audio.voices[0] == STORY.state('001introOpen').voice


if __name__ == '__main__':
    _quiet.run_tests(globals())
