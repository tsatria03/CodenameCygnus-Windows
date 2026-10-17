"""The key bindings screen, opened with F1 from anywhere and read aloud.

    Up and Down     move through the actions, each read with its keys
    Home and End    the first action and the last
    Enter           rebind: press the key you want, with Shift, Control or Alt if you like
    A               add a second key instead of replacing
    Delete          unbind
    R               reset every binding, after asking: R again to do it
    F1 or Escape    back

Escape and F1 can never be rebound, so there is always a way out, and neither can the
number keys 1 to 9, which always choose by number (aidocks/plans/foundation_plan.md).
"""
from __future__ import annotations

import logging

from ..platform.keymap import FIXED, FIXED_TEXT, MODIFIER_KEYS, binding, key_text
from .screens import Screen

log = logging.getLogger('keybind')

HELP = ('Key bindings. Up and Down to move, Enter to rebind, A to add a second key, '
        'Delete to unbind, R twice to reset everything, Escape to go back.')
RESET_PROMPT = ('Reset every binding to the default? Press R again to do it, or any other '
                'key to keep the bindings you have.')
#: Keys that can never be given to an action.
UNBINDABLE = set(FIXED) | {str(n) for n in range(1, 10)}


class KeyBindScreen(Screen):
    name = 'key bindings'

    def __init__(self, app):
        super().__init__(app)
        self.keymap = app.keymap
        self.index = 0
        self.capturing = False
        self.capture_add = False
        self.confirm_reset = False

    @property
    def action(self):
        return self.keymap.actions[self.index]

    def current_text(self):
        a = self.action
        return '%s: %s' % (self.keymap.label(a), self.keymap.keys_text(a))

    def opened(self):
        self.capturing = self.confirm_reset = False
        self.say(HELP)
        self.say(self.current_text(), interrupt=False)

    def move_to(self, i):
        self.index = i % len(self.keymap.actions)
        self.say(self.current_text())

    def capture(self, add):
        self.capturing, self.capture_add = True, add
        self.say('Press the key for %s.' % self.keymap.label(self.action))

    def finish_capture(self, key, mods):
        self.capturing = False
        b = binding(key, mods)
        if key in FIXED or (key in UNBINDABLE and not mods):
            self.say('%s cannot be rebound. %s' % (key_text(key), self.current_text()))
            return
        stolen = self.keymap.conflicts(b, ignore=self.action)
        self.keymap.set_binding(self.action, b, replace=not self.capture_add)
        said = '%s is now %s.' % (self.keymap.label(self.action), self.keymap.keys_text(self.action))
        if stolen:
            said += ' Taken from %s.' % ', '.join(self.keymap.label(a) for a in stolen)
        self.say(said)

    def handle_key(self, key, mods):
        if self.capturing:
            if key in MODIFIER_KEYS:
                return True                 # wait for the key that goes with them
            self.finish_capture(key, mods)
            return True
        if self.confirm_reset:
            self.confirm_reset = False
            if key == 'r' and not mods:
                self.keymap.reset()
                self.say('Every binding is back to the default. %s' % self.current_text())
            else:
                self.say('Your bindings are kept. %s' % self.current_text())
            return True
        if mods:
            self.say(self.current_text())
            return True
        if key in ('escape', 'f1'):
            self.stack.pop()
        elif key == 'up':
            self.move_to(self.index - 1)
        elif key == 'down':
            self.move_to(self.index + 1)
        elif key == 'home':
            self.move_to(0)
        elif key == 'end':
            self.move_to(len(self.keymap.actions) - 1)
        elif key in ('return', 'enter'):
            self.capture(add=False)
        elif key == 'a':
            self.capture(add=True)
        elif key in ('delete', 'backspace'):
            self.keymap.clear(self.action)
            self.say('%s is unbound.' % self.keymap.label(self.action))
        elif key == 'r':
            self.confirm_reset = True
            self.say(RESET_PROMPT)
        else:
            self.say(self.current_text())
        return True

    def lines(self):
        out = ['Key bindings', '']
        for i, a in enumerate(self.keymap.actions):
            out.append('%s %-44s %s' % ('>' if i == self.index else ' ',
                                        self.keymap.label(a), self.keymap.keys_text(a)))
        out.append('')
        for name, what in FIXED.items():
            out.append('  %-44s %s (fixed)' % (what, key_text(name)))
        for keys, what in FIXED_TEXT:
            out.append('  %-44s %s (fixed)' % (what, keys))
        if self.capturing:
            out += ['', 'Press the key you want...']
        if self.confirm_reset:
            out += ['', 'Press R again to reset every binding, or any other key to keep them.']
        return out
