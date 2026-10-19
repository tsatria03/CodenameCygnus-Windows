"""Playing an episode: sections 2 to 5 of aidocks/plans/story_engine_plan.md.

The screen walks a ``Playthrough`` (game/story.py) state by state through the audio
(aidocks/plans/audio_plan.md):

1. **A state starts:** the decision loop stops, the background carries on or cuts over,
   and the voice plays. A state with no voice ends at once, on the next frame.
2. **Its voice ends:** if the state waits for a choice, the decision loop starts and the
   first choice is the one you are on, said by its word alone; a timed one starts its
   clock. Otherwise the story goes on by itself to the next state.
3. **The episode's end state's voice ends:** "Episode complete!" and any achievements,
   then the end menu (game/episode_end.py), with the completion text as its own row.

    Up and Down     move through the choices from the first, wrapping round
    Left and Right  the same, while a choice waits
    Home and End    the first choice and the last
    Enter           choose the one you are on, the first until you move
    1 to 9          choose by number
    C               say every choice, such as "Charismatic or Hostile."
    R               the recording again from its start, then the choices again
    Left and Right  5 seconds back or forward, while the story plays
    S               straight on to the next choice, across recordings heard before
    H               the scene heading
    V               speech recognition on or off
    the volumes    Shift+Home and Shift+End, Page Up and Page Down, Shift+Page Up and Down
    Escape or P     pause, with the pause menu: Resume, Restart episode, Settings,
                    Return to menu; Resume or Escape there carries on

Every key but Escape, Home, End and the numbers comes from the key map, so F1 can rebind
it. While a choice waits, its recording has ended and there is nothing to skip through,
so Left and Right move through the choices as they do in a menu (the dev, 2026-10-17:
"left/right/home/end navigation in the choices list"). Holding a skip or a volume key
repeats it (app.py); a choice key never repeats.

A recording reaching its end, played through or skipped to the end with Right, is noted
as heard for good (game/heard.py), and S skips only across those, saying "Not heard yet"
on a recording that is new, so a stray press never skips story the player has not heard.

An achievement a state earns (game/achievements.py) is kept at once, and said at the next
quiet moment, "Achievement earned: Card Shark.", before the choice that comes next or after
"Episode complete!", never over the story; only the first time it is ever earned.

The story pauses by itself while another screen covers it (the pause menu, F1) and while
the window has lost the keyboard, and carries on when it comes back. A timed choice keeps
the seconds it had left. There is no pause key of its own: Escape pauses, through the
pause menu (the dev, 2026-10-18: "Can you remove space to pause? I feel like escape
already does the job").

With speech recognition on (aidocks/plans/speech_recognition_plan.md), a choice can be
spoken too: after the first choice is said, "Listening.", and the microphone listens for
the choices' words, hidden ones too, for 15 seconds, or for the rest of a timed choice's
clock; then "No longer listening.", and the keys still choose. Words that are no choice
get "Sorry, I did not catch that", and listening goes on. C listens again. Pausing stops
listening and keeps the seconds left, for when the story resumes. While it listens, Enter
and the number keys say "Speak your choice." and choose nothing; the arrows still read the
choices.
"""
from __future__ import annotations

import logging

from ..platform.audio import SKIP_SECONDS
from ..platform.listener import BLOCKED, MicrophoneError
from ..ui.menu import Menu, Row
from ..ui.screens import Screen
from ..ui.settings_screen import SettingsScreen
from .achievements import Achievements, name_of
from .debug import JumpScreen, state_report
from .heard import Heard
from .progress import Progress
from .recordings import Recordings
from .story import TICKS, Playthrough, Story

log = logging.getLogger('episode')

#: Volume actions: (the setting, which way).
VOLUME_KEYS = {
    'master_up': ('master_volume', 1), 'master_down': ('master_volume', -1),
    'ambience_up': ('ambience_volume', 1), 'ambience_down': ('ambience_volume', -1),
    'decision_up': ('decision_volume', 1), 'decision_down': ('decision_volume', -1),
}

#: Why the story is paused: the player pressed Escape, or it paused by itself.
BY_PLAYER, BY_COVER, BY_FOCUS = 'player', 'cover', 'focus'

#: Seconds speech recognition listens at a choice that has no clock of its own.
LISTEN_SECONDS = 15
#: The original's own words for listening and not catching a word.
LISTENING, NOT_LISTENING = 'Listening.', 'No longer listening.'
NOT_CAUGHT = 'Sorry, I did not catch that'
#: Enter or a number key while it listens: the choice is to be spoken.
SPEAK_INSTEAD = 'Speak your choice.'
NO_MICROPHONE_TEXT = 'No microphone found. Choose with the keys.'
BLOCKED_TEXT = 'The microphone is blocked in Windows privacy settings.'


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

    def __init__(self, app, episode, story=None, recordings=None, variables=None, heard=None,
                 at=None, achievements=None, progress=None):
        super().__init__(app)
        # The state to start at, for Continue or a debug jump, or None for a fresh start.
        self.at = at
        self.achievements = achievements if achievements is not None else Achievements.shared()
        self.earned_seen = 0        # how many of the run's earned ids have been looked at
        self.to_announce = []       # names of achievements earned, waiting for a quiet moment
        self.story = story or Story.shared()
        self.progress = progress if progress is not None else Progress.shared(self.story)
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
        self.listening = False      # the microphone listens for the choices' words
        self.listen_timer = None    # the call ending 15 seconds of listening
        self.listen_left = None     # its seconds left, while paused
        self.was_listening = False  # listening when the story paused
        self.listen_done = False    # listening ended at this choice: C or V listens again

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
            log.info('episode %s, %s, starts%s', self.episode.id, self.episode.title,
                     ' at %s' % self.at if self.at else '')
            if self.at is None:
                self.progress.begin(self.episode, self.start_variables)
            self.play(self.run.start(self.at))
        elif self.paused in (BY_COVER, BY_FOCUS):
            self.resume()

    def covered(self):
        # Once the episode is complete, the end menu covers it, and its background plays on.
        if not self.complete:
            self.pause(BY_COVER)

    def closed(self):
        self.cancel_timer()
        self.stop_listening()
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
        self.stop_listening()
        self.listen_done = False
        if state.heading:
            self.heading = state.heading
        self.collect()
        self.save_place()
        self.audio.stop_decision()
        self.audio.set_background(self.find(state.background))
        self.start_voice(state)

    def save_place(self):
        """Continue comes back to the start of this state (aidocks/plans/saves_plan.md)."""
        if not self.run.finished:
            self.progress.save_place(self.episode, self.run.current.name, self.run.entered_with)

    # ---- achievements (game/achievements.py) -----------------------------
    def collect(self):
        """Note the achievements the states entered so far have earned, by play, S, F2 or a
        jump alike; one earned for the first time ever waits to be announced."""
        for a in self.run.earned[self.earned_seen:]:
            if self.achievements.add(a):
                self.to_announce.append(name_of(a))
        self.earned_seen = len(self.run.earned)

    def announce(self):
        """At a quiet moment, a choice or the end, never over the story: each achievement
        earned since the last one, waiting behind whatever was being said."""
        self.collect()
        for name in self.to_announce:
            self.say('Achievement earned: %s.' % name, interrupt=False)
        self.to_announce = []

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
        # whatever the player made it say. An achievement earned on the way comes first.
        self.announce()
        self.say(self.offered[0].spoken, interrupt=False)
        timeout = self.run.timeout()
        if timeout is not None:
            self.start_timer(timeout[0])
        self.listen_done = False
        self.start_listening()

    def choose(self, choice, heard=False):
        """Make a choice, with the skip sound, PushButton D (the dev, 2026-10-18: "Use that
        same sound for choices as well"). A key chooses in silence, since the choice was
        just said as it was moved to ("I also do not want it to speak if you press enter on
        a choice"); a spoken one is said back, so the player knows which word was heard."""
        if self.paused:
            self.listen_done = True         # no listening on the way out of the choice
            self.resume()
        log.info('chose %s at %s', choice.text, self.run.current.name)
        self.audio.play_menu(self.recordings.menu_sound('PushButton D'))
        if heard:
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
        self.stop_listening()
        self.audio.stop_decision()
        log.info('episode %s complete', self.episode.id)
        self.progress.complete(self.episode, self.run.variables)
        # "Episode complete!" alone; the completion text is the end menu's row after Back
        # (the dev, 2026-10-18: "I should only here, episode complete, not the description
        # added to it").
        self.say('Episode complete!', interrupt=False)
        self.announce()
        from .episode_end import EndMenu       # it starts episodes, so it imports this module
        self.stack.push(EndMenu(self.app, self))

    def leave(self):
        """Back to the menu below."""
        self.stack.pop()

    def start_next(self, episode):
        """The end menu's Next episode: that episode in this one's place, the story so far
        carried on, as aidocks/plans/saves_plan.md has an episode start with the variables
        the one before it ended with."""
        log.info('episode %s goes on to %s', self.episode.id, episode.id)
        self.stack.replace(EpisodeScreen(self.app, episode, story=self.story,
                                         recordings=self.recordings,
                                         variables=self.run.variables, heard=self.heard,
                                         achievements=self.achievements,
                                         progress=self.progress))

    def restart(self):
        """The episode again from its start, with the variables it began with; every later
        episode goes back to locked (game/progress.py)."""
        log.info('episode %s restarts', self.episode.id)
        began = self.progress.restart(self.episode)
        self.stack.replace(EpisodeScreen(self.app, self.episode, story=self.story,
                                         recordings=self.recordings,
                                         variables=began, heard=self.heard,
                                         achievements=self.achievements,
                                         progress=self.progress))
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

    # ---- speech recognition (platform/listener.py) ----------------------
    def speech_on(self):
        return bool(self.app.settings.get('speech_recognition'))

    def start_listening(self, seconds=None, announce=True):
        """Listen for the waiting choice's words, saying "Listening." first: for
        ``seconds``, 15 by default, or while a timed choice's clock runs."""
        self.stop_listening()
        if not (self.offered and self.speech_on()) or self.paused:
            return
        phrases = [c.text for c in self.run.all_choices()]
        try:
            if not self.app.listener.start(phrases, others=self.story.choice_texts()):
                return
        except MicrophoneError as error:
            log.warning('cannot listen: %s', error)
            self.listen_done = True
            if not self.app.microphone_warned:
                self.app.microphone_warned = True
                self.say(BLOCKED_TEXT if error.kind == BLOCKED else NO_MICROPHONE_TEXT,
                         interrupt=False)
            return
        except Exception:
            log.exception('speech recognition failed to start')
            self.listen_done = True
            return
        self.listening = True
        if announce:
            self.say(LISTENING, interrupt=False)
        # A timed choice listens until its clock ends the choice.
        if self.timer is None:
            self.listen_timer = self.loop.after(seconds or LISTEN_SECONDS, self.listen_ended)
        log.info('listening at %s', self.run.current.name)

    def stop_listening(self):
        if self.listen_timer is not None:
            self.listen_timer.cancel()
        self.listen_timer = None
        self.listen_left = None
        if self.listening:
            self.listening = False
            self.app.listener.stop()

    def listen_ended(self):
        """15 seconds with no choice heard; the keys still choose."""
        self.listen_timer = None
        self.stop_listening()
        self.listen_done = True
        self.say(NOT_LISTENING)

    def update(self):
        """Once a frame: anything said while listening."""
        if not self.listening:
            return
        for phrase, words in self.app.listener.poll():
            choice = next((c for c in self.run.all_choices() if c.text == phrase), None)
            if choice is not None:
                log.info('heard %r', words)
                return self.choose(choice, heard=True)
            log.info('heard %r, no choice', words)
            self.say(NOT_CAUGHT)

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
        self.was_listening = self.listening
        if self.listening:
            left = self.loop.remaining(self.listen_timer) if self.listen_timer else None
            self.stop_listening()
            self.listen_left = left
        return True

    def resume(self):
        if not self.paused:
            return False
        self.paused = None
        self.audio.resume()
        if self.timer_left is not None:
            self.timer = self.loop.after(self.timer_left, self.timed_out)
            self.timer_left = None
        # Listening goes on where it stopped, or starts if it was turned on meanwhile.
        if self.offered and self.speech_on() and not self.listen_done:
            self.start_listening(self.listen_left, announce=not self.was_listening)
        self.was_listening = False
        self.listen_left = None
        return True

    def open_pause_menu(self):
        self.pause(BY_PLAYER)
        self.app.play_sound('open')
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

    def speak_instead(self):
        """While it listens, a choice can only be spoken (aidocks/plans/speech_recognition_plan.md;
        the dev, 2026-10-18: "When it's listening, you should not be allowed to tap your
        choices or pick from them"). True when the key was refused."""
        if self.listening:
            self.say(SPEAK_INSTEAD)
            return True
        return False

    def do_choose(self):
        if not self.offered:
            return self.no_choices_yet()
        if self.speak_instead():
            return
        self.choose(self.offered[self.index or 0])

    def choose_number(self, n):
        if not self.offered:
            return self.no_choices_yet()
        if self.speak_instead():
            return
        if n > len(self.offered):
            return self.say('There %s only %d.' % ('is' if len(self.offered) == 1 else 'are',
                                                  len(self.offered)))
        self.choose(self.offered[n - 1])

    def do_repeat_choices(self):
        if not self.offered:
            return self.no_choices_yet()
        self.say(choices_text(self.offered))
        # And listens again, for another 15 seconds.
        if self.speech_on():
            self.listen_done = False
            self.start_listening()

    def do_pause_menu(self):
        """P, as Escape: pause, with the pause menu."""
        self.open_pause_menu()

    def do_replay(self):
        state = self.run.current
        if self.offered:
            # The question again: the choices are offered once more after it, and a timed
            # choice's clock waits until then.
            self.offered = []
            self.index = None
            self.cancel_timer()
            self.stop_listening()
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
        self.collect()
        self.save_place()
        self.cancel_timer()
        self.audio.stop_decision()
        self.audio.set_background(self.find(state.background))
        self.audio.stop_voice()
        self.voice_playing = None
        self.voice_ended()

    # ---- debug mode (game/debug.py) --------------------------------------
    def do_debug_skip(self):
        """F2: on past this recording, heard or not, and never noted as heard, so testing
        a branch does not mark story the dev never listened to."""
        if self.offered:
            return self.say('Already at the choices.')
        if self.paused:
            self.resume()
        log.info('debug: skipped %s', self.run.current.name)
        # The skip sound, as S plays (the dev, 2026-10-18: "f2 should play the skip sound").
        self.audio.play_menu(self.recordings.menu_sound('PushButton D'))
        self.voice_playing = None
        self.audio.stop_voice()
        self.voice_ended()

    def do_debug_jump(self):
        self.stack.push(JumpScreen(self.app, self))

    def do_debug_state(self):
        self.say(state_report(self.run))

    def jump(self, name):
        """Debug mode: play from any state. One in another episode starts that episode
        there, so its end is the right one; the variables carry over either way."""
        episode = self.story.episode_of(name) or self.episode
        log.info('debug: jumped to %s, in %s', name, episode.title)
        if episode is self.episode:
            self.play(self.run.enter(name))
        else:
            self.stack.replace(EpisodeScreen(self.app, episode, story=self.story,
                                             recordings=self.recordings,
                                             variables=self.run.variables,
                                             heard=self.heard, at=name,
                                             achievements=self.achievements,
                                             progress=self.progress))
        # Cuts off the screens that spoke as they closed on the way back here.
        self.say('Jumped to %s, in %s.' % (name, episode.title))

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
        """V: speech recognition on or off, for good; turned on at a waiting choice, it
        starts listening at once. While it listens, V does nothing but say so, as the
        original's voice button was disabled while it listened (-[CCGameViewController
        voiceRecognitionChangedStateToActive:], 0x100042174, setting setVoiceEnabled: to
        the opposite of listening; the dev, 2026-10-18: "The V key should not disable
        listening ... Match it to the original")."""
        if self.listening:
            return self.say(LISTENING)
        on = self.app.settings.toggle('speech_recognition')
        self.say('Speech recognition %s.' % ('on' if on else 'off'))
        if on and self.offered:
            self.listen_done = False
            self.start_listening()
        elif not on:
            self.stop_listening()

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
            if self.listening:
                out.append('(listening)')
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
                Row('Restart episode', lambda: self.open(RestartQuestion(self.app, self.restart))),
                Row('Settings', lambda: self.open(SettingsScreen(self.app))),
                Row('Return to menu', self.return_to_menu)]

    def back(self):
        """Resume, or Escape: the story carries on where it paused."""
        self.app.play_sound('back')
        self.stack.pop()
        self.episode_screen.resume()

    def restart(self):
        self.app.play_sound('restart')
        self.stack.pop()
        self.episode_screen.restart()

    def return_to_menu(self):
        self.app.play_sound('back')
        self.stack.pop()
        self.episode_screen.leave()


#: The original's own question, from -[CCEpisodeTableCell restartEpisode] and
#: replayEpisode (aidocks/plans/saves_plan.md).
RESTART_WARNING = ('Restart episode? If you restart this episode, all saved progress beyond '
                   'this episode will be erased.')


class RestartQuestion(Menu):
    """Restart episode, Replay episode, or the pause menu's Restart episode: asked first
    with the original's warning, No first, so a stray Enter keeps the place. Escape is No.
    ``on_yes`` is called once the question has closed."""

    name = 'restart question'
    title = RESTART_WARNING

    def __init__(self, app, on_yes):
        super().__init__(app)
        self.on_yes = on_yes

    def rows(self):
        return [Row('No', self.back), Row('Yes', self.restart)]

    def restart(self):
        self.stack.pop()
        self.on_yes()
