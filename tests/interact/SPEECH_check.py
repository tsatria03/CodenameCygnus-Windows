"""Speak the story's choices and hear what speech recognition makes of them. Not a test.

    python tests/interact/SPEECH_check.py

It opens on a list: the microphone's name first, then Every choice word, which listens
for all 98 at once, then the eight episodes. An episode opens its questions, Back first,
each one its choices, such as "Charismatic or Hostile", with any hidden ones after, such
as "Delphi's or My own, also Mine or Her drink". Up and Down move, Enter opens, Escape
goes back, and Escape on the first list quits.

A question listens for 15 seconds, as the game does at a choice, until it hears one:

    "Heard Hostile."                                    a choice, and listening stops
    "Sorry, I did not catch that. It sounded like um."  speech that is no choice, with
                                                        the word the recogniser picked;
                                                        listening goes on
    "No longer listening."                              15 seconds are up

    Enter or C      listen again, for another 15 seconds
    Escape          back to the questions

The window lists everything heard, and how many of each, so a word that is often missed
or mistaken can be found. Headphones keep the screen reader out of the microphone.

Nothing is recorded or kept. It keeps its own save, in
%APPDATA%\\CodenameCygnus\\voice_check, and its log is logs\\log.txt there.
"""
import logging
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
os.environ.setdefault('CYGNUS_USER_DIR',
                      os.path.join(os.environ.get('APPDATA') or os.path.expanduser('~'),
                                   'CodenameCygnus', 'voice_check'))
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

import pygame  # noqa: E402

from codenamecygnus import paths  # noqa: E402
from codenamecygnus.app import App  # noqa: E402
from codenamecygnus.game.episode_screen import (BLOCKED_TEXT, LISTEN_SECONDS, NO_MICROPHONE_TEXT,  # noqa: E402
                                                NOT_CAUGHT, NOT_LISTENING, choices_text)
from codenamecygnus.game.story import Story  # noqa: E402
from codenamecygnus.platform.listener import BLOCKED, MicrophoneError, microphone_name  # noqa: E402
from codenamecygnus.ui.menu import Menu, Row  # noqa: E402
from codenamecygnus.ui.screens import Screen  # noqa: E402


def episode_states(story, episode):
    """Every state an episode reaches from its start, in the order the story reaches them."""
    seen, order, todo = set(), [], [episode.start]
    while todo:
        name = todo.pop(0)
        if name in seen or name not in story.states:
            continue
        seen.add(name)
        order.append(name)
        todo += story.leads_to(name)
    return order


def questions(story, episode):
    """(what it is called, its phrases) for each different question in an episode."""
    out, seen = [], set()
    for name in episode_states(story, episode):
        choices = story.choices(name, include_hidden=True)
        phrases = tuple(c.text for c in choices)
        if not phrases or frozenset(phrases) in seen:
            continue
        seen.add(frozenset(phrases))
        shown = [c for c in choices if not c.hidden]
        hidden = [c for c in choices if c.hidden]
        label = choices_text(shown)[:-1] if shown else 'Nothing shown'
        if hidden:
            label += ', also ' + choices_text(hidden)[:-1]
        out.append((label, list(phrases)))
    return out


class VoiceChooser(Menu):
    name = 'voice check'
    title = 'Voice check. Choose what to listen for.'

    def __init__(self, app, story):
        super().__init__(app)
        self.story = story
        self.microphone = microphone_name()

    def rows(self):
        rows = [Row('Microphone: %s' % (self.microphone or 'none found')),
                Row('Every choice word', lambda: self.stack.push(
                    ListenScreen(self.app, 'Every choice word', self.story.choice_texts(), self.story)))]
        for e in self.story.playable_episodes():
            rows.append(Row('Episode %d, %s' % (e.number, e.title),
                            lambda e=e: self.stack.push(QuestionList(self.app, self.story, e))))
        return rows

    def back(self):
        self.app.quit()


class QuestionList(Menu):
    name = 'questions'

    def __init__(self, app, story, episode):
        super().__init__(app)
        self.story = story
        self.title = 'Episode %d, %s.' % (episode.number, episode.title)
        self.questions = questions(story, episode)

    def rows(self):
        return [Row('Back', self.back)] + [
            Row(label, lambda label=label, phrases=phrases: self.stack.push(
                ListenScreen(self.app, label, phrases, self.story)))
            for label, phrases in self.questions]


class ListenScreen(Screen):
    """Listens for one question's phrases, 15 seconds at a time, saying what it heard."""

    name = 'listen'

    def __init__(self, app, label, phrases, story):
        super().__init__(app)
        self.label = label
        self.phrases = list(phrases)
        self.story = story
        self.timer = None
        self.history = []           # what was heard, newest last
        self.counts = {}            # what was heard -> how many times

    @property
    def listener(self):
        return self.app.listener

    def opened(self):
        self.listen('Listening for %s.' % self.label)

    def closed(self):
        self.stop()

    def covered(self):
        self.stop()

    def listen(self, text='Listening.'):
        self.stop()
        try:
            if not self.listener.start(self.phrases, others=self.story.choice_texts()):
                return self.say('None of these words can be listened for.')
        except MicrophoneError as error:
            return self.say(BLOCKED_TEXT if error.kind == BLOCKED else NO_MICROPHONE_TEXT)
        self.say(text)
        self.timer = self.app.loop.after(LISTEN_SECONDS, self.ended)

    def stop(self):
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None
        self.listener.stop()

    def ended(self):
        self.timer = None
        self.listener.stop()
        self.say(NOT_LISTENING)

    def update(self):
        for phrase, words in self.listener.poll():
            note = phrase.capitalize() if phrase is not None else 'no choice: %s' % (words or 'nothing')
            self.history.append(note)
            self.counts[note] = self.counts.get(note, 0) + 1
            if phrase is not None:
                # A choice heard stops listening, as it does in the game (the dev,
                # 2026-10-18: "as soon as it heres the correct word, it should stop
                # listening").
                self.stop()
                self.say('Heard %s.' % note)
                return
            self.say('%s. It sounded like %s.' % (NOT_CAUGHT, words or 'nothing'))

    def handle_key(self, key, mods):
        if mods:
            return False
        if key == 'escape':
            self.stack.pop()
        elif key in ('return', 'enter', 'c'):
            self.listen()
        else:
            self.say('Listening.' if self.listener.listening else
                     'Not listening. Press Enter to listen again.')
        return True

    def lines(self):
        out = [self.label, '(listening)' if self.listener.listening else '(not listening)', '']
        out += ['%s: %d' % (k, v) for k, v in sorted(self.counts.items())]
        if self.history:
            out += ['', 'Last heard: ' + ', '.join(self.history[-6:])]
        return out


def main():
    handler = logging.FileHandler(os.path.join(paths.logs_dir(), 'log.txt'), 'w', encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-7s %(name)-8s %(message)s',
                                           '%H:%M:%S'))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)
    options = types.SimpleNamespace(debug=False, episode=None, state=None, verbose=False,
                                    exit_after=None)
    app = App(options)
    app.run(VoiceChooser(app, Story.shared()), pygame)
    logging.shutdown()
    return 0


if __name__ == '__main__':
    sys.exit(main())
