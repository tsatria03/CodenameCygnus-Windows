"""The Settings screen: section 2 of aidocks/plans/menus_plan.md.

Each row says what it is and what it is set to, and the game remembers it in
``config/settings.json``:

    Debug mode, currently off       source runs only, first (the dev, 2026-10-18)
    Back
    Master volume, 100 percent      Enter opens its levels
    Background ambience volume, 100 percent
    Decision loop volume, 100 percent
    Speech recognition, currently off   Enter turns it on or off
    Key bindings                    the F1 screen

Enter on a volume opens its levels, 100 percent down to 0 percent in tens, on the one it
is at, moved through with the usual menu keys (the dev, 2026-10-18: "With the volumes, you
can click on it, and the normal menu keys will work, up/down/left/right/home/end"). Enter
sets the level and comes back here; Escape keeps the old one. The same screen opens from
the main menu and from the pause menu during an episode.

Speech recognition is remembered now, and listened for once
aidocks/plans/speech_recognition_plan.md is built.
"""
from __future__ import annotations

from .. import paths
from ..platform.audio import VOLUME_LABELS
from ..platform.settings import VOLUMES
from .menu import Menu, Row


def volume_text(app, key):
    """ "Background ambience volume, 60 percent" """
    return '%s, %d percent' % (VOLUME_LABELS[key], app.settings.get(key))


class SettingsScreen(Menu):
    name = 'settings'
    title = 'Settings.'

    def rows(self):
        rows = []
        if not paths.FROZEN:
            # First (the dev, 2026-10-18: "The debug mode should be the first option").
            rows.append(Row(lambda: 'Debug mode, currently %s' % self.on_off('debug'),
                            self.toggle_debug))
        rows.append(Row('Back', self.back))
        for key in VOLUMES:
            rows.append(Row(lambda key=key: volume_text(self.app, key),
                            lambda key=key: self.open(VolumeLevels(self.app, key))))
        rows.append(Row(lambda: 'Speech recognition, currently %s' % self.on_off('speech_recognition'),
                        self.toggle_speech_recognition))
        rows.append(Row('Key bindings', self.app.open_key_bindings))
        return rows

    def on_off(self, key):
        return 'on' if self.app.settings.get(key) else 'off'

    def toggle_speech_recognition(self):
        self.app.settings.toggle('speech_recognition')
        self.say(self.row_text())

    def toggle_debug(self):
        self.app.set_debug(not self.app.debug)
        self.say(self.row_text())


class VolumeLevels(Menu):
    """One volume's levels, loudest first, on the one it is at."""

    name = 'volume levels'
    LEVELS = tuple(range(100, -1, -10))

    def __init__(self, app, key):
        super().__init__(app)
        self.key = key
        self.title = '%s.' % VOLUME_LABELS[key]
        now = app.settings.get(key)
        self.index = self.LEVELS.index(now) if now in self.LEVELS else 0

    def rows(self):
        return [Row('%d percent' % level, lambda level=level: self.set(level))
                for level in self.LEVELS]

    def set(self, level):
        self.app.settings.set(self.key, level)
        self.app.audio.apply_volumes()
        self.stack.pop()
        # Cuts off Settings, which spoke as it came back.
        self.say('%s %d percent' % (VOLUME_LABELS[self.key], level))
