"""Try skip lengths by ear, to choose the one Left and Right should use. Not a test.

    python tests/interact/seek_check.py

It plays one of the story's longest recordings, and Left and Right skip back or forward by
the length set with A and D. Holding Left or Right repeats, after the game's own 0.4-second
wait (app.py's REPEAT_DELAY), at the rate set with Q and E (REPEAT_EVERY, changed here for
this tool alone), so a length and a rate sound here as they would in the game.

    A and D         a shorter or longer skip, said as it changes: 1, 2, 3, 5, 10, 15, 20,
                    30 or 60 seconds; the game uses 5
    Q and E         a slower or faster repeat while Left or Right is held: every 500 down
                    to 50 milliseconds, in steps of 50; the game uses 150
    Left and Right  skip back or forward by that length; hold to keep going
    T               where you are, and how long the recording is
    Space           pause and resume
    R               the recording again from its start
    N               the next of the longest recordings
    Escape          quit

The window shows the skip length, where you are and the recording's name. It plays the
loose recordings from source, or the mission pack when they are not there, as the game
does. It keeps its own save, in %APPDATA%\\CodenameCygnus\\seek_check, so your volumes in
the game are not changed, and its log is logs\\log.txt there.
"""
import logging
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
os.environ.setdefault('CYGNUS_USER_DIR',
                      os.path.join(os.environ.get('APPDATA') or os.path.expanduser('~'),
                                   'CodenameCygnus', 'seek_check'))
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

import pygame  # noqa: E402

from codenamecygnus import app as app_module  # noqa: E402
from codenamecygnus import paths  # noqa: E402
from codenamecygnus.app import App  # noqa: E402
from codenamecygnus.game.recordings import Recordings, story_key  # noqa: E402
from codenamecygnus.game.story import Story  # noqa: E402
from codenamecygnus.platform.audio import SKIP_SECONDS  # noqa: E402
from codenamecygnus.ui.screens import Screen  # noqa: E402

#: The skip lengths A and D move through, in seconds.
STEPS = (1, 2, 3, 5, 10, 15, 20, 30, 60)
#: The repeat rates Q and E move through, slowest first: milliseconds between repeats.
RATES = (500, 450, 400, 350, 300, 250, 200, 150, 100, 50)
#: The game's own, from app.py, which this tool changes for itself alone.
GAME_RATE = int(round(app_module.REPEAT_EVERY * 1000))
#: How many of the longest recordings N goes through.
LONGEST = 20


def seconds_text(seconds):
    """ "1 minute 5 seconds", "40 seconds" """
    seconds = int(round(seconds))
    minutes, rest = divmod(seconds, 60)
    parts = []
    if minutes:
        parts.append('%d minute%s' % (minutes, '' if minutes == 1 else 's'))
    if rest or not minutes:
        parts.append('%d second%s' % (rest, '' if rest == 1 else 's'))
    return ' '.join(parts)


def longest_voices(story, recordings, count=LONGEST):
    """The story's longest voice recordings, longest first, by their size on disk or in the
    pack, which follows their length closely enough to choose by."""
    sizes = {}
    for state in story.states.values():
        if not state.voice:
            continue
        key = story_key(state.voice)
        path = recordings.index.get(key)
        if path is not None:
            sizes[state.voice] = os.path.getsize(path)
        elif recordings.pack is not None and key in recordings.pack:
            sizes[state.voice] = recordings.pack.index[key][1]
    return sorted(sizes, key=sizes.get, reverse=True)[:count]


class SeekScreen(Screen):
    name = 'seek check'

    def __init__(self, app, voices, recordings):
        super().__init__(app)
        self.voices = voices
        self.recordings = recordings
        self.which = 0
        self.step = STEPS.index(int(SKIP_SECONDS)) if int(SKIP_SECONDS) in STEPS else 3
        self.rate = RATES.index(GAME_RATE) if GAME_RATE in RATES else RATES.index(150)
        self.set_rate()
        self.paused = False
        self.started = False

    @property
    def audio(self):
        return self.app.audio

    @property
    def seconds(self):
        return STEPS[self.step]

    @property
    def milliseconds(self):
        return RATES[self.rate]

    def set_rate(self):
        """The repeat rate the main loop uses while a key is held, for this tool only."""
        app_module.REPEAT_EVERY = self.milliseconds / 1000.0

    def rate_text(self):
        """ "every 150 milliseconds, about 7 a second" """
        return 'every %d milliseconds, about %d a second' % (
            self.milliseconds, round(1000.0 / self.milliseconds))

    def opened(self):
        if self.started:
            return
        self.started = True
        if not self.voices:
            return self.say('There are no recordings to play: Mission 1 is not here, loose '
                            'or downloaded. Press Escape to quit.')
        self.say('Seek check. A and D change the skip, now %s. Q and E change the repeat, '
                 'now %s. Left and Right skip.' % (seconds_text(self.seconds), self.rate_text()))
        self.play()

    def play(self):
        self.paused = False
        self.audio.resume()
        voice = self.voices[self.which]
        self.audio.play_voice(self.recordings.find(voice), on_end=self.ended)

    def ended(self):
        self.say('The end of the recording. R plays it again, N the next.')

    def where(self):
        length = self.audio.voice_length
        if self.audio.voice is None:
            return 'At the end.'
        return '%s of %s.' % (seconds_text(self.audio.position()),
                              seconds_text(length) if length else 'an unknown length')

    def handle_key(self, key, mods):
        if mods:
            return False
        if key == 'escape':
            self.app.quit()
        elif not self.voices:
            self.say('There are no recordings to play.')
        elif key in ('a', 'd'):
            self.step = max(0, min(len(STEPS) - 1, self.step + (1 if key == 'd' else -1)))
            self.say(seconds_text(self.seconds))
        elif key in ('q', 'e'):
            self.rate = max(0, min(len(RATES) - 1, self.rate + (1 if key == 'e' else -1)))
            self.set_rate()
            self.say('Repeats %s.' % self.rate_text())
        elif key in ('left', 'right'):
            if self.audio.voice is None:
                return self.say('At the end. R plays it again.')
            self.audio.seek(self.seconds if key == 'right' else -self.seconds)
        elif key == 't':
            self.say(self.where())
        elif key == 'space':
            self.paused = not self.paused
            (self.audio.pause if self.paused else self.audio.resume)()
            self.say('Paused.' if self.paused else 'Playing.')
        elif key == 'r':
            self.play()
            self.say('From the start.')
        elif key == 'n':
            self.which = (self.which + 1) % len(self.voices)
            self.play()
            self.say('Recording %d of %d.' % (self.which + 1, len(self.voices)))
        else:
            self.say('Skipping %s, repeating %s.' % (seconds_text(self.seconds), self.rate_text()))
        return True

    def repeats(self, key, mods):
        """Holding Left or Right repeats, as in the game."""
        return not mods and key in ('left', 'right') and not self.paused

    def lines(self):
        if not self.voices:
            return ['Seek check', '', 'No recordings.']
        return ['Seek check', '',
                'Skip: %s (the game uses %s)' % (seconds_text(self.seconds),
                                                 seconds_text(SKIP_SECONDS)),
                'Repeat: %s (the game uses %d milliseconds)' % (self.rate_text(), GAME_RATE),
                'Position: %s' % self.where(),
                'Recording %d of %d: %s' % (self.which + 1, len(self.voices),
                                            self.voices[self.which]),
                '', 'A and D: skip length. Q and E: repeat rate. Left and Right: skip.',
                'T: where you are.',
                'Space: pause. R: again. N: next. Escape: quit.']


def main():
    handler = logging.FileHandler(os.path.join(paths.logs_dir(), 'log.txt'), 'w', encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-7s %(name)-8s %(message)s',
                                           '%H:%M:%S'))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)
    options = types.SimpleNamespace(debug=False, episode=None, state=None, verbose=False,
                                    exit_after=None)
    app = App(options)
    recordings = Recordings.shared()
    voices = longest_voices(Story.shared(), recordings)
    app.run(SeekScreen(app, voices, recordings), pygame)
    logging.shutdown()
    return 0


if __name__ == '__main__':
    sys.exit(main())
