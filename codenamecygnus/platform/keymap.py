"""The keys a player uses during an episode, and their changes from the F1 screen.

The actions and their default keys are the ones agreed in
aidocks/plans/story_engine_plan.md and aidocks/plans/audio_plan.md. A binding is one key
with any of Shift, Control and Alt, written as pygame names it with the modifiers first,
such as ``"page up"`` or ``"shift+page up"``. It matches only with exactly those modifiers
held, so Page Up and Shift+Page Up never both fire. Left and right Shift count the same.

Keys are stored by name, not keycode, so a saved keymap survives a pygame update, in
``config/keys.json`` in the save folder, written safely like every other file there.

A few keys are fixed and cannot be rebound, so there is always a way out and the menus
always work: Escape, F1, and in a menu the arrows, Enter, Home and End. The number keys 1
to 9 always choose by number.
"""
from __future__ import annotations

import logging

from .. import paths
from .files import JsonFile

log = logging.getLogger('keymap')

#: (action, what the F1 screen calls it, default bindings). Debug actions work only in
#: debug mode, and the F1 screen lists them only then. Space no longer pauses (the dev,
#: 2026-10-18: "Can you remove space to pause? I feel like escape already does the job");
#: Escape, fixed, and P, the pause_menu action, open the pause menu ("add p to that list
#: along with escape"). The old ``pause`` binding, Space, is dropped from a keys file when
#: it is next written; the new action has a name of its own so it never comes back.
ACTIONS = (
    ('previous_choice', 'Previous choice', ('up',)),
    ('next_choice', 'Next choice', ('down',)),
    ('choose', 'Choose', ('return', 'enter')),
    ('repeat_choices', 'Say the choices again', ('c',)),
    ('pause_menu', 'Pause menu', ('p',)),
    ('replay', 'Replay the recording', ('r',)),
    ('back', 'Back 5 seconds', ('left',)),
    ('forward', 'Forward 5 seconds', ('right',)),
    ('skip', 'Skip to the choices, in a part heard before', ('s',)),
    ('heading', 'Say where you are', ('h',)),
    ('speech_recognition', 'Speech recognition on or off', ('v',)),
    ('master_up', 'Master volume up', ('shift+home',)),
    ('master_down', 'Master volume down', ('shift+end',)),
    ('ambience_up', 'Background ambience volume up', ('page up',)),
    ('ambience_down', 'Background ambience volume down', ('page down',)),
    ('decision_up', 'Decision loop volume up', ('shift+page up',)),
    ('decision_down', 'Decision loop volume down', ('shift+page down',)),
    ('debug_skip', 'Debug: skip the recording', ('f2',)),
    ('debug_jump', 'Debug: jump to a state', ('f3',)),
    ('debug_state', 'Debug: say the state, traits and flags', ('f4',)),
)

ACTION_IDS = [a[0] for a in ACTIONS]
DEBUG_IDS = [a for a in ACTION_IDS if a.startswith('debug_')]
LABELS = {a[0]: a[1] for a in ACTIONS}
DEFAULTS = {a[0]: list(a[2]) for a in ACTIONS}

#: Never rebindable: bind over these and there would be no way back.
FIXED = {'escape': 'Back, pause or quit', 'f1': 'Key bindings'}
#: Listed on the F1 screen beside the actions, but not rebindable either.
FIXED_TEXT = (('1 to 9', 'Choose by number'),
              ('Arrows, Enter, Home and End', 'Move and choose in a menu, Left and Right as Up and Down'))

MODIFIERS = ('shift', 'ctrl', 'alt')
#: pygame's names for the modifier keys themselves, which are never a binding on their own.
MODIFIER_KEYS = {'left shift', 'right shift', 'left ctrl', 'right ctrl', 'left alt',
                 'right alt', 'left meta', 'right meta', 'left super', 'right super',
                 'caps lock', 'num lock', 'scroll lock', 'mode', 'compose', 'menu'}

#: pygame's terse names, as they should be spoken.
SPOKEN = {
    'left': 'Left Arrow', 'right': 'Right Arrow', 'up': 'Up Arrow', 'down': 'Down Arrow',
    'space': 'Space', 'tab': 'Tab', 'escape': 'Escape', 'return': 'Enter', 'enter': 'Keypad Enter',
    'shift': 'Shift', 'ctrl': 'Control', 'alt': 'Alt',
    ',': 'Comma', '.': 'Full stop', '/': 'Slash', ';': 'Semicolon', "'": 'Apostrophe',
    '[': 'Left bracket', ']': 'Right bracket', '\\': 'Backslash', '-': 'Minus',
    '=': 'Equals', '`': 'Backtick', 'backspace': 'Backspace', 'delete': 'Delete',
    'home': 'Home', 'end': 'End', 'page up': 'Page Up', 'page down': 'Page Down',
    'insert': 'Insert',
}


def binding(key, mods=()):
    """The binding for a key pressed with these modifiers, such as ``shift+page up``."""
    held = [m for m in MODIFIERS if m in set(mods)]
    return '+'.join(held + [key])


def mods_from_pygame(mod_state, pygame):
    """The modifiers held, from pygame's ``event.mod``."""
    held = []
    if mod_state & pygame.KMOD_SHIFT:
        held.append('shift')
    if mod_state & pygame.KMOD_CTRL:
        held.append('ctrl')
    if mod_state & pygame.KMOD_ALT:
        held.append('alt')
    return held


def key_text(name):
    """One key name as it should be spoken."""
    if name in SPOKEN:
        return SPOKEN[name]
    if len(name) == 1:
        return name.upper()
    return name.title()


def binding_text(b):
    """A binding as it should be spoken: 'Shift plus Page Up'."""
    return ' plus '.join(key_text(part) for part in b.split('+') if part)


def bindings_text(bindings):
    if not bindings:
        return 'nothing'
    return ', or '.join(binding_text(b) for b in bindings)


def _clean(saved):
    """The bindings a file gives an action, keeping only strings that name a key."""
    if not isinstance(saved, list):
        return None
    return [b for b in saved if isinstance(b, str) and b and not b.endswith('+')]


class KeyMap:
    _shared = None

    @classmethod
    def shared(cls):
        if cls._shared is None:
            cls._shared = KeyMap()
        return cls._shared

    def __init__(self, path=None):
        self.file = JsonFile(path or paths.user_path('config', 'keys.json'), order=ACTION_IDS)
        self.bindings = {a: list(DEFAULTS[a]) for a in ACTION_IDS}
        self.debug = False          # debug mode: the debug_ actions are live
        changed = self.file.recovered
        for action in ACTION_IDS:
            saved = _clean(self.file.data.get(action))
            if saved is None:
                changed = True      # a new action, or one the file got wrong
            else:
                self.bindings[action] = saved
        if changed:
            self.save()

    @property
    def actions(self):
        """The actions in play: every one in debug mode, the debug_ ones left out otherwise."""
        if self.debug:
            return list(ACTION_IDS)
        return [a for a in ACTION_IDS if a not in DEBUG_IDS]

    def save(self):
        self.file.data = {a: list(self.bindings[a]) for a in ACTION_IDS}
        self.file.write()

    def reset(self):
        self.bindings = {a: list(DEFAULTS[a]) for a in ACTION_IDS}
        self.save()

    def label(self, action):
        return LABELS[action]

    def keys_text(self, action):
        return bindings_text(self.bindings.get(action, []))

    def action_for(self, key, mods=()):
        """The action a key pressed with these modifiers does, or None."""
        b = binding(key, mods)
        for action in self.actions:
            if b in self.bindings[action]:
                return action
        return None

    def conflicts(self, b, ignore=None):
        """The actions already using this binding."""
        return [a for a in ACTION_IDS if a != ignore and b in self.bindings[a]]

    def set_binding(self, action, b, replace=True):
        """Give ``action`` this binding, taking it off whatever else had it."""
        for other in ACTION_IDS:
            self.bindings[other] = [x for x in self.bindings[other] if x != b]
        self.bindings[action] = [b] if replace else self.bindings[action] + [b]
        self.save()

    def clear(self, action):
        self.bindings[action] = []
        self.save()
