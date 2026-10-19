"""The stack of screens the main loop drives.

The top screen gets every key and is drawn in the window. A screen can open another on top
(``stack.push``), close itself (``stack.pop``), or put another in its place
(``stack.replace``); closing the last one ends the game. The F1 key bindings screen goes
on top of whatever is open, and the story's timers are held while it is up
(aidocks/plans/foundation_plan.md).
"""
from __future__ import annotations

import logging

log = logging.getLogger('screens')


class Screen:
    """What every screen has. Subclasses fill in what they need."""

    #: A short name for the log.
    name = 'screen'
    #: True for a screen whose timers must stop while another is on top of it.
    holds_time = False

    def __init__(self, app):
        self.app = app

    @property
    def stack(self):
        return self.app.stack

    def say(self, text, interrupt=True):
        self.app.speech.speak(text, interrupt)

    def opened(self):
        """Put on top of the stack, or back on top after the one above it closed."""

    def closed(self):
        """Taken off the stack for good."""

    def covered(self):
        """Another screen was opened on top of this one."""

    def handle_key(self, key, mods):
        """A key was pressed: pygame's name for it, and the modifiers held. True when used."""
        return False

    def repeats(self, key, mods):
        """Whether holding this key down presses it again and again, such as a skip or a
        volume step. Only keys that are safe to press twice say yes, never Enter or
        a choice key."""
        return False

    def repeat_every(self, key, mods):
        """Seconds between repeats of a key that repeats, or None for the main loop's own
        (app.py's REPEAT_EVERY)."""
        return None

    def update(self):
        """Called once a frame while on top."""

    def focus_lost(self):
        """The game's window lost the keyboard."""

    def focus_gained(self):
        """The game's window has the keyboard again."""

    def lines(self):
        """What the window shows, for a sighted helper."""
        return []


class ScreenStack:
    def __init__(self):
        self.screens = []

    @property
    def top(self):
        return self.screens[-1] if self.screens else None

    @property
    def empty(self):
        return not self.screens

    def push(self, screen):
        if self.top is not None:
            self.top.covered()
        self.screens.append(screen)
        log.info('opened %s', screen.name)
        screen.opened()

    def put_under(self, screen):
        """Put ``screen`` at the bottom without opening it; it opens when the screens above
        it close. ``--episode`` starts the story over a main menu this way, so the menu says
        nothing until the episode is left."""
        self.screens.insert(0, screen)
        log.info('put %s underneath', screen.name)

    def pop(self):
        """Close the top screen and reopen the one below it."""
        if not self.screens:
            return
        screen = self.screens.pop()
        log.info('closed %s', screen.name)
        screen.closed()
        if self.top is not None:
            self.top.opened()

    def replace(self, screen):
        """Put ``screen`` in place of the top one."""
        if self.screens:
            old = self.screens.pop()
            log.info('closed %s', old.name)
            old.closed()
        self.screens.append(screen)
        log.info('opened %s', screen.name)
        screen.opened()

    def clear(self):
        while self.screens:
            self.screens.pop().closed()
