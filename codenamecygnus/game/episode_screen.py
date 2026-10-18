"""Playing an episode: sections 2 and 3 of aidocks/plans/story_engine_plan.md.

The screen walks a ``Playthrough`` (game/story.py) state by state through the audio
(aidocks/plans/audio_plan.md):

1. **A state starts:** the decision loop stops, the background carries on or cuts over,
   and the voice plays. A state with no voice ends at once, on the next frame.
2. **Its voice ends:** if the state waits for a choice, the decision loop starts and the
   first choice is the one you are on, said by its word alone; a timed one starts its
   clock. Otherwise the story goes on by itself to the next state.
3. **The episode's end state's voice ends:** "Episode complete!" and the completion text,
   then Enter or Escape goes back to the menu.

    Up and Down     move through the choices from the first, wrapping round
    Left and Right  the same, while a choice waits
    Home and End    the first choice and the last
    Enter           choose the one you are on, the first until you move
    1 to 9          choose by number
    C               say every choice, such as "Charismatic or Hostile."
    Space           pause and resume
    R               the recording again from its start, then the choices again
    Left and Right  5 seconds back or forward, while the story plays
    S               straight on to the next choice, across recordings heard before
    H               the scene heading
    the volumes     Shift+Home and Shift+End, Page Up and Page Down, Shift+Page Up and Down
    Escape          the pause menu: Resume, Restart episode, Settings, Return to menu

Every key but Escape, Home, End and the numbers comes from the key map, so F1 can rebind
it. While a choice waits, its recording has ended and there is nothing to skip through,
so Left and Right move through the choices as they do in a menu (the dev, 2026-10-17:
"left/right/home/end navigation in the choices list"). Holding a skip or a volume key
repeats it (app.py); a choice key never repeats.

A recording reaching its end, played through or skipped to the end with Right, is noted
as heard for good (game/heard.py), and S skips only across those, saying "Not heard yet"
on a recording that is new, so a stray press never skips story the player has not heard.

The story pauses by itself while another screen covers it (the pause menu, F1) and while
the window has lost the keyboard, and carries on when it comes back, unless the player
had paused it with Space. A timed choice keeps the seconds it had left.
"""
from __future__ import annotations

import logging

from ..platform.audio import SKIP_SECONDS
from ..ui.menu import Menu, Row
from ..ui.screens import Screen
from ..ui.settings_screen import SettingsScreen
from .heard import Heard
from .recordings import Recordings
from .story import TICKS, Playthrough, Story

log = logging.getLogger('episode')

#: Volume actions: (the setting, which way).
VOLUME_KEYS = {
    'master_up': ('master_volume', 1), 'master_down': ('master_volume', -1),
    'ambience_up': ('ambience_volume', 1), 'ambience_down': ('ambience_volume', -1),
    'decision_up': ('decision_volume', 1), 'decision_down': ('decision_volume', -1),
}

#: Why the story is paused: the player pressed Space or Escape, or it paused by itself.
BY_PLAYER, BY_COVER, BY_FOCUS = 'player', 'cover', 'focus'


def heading_text(heading):
    """A scene heading as it is spoken: "CONSULATE - BOMB ROOM" as "Consulate, bomb room"."""
    parts = [p.strip().lower() for p in heading.split(' - ') if p.strip()]
    text = ', '.join(parts)
    return text[:1].upper() + text[1:]


def choices_text(choices):
    """The choices read together: "Charismatic or Hostile", "Bold, Clever or Athletic"."""
    words = [c.spoken for c in choices]
    if len(words) < 2:
        return ''.join(words) + '.'
    return '%s or %s.' % (', '.join(words[:-1]), words[-1])


def script_line(line):
    """One script line for the window, without its pacing marks."""
    text = ' '.join(TICKS.sub(' ', line.get('text', '')).split())
    if line.get('type') == 'SPEECH' and line.get('character'):
        return '%s: %s' % (line['character'].title(), text)
    return text


class EpisodeScreen(Screen):
    name = 'episode'
    holds_time = True

    def __init__(self, app, episode, story=None, recordings=None, variables=None, heard=None):
        super().__init__(app)
        self.story = story or Story.shared()
        self.recordings = recordings or Recordings.shared()
        self.heard = heard if heard is not None else Heard.shared()
        self.voice_playing = None   # the story name of the voice playing, once found on disk
        self.episode = episode
        self.start_variables = dict(variables or {})
        self.run = Playthrough(self.story, episode, variables)
        self.started = False
        self.offered = []           # the choices waiting, once the question has been asked
        self.index = None           # the choice you are on: the first, once they are offered
        self.heading = None         # the last scene heading reached
        self.complete = False       # the end state's voice has finished
        self.paused = None          # None, or why: BY_PLAYER, BY_COVER or BY_FOCUS
        self.timer = None           # the timed choice's call
        self.timer_left = None      # its seconds left, while paused

    @property
    def audio(self):
        return self.app.audio

    @property
    def loop(self):
        return self.app.loop

    # ---- the screen's life ---------------------------------------------
    def opened(self):
        if not self.started:
            self.started = True
            log.info('episode %s, %s, starts', self.episode.id, self.episode.title)
            self.play(self.run.start())
        elif self.paused in (BY_COVER, BY_FOCUS):
            self.resume()

    def covered(self):
        self.pause(BY_COVER)

    def closed(self):
        self.cancel_timer()
        self.audio.stop_all()

    def focus_lost(self):
        self.pause(BY_FOCUS)

    def focus_gained(self):
        if self.paused == BY_FOCUS:
            self.resume()

    # ---- playing --------------------------------------------------------
    def find(self, file_name):
        return self.recordings.find(file_name) if file_name else None

    def play(self, state):
        """Play a state just entered."""
        log.debug('state %s', state.name)
        self.offered = []
        self.index = None
        self.cancel_timer()
        if state.heading:
            self.heading = state.heading
        self.audio.stop_decision()
        self.audio.set_background(self.find(state.background))
        self.start_voice(state)

    def start_voice(self, state):
        """Play a state's voice from its start. No voice, or one not on disk, ends on the
        next frame, so the story never waits on silence and a run of empty states never
        piles up in one call."""
        recording = self.find(state.voice)
        self.voice_playing = state.voice if recording is not None else None
        self.audio.play_voice(recording, on_end=self.voice_ended)

    def voice_ended(self):
        if self.voice_playing:
            # Reached its end, played through or skipped there with Right: heard.
            if self.heard.add(self.voice_playing):
                log.debug('heard %s', self.voice_playing)
            self.voice_playing = None
        if self.run.finished:
            self.finish()
        elif self.run.waiting:
            self.offer()
        else:
            state = self.run.after_voice()
            if state is None:
                log.error('%s leads nowhere, so the episode stops', self.run.current.name)
                self.finish()
            else:
                self.play(state)

    def offer(self):
        """The question has been asked: the decision loop, the choices and any clock."""
        state = self.run.current
        self.offered = self.run.choices()
        # The first choice is the one you are on, so Enter at once chooses it (the dev,
        # 2026-10-17: "pressing enter should activate the first focused option").
        self.index = 0
        self.audio.start_decision(self.find(state.decision))
        # The one you are on is said, as a menu says its row (the dev, 2026-10-17: "When
        # there are more than 1 choice on screen, it should auto focus to it and speak the
        # first one"); C says them all. Said by the game itself, so it waits behind
        # whatever the player made it say.
        self.say(self.offered[0].spoken, interrupt=False)
        timeout = self.run.timeout()
        if timeout is not None:
            self.start_timer(timeout[0])

    def choose(self, choice):
        if self.paused:
            self.resume()
        log.info('chose %s at %s', choice.text, self.run.current.name)
        self.say(choice.spoken)
        self.play(self.run.choose(choice))

    def timed_out(self):
        self.timer = None
        log.info('the choice at %s timed out', self.run.current.name)
        state = self.run.time_out()
        if state is not None:
            self.play(state)

    def finish(self):
        self.complete = True
        self.offered = []
        self.cancel_timer()
        self.audio.stop_decision()
        log.info('episode %s complete', self.episode.id)
        text = 'Episode complete! ' + self.episode.completion_text.strip()
        self.say(text.strip(), interrupt=False)
        self.say('Press Enter to return to the menu.', interrupt=False)

    def leave(self):
        """Back to the menu below."""
        self.stack.pop()

    def restart(self):
        """The episode again from its start, with the variables it began with."""
        log.info('episode %s restarts', self.episode.id)
        self.stack.replace(EpisodeScreen(self.app, self.episode, story=self.story,
                                         recordings=self.recordings,
                                         variables=self.start_variables, heard=self.heard))
        # Cuts off the pause menu, which spoke as it came back on its way out.
        self.say('Restarting %s.' % self.episode.title)

    # ---- the timed choice's clock ---------------------------------------
    def start_timer(self, seconds):
        self.cancel_timer()
        if self.paused:
            self.timer_left = seconds
        else:
            self.timer = self.loop.after(seconds, self.timed_out)

    def cancel_timer(self):
        if self.timer is not None:
            self.timer.cancel()
        self.timer = None
        self.timer_left = None

    # ---- pausing --------------------------------------------------------
    def pause(self, why):
        if self.paused:
            return False
        self.paused = why
        self.audio.pause()
        if self.timer is not None:
            self.timer_left = self.loop.remaining(self.timer)
            self.timer.cancel()
            self.timer = None
        return True

    def resume(self):
        if not self.paused:
            return False
        self.paused = None
        self.audio.resume()
        if self.timer_left is not None:
            self.timer = self.loop.after(self.timer_left, self.timed_out)
            self.timer_left = None
        return True

    def open_pause_menu(self):
        self.pause(BY_PLAYER)
        self.stack.push(PauseMenu(self.app, self))

    # ---- keys -----------------------------------------------------------
    def handle_key(self, key, mods):
        if self.complete:
            if key in ('return', 'enter', 'escape') and not mods:
                self.leave()
            else:
                self.say('Episode complete. Press Enter to return to the menu.')
            return True
        if key == 'escape' and not mods:
            self.open_pause_menu()
            return True
        if not mods and len(key) == 1 and key in '123456789':
            self.choose_number(int(key))
            return True
        if not mods and key in ('home', 'end') and self.offered:
            self.index = 0 if key == 'home' else len(self.offered) - 1
            self.say(self.offered[self.index].spoken)
            return True
        action = self.app.keymap.action_for(key, mods)
        if action is None:
            return False
        handler = getattr(self, 'do_' + action, None)
        if handler is not None:
            handler()
        elif action in VOLUME_KEYS:
            setting, step = VOLUME_KEYS[action]
            self.say(self.audio.step_volume(setting, step))
        return True

    def repeats(self, key, mods):
        """Holding a key repeats it for the skips, while the story plays, and the volumes."""
        if self.complete:
            return False
        action = self.app.keymap.action_for(key, mods)
        if action in VOLUME_KEYS:
            return True
        return action in ('back', 'forward') and not self.offered

    def no_choices_yet(self):
        self.say('No choices yet.')

    def move(self, step):
        if not self.offered:
            return self.no_choices_yet()
        if self.index is None:
            self.index = 0 if step > 0 else len(self.offered) - 1
        else:
            self.index = (self.index + step) % len(self.offered)
        self.say(self.offered[self.index].spoken)

    def do_previous_choice(self):
        self.move(-1)

    def do_next_choice(self):
        self.move(1)

    def do_choose(self):
        if not self.offered:
            return self.no_choices_yet()
        self.choose(self.offered[self.index or 0])

    def choose_number(self, n):
        if not self.offered:
            return self.no_choices_yet()
        if n > len(self.offered):
            return self.say('There %s only %d.' % ('is' if len(self.offered) == 1 else 'are',
                                                  len(self.offered)))
        self.choose(self.offered[n - 1])

    def do_repeat_choices(self):
        if not self.offered:
            return self.no_choices_yet()
        self.say(choices_text(self.offered))

    def do_pause(self):
        if self.paused:
            self.resume()
            self.say('Resumed.')
        else:
            self.pause(BY_PLAYER)
            self.say('Paused.')

    def do_replay(self):
        state = self.run.current
        if self.offered:
            # The question again: the choices are offered once more after it, and a timed
            # choice's clock waits until then.
            self.offered = []
            self.index = None
            self.cancel_timer()
            self.audio.stop_decision()
            self.start_voice(state)
        else:
            self.audio.replay()

    def is_heard(self, state):
        """Whether S may skip this state's voice: heard to its end before, or none at all."""
        return not state.voice or state.voice in self.heard

    def do_skip(self):
        """S: straight on to the next choice, across every recording heard before.

        Each state passed is entered as play would enter it, setting its variables and
        taking its conditions, so skipping never changes how the story turns out. A
        recording not heard yet stops the skip, and plays from its start."""
        if self.offered:
            return self.say('Already at the choices.')
        if not self.is_heard(self.run.current):
            return self.say('Not heard yet.')
        if self.paused:
            self.resume()
        self.audio.play_menu(self.recordings.menu_sound('PushButton D'))
        start = self.run.current.name
        # A guard only: no run of automatic states in the story comes near it.
        for _ in range(10000):
            if self.run.finished or self.run.waiting:
                break
            state = self.run.after_voice()
            if state is None:
                break
            if state.heading:
                self.heading = state.heading
            if not self.is_heard(state):
                log.info('skipped from %s to %s, not heard yet', start, state.name)
                self.play(state)
                return
        log.info('skipped from %s to %s', start, self.run.current.name)
        # At a choice or the end, its voice heard: as if that voice had just finished.
        state = self.run.current
        self.cancel_timer()
        self.audio.stop_decision()
        self.audio.set_background(self.find(state.background))
        self.audio.stop_voice()
        self.voice_playing = None
        self.voice_ended()

    def do_back(self):
        if self.offered:
            self.move(-1)
        else:
            self.audio.seek(-SKIP_SECONDS)

    def do_forward(self):
        if self.offered:
            self.move(1)
        else:
            self.audio.seek(SKIP_SECONDS)

    def do_heading(self):
        self.say(heading_text(self.heading) if self.heading else 'No scene heading yet.')

    def do_speech_recognition(self):
        self.say('Speech recognition is not ready yet.')

    # ---- the window -----------------------------------------------------
    def lines(self):
        out = ['Episode %d: %s' % (self.episode.number, self.episode.title)]
        if self.heading:
            out.append(self.heading)
        if self.paused == BY_PLAYER:
            out.append('(paused)')
        out.append('')
        if self.run.current is not None:
            out += [script_line(line) for line in self.run.current.script
                    if line.get('type') != 'HEADING']
        if self.offered:
            out.append('')
            for i, c in enumerate(self.offered):
                out.append('%s %d. %s' % ('>' if i == self.index else ' ', i + 1, c.spoken))
        if self.complete:
            out += ['', 'Episode complete!', self.episode.completion_text.strip()]
        return out


class PauseMenu(Menu):
    """Escape during an episode: the story waits underneath, paused."""

    name = 'pause menu'
    title = 'Paused.'

    def __init__(self, app, episode_screen):
        super().__init__(app)
        self.episode_screen = episode_screen

    def rows(self):
        return [Row('Resume', self.back),
                Row('Restart episode', lambda: self.stack.push(RestartQuestion(self.app, self))),
                Row('Settings', lambda: self.stack.push(SettingsScreen(self.app))),
                Row('Return to menu', self.return_to_menu)]

    def back(self):
        """Resume, or Escape: the story carries on where it paused."""
        self.stack.pop()
        self.episode_screen.resume()

    def restart(self):
        self.stack.pop()
        self.episode_screen.restart()

    def return_to_menu(self):
        self.stack.pop()
        self.episode_screen.leave()


class RestartQuestion(Menu):
    """Restart episode, from the pause menu: asked first, No first, so a stray Enter keeps
    the place. Escape is No. aidocks/plans/saves_plan.md adds the original's warning about
    saved progress once there is any."""

    name = 'restart question'
    title = 'Restart episode?'

    def __init__(self, app, pause_menu):
        super().__init__(app)
        self.pause_menu = pause_menu

    def rows(self):
        return [Row('No', self.back), Row('Yes', self.restart)]

    def restart(self):
        self.stack.pop()
        self.pause_menu.restart()
