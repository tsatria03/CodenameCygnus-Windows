"""The Settings screen: section 2 of aidocks/plans/menus_plan.md, with the steps and
speeds of aidocks/plans/seek_settings_plan.md.

Each row says what it is and what it is set to, and the game remembers it in
``config/settings.json``:

    Back                            first, as in every menu
    Debug mode, currently off       source runs only, the first option
    Master volume, 100 percent      Enter opens its levels
    Background ambience volume, 100 percent
    Decision loop volume, 100 percent
    Volume step, 10 percent         how far a volume key moves a volume
    Volume speed, 100 milliseconds  how often a held volume key repeats
    Seek step, 10 seconds           how far Left and Right skip
    Seek speed, 100 milliseconds    how often a held Left or Right repeats
    Speech recognition, currently off   Enter turns it on or off
    Key bindings                    the F1 screen

Enter on a volume, a step or a speed opens its levels, Back and then the levels, on Back,
moved through with the usual menu keys (the dev, 2026-10-18: "With the volumes, you can
click on it, and the normal menu keys will work, up/down/left/right/home/end"). A volume's
levels go from 100 percent down to 0 by the Volume step (the dev, 2026-10-18: "The volume
step should follow the volume settings in the settings screen"). Enter sets the level and
comes back here; Escape keeps the old one. The same screen opens from the main menu and
from the pause menu during an episode, and a change is used at once.

With speech recognition on, a choice in an episode can be spoken
(aidocks/plans/speech_recognition_plan.md); turned on from the pause menu, it listens
once the story resumes.
"""
from __future__ import annotations

from .. import paths
from ..platform.audio import VOLUME_LABELS
from ..platform.settings import LEVELS, SPEEDS, VOLUMES
from .menu import Menu, Row

#: The steps and speeds, in the dev's order (2026-10-18: "Volume step, volume speed, seek
#: step, seek speed"), each with what its level is counted in.
TUNING = (('volume_step', 'Volume step', 'percent'),
          ('volume_speed', 'Volume speed', 'milliseconds'),
          ('seek_step', 'Seek step', 'seconds'),
          ('seek_speed', 'Seek speed', 'milliseconds'))
LABELS = dict(VOLUME_LABELS, **{key: label for key, label, _unit in TUNING})
UNITS = dict({key: 'percent' for key in VOLUMES}, **{key: unit for key, _label, unit in TUNING})


def level_text(key, level):
    """ "60 percent", "10 seconds", "100 milliseconds" """
    return '%d %s' % (level, UNITS[key])


def setting_text(app, key):
    """ "Background ambience volume, 60 percent", "Seek step, 10 seconds" """
    return '%s, %s' % (LABELS[key], level_text(key, app.settings.get(key)))


class SettingsScreen(Menu):
    name = 'settings'
    title = 'Settings.'

    def rows(self):
        # Back first, as in every menu, then Debug mode as the first option (the dev,
        # 2026-10-18: "The back button should always appear first in any menu").
        rows = [Row('Back', self.back)]
        if not paths.FROZEN:
            rows.append(Row(lambda: 'Debug mode, currently %s' % self.on_off('debug'),
                            self.toggle_debug))
        for key in VOLUMES:
            rows.append(Row(lambda key=key: setting_text(self.app, key),
                            lambda key=key: self.open(VolumeLevels(self.app, key))))
        for key, _label, _unit in TUNING:
            rows.append(Row(lambda key=key: setting_text(self.app, key),
                            lambda key=key: self.open(Levels(self.app, key))))
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


class Levels(Menu):
    """A setting's levels: Back, then the levels, opening on Back. A speed's ends say which
    way they go, "50 milliseconds, fastest" and "500 milliseconds, slowest", since a smaller
    number is faster."""

    name = 'levels'

    def __init__(self, app, key):
        super().__init__(app)
        self.key = key
        self.title = '%s.' % LABELS[key]
        # It opens on Back, as every menu does (the dev, 2026-10-18: "I want it to open on
        # the back button"); the Settings row has already said the level it is at.

    def levels(self):
        return LEVELS[self.key]

    def row_label(self, level):
        text = level_text(self.key, level)
        if self.levels() is SPEEDS:
            if level == SPEEDS[0]:
                text += ', fastest'
            elif level == SPEEDS[-1]:
                text += ', slowest'
        return text

    def rows(self):
        return [Row('Back', self.back)] + [
            Row(self.row_label(level), lambda level=level: self.set(level))
            for level in self.levels()]

    def set(self, level):
        self.app.settings.set(self.key, level)
        self.changed()
        self.stack.pop()
        # Cuts off Settings, which spoke as it came back.
        self.say('%s %s' % (LABELS[self.key], level_text(self.key, level)))

    def changed(self):
        """Used at once: the steps and speeds are read as they are needed."""


class VolumeLevels(Levels):
    """One volume's levels: Back, then 100 percent down to 0 percent by the Volume step."""

    name = 'volume levels'

    def levels(self):
        return tuple(range(100, -1, -self.app.settings.get('volume_step')))

    def changed(self):
        self.app.audio.apply_volumes()
