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
from codenamecygnus.game.episode_screen import (RESTART_WARNING, EpisodeScreen, PauseMenu,
                                                choices_text, heading_text, script_line)
from codenamecygnus.game.achievements import ACHIEVEMENTS, Achievements, short_id
from codenamecygnus.game.debug import JumpScreen, MatchMenu
from codenamecygnus.game.episode_end import EndMenu, PreviewPauseMenu, PreviewScreen
from codenamecygnus.game.heard import Heard
from codenamecygnus.game.menus import MainMenu
from codenamecygnus.game.progress import Progress
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
    # Each test its own progress, so one test's episodes never show in the next's menus.
    Progress._shared = Progress(os.path.join(folder, 'progress.json'), story=STORY)
    settings = Settings(os.path.join(folder, 'settings.json'))
    options = types.SimpleNamespace(debug=debug, episode=episode, state=None, verbose=False,
                                    exit_after=None)
    return App(options, speech=Ear(), settings=settings,
               keymap=KeyMap(os.path.join(folder, 'keys.json')), loop=RunLoop(),
               audio=FakeAudio(settings))


def fresh_achievements():
    return Achievements(os.path.join(tempfile.mkdtemp(dir=_quiet.FOLDER), 'achievements.json'))


def start(episode_id='1.1.1', menu=True, heard=None, debug=False, achievements=None):
    app = make_app(debug=debug)
    if menu:
        app.stack.push(MainMenu(app))
    screen = EpisodeScreen(app, STORY.episodes[episode_id], story=STORY, recordings=Names(),
                           heard=heard if heard is not None else fresh_heard(),
                           achievements=achievements if achievements is not None
                           else fresh_achievements())
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
    assert app.speech.heard[-1] == ('Two cards', False)


def test_with_several_choices_the_first_is_focused_and_said_and_c_says_them_all():
    app, screen = start()
    jump(app, screen, '012introRejectPrompt')
    end_voice(app)
    assert screen.index == 0 and app.speech.heard[-1] == ('Charismatic', False)
    key(app, 'c')
    assert app.speech.heard[-1] == ('Charismatic or Hostile.', True)


def test_choices_are_read_together_by_their_words():
    assert choices_text(STORY.choices('012introRejectPrompt')) == 'Charismatic or Hostile.'
    assert choices_text(STORY.choices('027myraTacticPrompt_m1e8')).count(',') == 1


def test_up_and_down_say_each_choice_without_its_place_and_wrap():
    app, screen = start()
    jump(app, screen, '012introRejectPrompt')
    end_voice(app)
    key(app, 'down')                                # from the first, Charismatic
    key(app, 'down')                                # wraps round
    key(app, 'up')
    key(app, 'up')
    assert app.speech.said[-4:] == ['Hostile', 'Charismatic', 'Hostile', 'Charismatic']


def test_enter_chooses_the_one_moved_to_and_says_it():
    app, screen = start()
    jump(app, screen, '012introRejectPrompt')
    end_voice(app)
    key(app, 'up')                                  # from the first, Up wraps to the last
    key(app, 'return')
    assert app.speech.said[-1] == 'Hostile'
    hostile = next(c for c in STORY.choices('012introRejectPrompt') if c.text == 'HOSTILE')
    assert screen.run.current.name == hostile.destination
    assert app.audio.decision is None and screen.offered == []


def test_enter_before_moving_chooses_the_first():
    app, screen = start()
    jump(app, screen, '012introRejectPrompt')
    end_voice(app)
    key(app, 'return')
    first = STORY.choices('012introRejectPrompt')[0]
    assert app.speech.said[-1] == 'Charismatic' and screen.run.current.name == first.destination


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


def test_space_does_nothing_during_the_story():
    app, screen = start()
    before = len(app.speech.said)
    key(app, 'space')
    assert not app.audio.paused and len(app.speech.said) == before and app.stack.top is screen


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
    assert app.speech.said[-1] == 'Charismatic'


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
    key(app, 'escape')                              # the pause menu
    app.loop.pump(runloop.clock() + 60)
    assert screen.run.current.name == '009drinkPrompt_m1e8', 'it ran out while paused'
    key(app, 'escape')                              # Resume
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
    assert isinstance(app.stack.top, MainMenu)
    assert app.audio.voice is None and app.audio.background is None
    assert app.speech.said[-2] == 'Main menu.'


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


def test_f1_from_the_pause_menu_leaves_the_story_paused():
    app, screen = start()
    key(app, 'escape')                              # the pause menu
    key(app, 'f1')
    key(app, 'escape')
    assert isinstance(app.stack.top, PauseMenu) and app.audio.paused


def test_losing_the_window_pauses_and_coming_back_carries_on():
    app, screen = start()
    screen.focus_lost()
    assert app.audio.paused
    screen.focus_gained()
    assert not app.audio.paused


def finish_prologue():
    app, screen = start()
    jump(app, screen, STORY.episodes['1.1.1'].end)
    if app.audio.voice is not None:                 # the Prologue's end has none
        end_voice(app)
    return app, screen


def test_the_end_says_episode_complete_then_opens_the_end_menu_on_back():
    app, screen = finish_prologue()
    episode = STORY.episodes['1.1.1']
    assert screen.complete and isinstance(app.stack.top, EndMenu)
    said = app.speech.said
    assert said[-2].startswith('Episode complete!') and episode.completion_text.strip() in said[-2]
    assert app.speech.heard[-1] == ('Back', False), 'the end menu cut off the completion text'
    assert [r.text for r in app.stack.top.rows()] == ['Back', 'Next episode, Art Show',
                                                      'Preview next episode', 'Credits']
    key(app, 'return')                              # Back
    assert isinstance(app.stack.top, MainMenu)
    assert app.audio.background is None and app.audio.voice is None


def test_next_episode_starts_it_with_the_story_so_far():
    app, screen = finish_prologue()
    screen.run.variables['Diplomacy'] = 2           # as the Prologue's choices left it
    key(app, 'down')
    key(app, 'return')                              # Next episode, Art Show
    playing = app.stack.top
    assert isinstance(playing, EpisodeScreen) and playing.episode.title == 'Art Show'
    assert playing.run.variables['Diplomacy'] == 2 and playing.heard is screen.heard
    assert app.stack.screens[0].__class__ is MainMenu and len(app.stack.screens) == 2


def test_the_end_credits_list_the_episodes_cast_back_first():
    app, screen = finish_prologue()
    key(app, 'end')
    key(app, 'return')                              # Credits
    credits = app.stack.top
    rows = [r.text for r in credits.rows()]
    assert rows[:3] == ['Back', 'Voice actors', 'Miss Honeybourne: Sarah Elmaleh']
    assert app.speech.said[-2:] == ['Credits. Prologue.', 'Back']
    key(app, 'escape')
    assert isinstance(app.stack.top, EndMenu)
    assert app.speech.said[-2:] == ['Episode complete.', 'Credits']     # back on the row left


def test_a_preview_plays_the_next_episodes_teaser_and_comes_back_when_it_ends():
    app, screen = finish_prologue()
    key(app, 'down')
    key(app, 'down')
    key(app, 'return')                              # Preview next episode
    preview = app.stack.top
    assert isinstance(preview, PreviewScreen) and app.speech.said[-1] == 'Preview of Art Show.'
    assert app.audio.voice == 'm1e2_teaser.m4a' and app.audio.background is None
    end_voice(app)
    assert isinstance(app.stack.top, EndMenu)


def open_preview():
    app, screen = finish_prologue()
    key(app, 'down')
    key(app, 'down')
    key(app, 'return')                              # Preview next episode
    return app, app.stack.top


def test_space_and_enter_do_nothing_in_a_preview():
    app, preview = open_preview()
    for name in ('space', 'return'):
        key(app, name)
        assert app.stack.top is preview and not app.audio.paused, name


def test_escape_pauses_a_preview_with_its_own_pause_menu():
    app, preview = open_preview()
    key(app, 'escape')
    menu = app.stack.top
    assert isinstance(menu, PreviewPauseMenu) and app.audio.paused
    assert [r.text for r in menu.rows()] == ['Resume', 'Restart', 'Return to menu']
    assert app.speech.said[-2:] == ['Paused.', 'Resume']
    key(app, 'return')                              # Resume
    assert app.stack.top is preview and not app.audio.paused
    assert app.audio.voice == 'm1e2_teaser.m4a'
    key(app, 'escape')
    key(app, 'escape')                              # Escape there resumes too
    assert app.stack.top is preview and not app.audio.paused


def test_restart_plays_the_preview_again_from_its_beginning():
    app, preview = open_preview()
    plays = len(app.audio.voices)
    key(app, 'escape')
    key(app, 'down')
    key(app, 'return')                              # Restart
    assert app.stack.top is preview and not app.audio.paused
    assert len(app.audio.voices) == plays + 1 and app.audio.voice == 'm1e2_teaser.m4a'
    assert app.speech.said[-1] == 'Restarting the preview of Art Show.'


def test_return_to_menu_stops_the_preview():
    app, preview = open_preview()
    key(app, 'escape')
    key(app, 'end')
    key(app, 'return')                              # Return to menu
    assert isinstance(app.stack.top, EndMenu)
    assert app.audio.voice is None and not app.audio.paused


def test_the_last_episodes_have_no_next_episode_or_preview():
    for episode_id in ('1.7.1', '1.8.1'):
        app, screen = start(episode_id)
        jump(app, screen, STORY.episodes[episode_id].end)
        until_choices(app, screen)
        assert [r.text for r in app.stack.top.rows()] == ['Back', 'Credits'], episode_id


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
    assert app.speech.said[-5:] == [words[1], words[2], words[1], words[-1], words[0]]
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
    assert app.speech.said[-2:] == [RESTART_WARNING, 'No']
    assert RESTART_WARNING.endswith('all saved progress beyond this episode will be erased.')
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
    assert isinstance(app.stack.top, MainMenu)


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


def test_c_enter_and_the_choice_keys_never_repeat():
    app, screen = start()
    before = len(app.speech.said)
    t = runloop.clock()
    app.key_down('c', [], now=t)
    app.repeat_keys(now=t + 2)
    assert app.speech.said[before:] == ['No choices yet.']
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
    assert app.speech.said[-1] == screen.offered[0].spoken


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


def type_text(app, text):
    for ch in text:
        if ch == '_':
            key(app, '-', ['shift'])
        elif ch.isupper():
            key(app, ch.lower(), ['shift'])
        else:
            key(app, ch)


def test_the_debug_keys_do_nothing_out_of_debug_mode():
    app, screen = start()
    before = len(app.speech.said)
    for name in ('f2', 'f3', 'f4'):
        key(app, name)
    assert app.stack.top is screen and len(app.speech.said) == before
    assert screen.run.current.name == '001introOpen'


def test_f2_skips_a_recording_never_heard_without_noting_it():
    heard = fresh_heard()
    app, screen = start(heard=heard, debug=True)
    key(app, 'f2')
    assert screen.offered and screen.run.current.name == '001introOpen'
    assert '001introOpen.m4a' not in heard
    assert app.audio.menu_sounds == ['PushButton D']
    key(app, 'f2')
    assert app.speech.said[-1] == 'Already at the choices.'


def test_f4_says_the_state_the_traits_and_the_flags():
    app, screen = start(debug=True)
    key(app, 'f4')
    said = app.speech.said[-1]
    assert said.startswith('State 001introOpen. Openness 0, Predictability 0, Diplomacy 0, Activeness 0.')
    assert 'npc_state.tomassi 1' in said


def test_f3_jumps_to_a_state_typed_in_part():
    app, screen = start(debug=True)
    key(app, 'f3')
    assert isinstance(app.stack.top, JumpScreen) and app.audio.paused
    type_text(app, '012introRejectPromptX')
    key(app, 'backspace')
    assert app.speech.said[-1] == 'X' and app.stack.top.query == '012introRejectPrompt'
    key(app, 'return')
    assert app.stack.top is screen and not app.audio.paused
    assert screen.run.current.name == '012introRejectPrompt'
    assert app.speech.said[-1] == 'Jumped to 012introRejectPrompt, in Prologue.'


def test_f3_types_underscores_with_shift_and_minus():
    app, screen = start(debug=True)
    key(app, 'f3')
    type_text(app, 'card_')
    assert app.stack.top.query == 'card_' and app.speech.said[-1] == '_'


class FakeClipboard:
    """Stands in for the Windows clipboard, so a test never touches the real one."""

    def __init__(self, text=''):
        self.text = text

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text
        return True


def open_jump(app, clipboard_text=''):
    key(app, 'f3')
    prompt = app.stack.top
    prompt.clipboard = FakeClipboard(clipboard_text)
    return prompt


def test_f3_pastes_a_name_with_ctrl_v_and_jumps_to_it():
    app, screen = start(debug=True)
    prompt = open_jump(app, 'State: 012introRejectPrompt\r\n')     # as copied from the script
    key(app, 'v', ['ctrl'])
    assert prompt.query == '012introRejectPrompt'
    assert app.speech.said[-1] == 'Pasted 012introRejectPrompt'
    key(app, 'return')
    assert screen.run.current.name == '012introRejectPrompt'


def test_f3_copies_with_ctrl_c_and_cuts_with_ctrl_x():
    app, screen = start(debug=True)
    prompt = open_jump(app)
    type_text(app, 'contact')
    key(app, 'c', ['ctrl'])
    assert prompt.clipboard.text == 'contact' and prompt.query == 'contact'
    assert app.speech.said[-1] == 'Copied contact'
    key(app, 'x', ['ctrl'])
    assert prompt.clipboard.text == 'contact' and prompt.query == ''
    assert app.speech.said[-1] == 'Cut contact'
    key(app, 'c', ['ctrl'])
    assert app.speech.said[-1] == 'Nothing typed yet.'
    key(app, 'v', ['ctrl'])
    assert prompt.query == 'contact'


def test_f3_says_when_the_clipboard_has_no_text():
    app, screen = start(debug=True)
    prompt = open_jump(app, '   ')
    key(app, 'v', ['ctrl'])
    assert prompt.query == '' and app.speech.said[-1] == 'The clipboard has no text.'


def test_f3_lists_several_matches_to_choose_from():
    app, screen = start(debug=True)
    key(app, 'f3')
    type_text(app, 'contactMark')
    key(app, 'return')
    menu = app.stack.top
    assert isinstance(menu, MatchMenu) and len(menu.names) > 1
    assert app.speech.said[-2:] == ['%d states match.' % len(menu.names), 'Back']
    key(app, 'down')
    key(app, 'return')                              # the first, 015contactMark, in Art Show
    assert isinstance(app.stack.top, EpisodeScreen)
    assert app.stack.top.run.current.name == menu.names[0]


def test_f3_says_when_nothing_or_too_much_matches():
    app, screen = start(debug=True)
    key(app, 'f3')
    type_text(app, 'nosuchstate')
    key(app, 'return')
    assert app.speech.said[-1] == 'No state has nosuchstate in its name.'
    for _ in range(len('nosuchstate')):
        key(app, 'backspace')
    type_text(app, 'm1e')
    key(app, 'return')
    assert app.speech.said[-1].endswith('states match. Type more of the name.')
    key(app, 'escape')
    assert app.stack.top is screen and not app.audio.paused
    assert app.speech.said[-1] == 'Canceled.'


def test_f3_to_a_state_in_another_episode_plays_that_episode():
    app, screen = start(debug=True)
    key(app, 'f3')
    type_text(app, '009drinkPrompt_m1e8')
    key(app, 'return')
    there = app.stack.top
    assert isinstance(there, EpisodeScreen) and there is not screen
    assert there.episode.title == 'Holiday Party' and there.run.current.name == '009drinkPrompt_m1e8'
    key(app, 'escape')
    key(app, 'end')
    key(app, 'return')                              # Return to menu
    assert isinstance(app.stack.top, MainMenu)


def test_a_jump_away_from_the_end_goes_on_playing():
    app, screen = start(debug=True)
    episode = STORY.episodes['1.1.1']
    screen.play(screen.run.enter(episode.end))      # before its next frame ends it
    assert screen.run.finished
    screen.jump('012introRejectPrompt')
    app.audio.update()
    assert not screen.run.finished
    end_voice(app)
    assert screen.offered and not screen.complete


def test_state_on_the_command_line_starts_there_in_debug_mode_only():
    e = entry()
    app = make_app(debug=True)
    app.options.state = '016F_contactMark'
    screen = e.episode_from_options(app, app.options)
    assert screen.episode.title == 'Art Show' and screen.at == '016F_contactMark'
    plain = make_app()
    plain.options.state = '016F_contactMark'
    assert e.episode_from_options(plain, plain.options) is None


def test_the_16_achievements_are_every_one_the_story_earns():
    ids = {short_id(a) for s in STORY.states.values() for a in s.achievements}
    assert len(ACHIEVEMENTS) == 16 and ids == {a[0] for a in ACHIEVEMENTS}
    assert sum(len(s.achievements) for s in STORY.states.values()) == 23


def test_an_achievement_is_said_at_the_next_choice_before_it():
    kept = fresh_achievements()
    app, screen = start(achievements=kept)
    jump(app, screen, 'achievement_cardsWin')
    assert 'event.m1e1_cardsWin' in kept
    assert 'Achievement earned: Card Shark.' not in app.speech.said, 'said over the story'
    until_choices(app, screen)
    assert app.speech.heard[-2:] == [('Achievement earned: Card Shark.', False),
                                     (screen.offered[0].spoken, False)]
    assert 'event.m1e1_cardsWin' in Achievements(kept.file.path), 'not kept in the file'


def test_an_achievement_is_said_only_the_first_time_ever():
    kept = fresh_achievements()
    for time in (1, 2):
        app, screen = start(achievements=kept)
        jump(app, screen, 'achievement_cardsWin')
        until_choices(app, screen)
        said = app.speech.said.count('Achievement earned: Card Shark.')
        assert said == (1 if time == 1 else 0), (time, said)


def test_an_achievement_at_the_end_is_said_after_episode_complete():
    app, screen = start('1.7.1')
    jump(app, screen, 'achievement_completeSignumCygni')
    until_choices(app, screen)
    assert screen.complete
    said = app.speech.said
    assert said[-3].startswith('Episode complete!')
    assert said[-2:] == ['Achievement earned: Mission Complete.', 'Back']


def test_an_achievement_passed_with_s_still_counts():
    heard = fresh_heard()
    kept = fresh_achievements()
    app, screen = start(heard=heard, achievements=kept)
    jump(app, screen, '002introOpenPrompt')
    heard.add(STORY.state('002introOpenPrompt').voice)
    raise_bet = next(c for c in STORY.choices('002introOpenPrompt') if c.text == 'IMPULSIVE')
    screen.play(screen.run.enter(raise_bet.destination))
    app.audio.update()
    for _ in range(50):                             # hear everything on the way, but by S
        state = screen.run.current
        if screen.offered or screen.complete:
            break
        if state.voice:
            heard.add(state.voice)
        key(app, 's')
    assert 'event.m1e1_cardsWin' in kept
    assert 'Achievement earned: Card Shark.' in app.speech.said


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
    app.run(MainMenu(app), pygame, on_top=screen)
    assert 'Main menu.' not in app.speech.said
    assert app.audio.voices[0] == STORY.state('001introOpen').voice


if __name__ == '__main__':
    _quiet.run_tests(globals())
