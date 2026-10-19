"""The player's settings, in ``config/settings.json`` in the save folder.

Every setting is written on the first start, at its default, so the file always lists all
of them (aidocks/plans/saves_plan.md). A value the game cannot use is put back to its
default, and a setting it no longer knows is left alone.
"""
from __future__ import annotations

import logging

from .. import paths
from .files import JsonFile

log = logging.getLogger('settings')

#: Each setting's default, in the order the file lists them.
DEFAULTS = {
    'speech_recognition': False,        # aidocks/plans/speech_recognition_plan.md: off at first
    'master_volume': 100,               # aidocks/plans/audio_plan.md: 0 to 100, in fives
    'ambience_volume': 100,
    'decision_volume': 100,
    # aidocks/plans/seek_settings_plan.md: how far a volume key moves a volume, in percent,
    # how often a held one repeats, in milliseconds, and the same for Left and Right, in
    # seconds. The seek step was 5 seconds before it was a setting.
    'volume_step': 10,
    'volume_speed': 100,
    'seek_step': 10,
    'seek_speed': 100,
    'debug': False,                     # aidocks/plans/foundation_plan.md: source runs only
    'headphones_notice_shown': False,   # aidocks/plans/menus_plan.md: the first start only
}
VOLUMES = ('master_volume', 'ambience_volume', 'decision_volume')
#: Every volume step divides 100, so each volume is a multiple of 5 and 0 and 100 are
#: always reached.
VOLUME_MULTIPLE = 5
#: Milliseconds between repeats of a held key, fastest first (the dev, 2026-10-18: "It
#: should only be 50, 100, 150, 200, 250, 300, 350, 400, 450, and 500").
SPEEDS = tuple(range(50, 501, 50))
#: The levels of the settings that have them, in the order their lists give them.
LEVELS = {
    'volume_step': (5, 10, 20, 25),
    'volume_speed': SPEEDS,
    'seek_step': (5, 10, 15, 20, 30, 60),
    'seek_speed': SPEEDS,
}


def _valid(key, value):
    default = DEFAULTS[key]
    if isinstance(default, bool):
        return isinstance(value, bool)
    if isinstance(value, bool) or not isinstance(value, type(default)):
        return False
    if key in VOLUMES:
        return 0 <= value <= 100 and value % VOLUME_MULTIPLE == 0
    if key in LEVELS:
        return value in LEVELS[key]
    return True


class Settings:
    _shared = None

    @classmethod
    def shared(cls):
        if cls._shared is None:
            cls._shared = Settings()
        return cls._shared

    def __init__(self, path=None):
        self.file = JsonFile(path or paths.user_path('config', 'settings.json'),
                             order=list(DEFAULTS))
        changed = self.file.recovered
        for key, default in DEFAULTS.items():
            if key not in self.file.data:
                self.file.data[key] = default
                changed = True
            elif not _valid(key, self.file.data[key]):
                log.warning('settings: %s was %r, put back to %r', key, self.file.data[key], default)
                self.file.data[key] = default
                changed = True
        if changed:
            self.file.write()

    def get(self, key):
        return self.file.data.get(key, DEFAULTS[key])

    def set(self, key, value):
        """Change a setting and write the file at once."""
        if key not in DEFAULTS:
            raise KeyError(key)
        if not _valid(key, value):
            raise ValueError('%s cannot be %r' % (key, value))
        self.file.data[key] = value
        self.file.write()

    def every(self, key):
        """A speed setting in seconds, as the main loop's repeat takes it."""
        return self.get(key) / 1000.0

    def toggle(self, key):
        """Turn an on-or-off setting over; the new value."""
        value = not self.get(key)
        self.set(key, value)
        return value
