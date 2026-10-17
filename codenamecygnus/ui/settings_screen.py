"""The Settings screen.

Each row says what it is and what it is set to, such as "Debug mode, currently off", and
Enter changes it at once; the game remembers it in ``config/settings.json``.

The foundation brings only the Debug mode row, shown only when running from source
(aidocks/plans/foundation_plan.md). The speech recognition row and the volumes join it as
their plans are built.
"""
from __future__ import annotations

from .. import paths
from .menu import Menu, Row


class SettingsScreen(Menu):
    name = 'settings'
    title = 'Settings.'

    def rows(self):
        rows = [Row('Back', self.back)]
        if not paths.FROZEN:
            rows.append(Row(lambda: 'Debug mode, currently %s' % self.on_off('debug'),
                            self.toggle_debug))
        return rows

    def on_off(self, key):
        return 'on' if self.app.settings.get(key) else 'off'

    def toggle_debug(self):
        self.app.set_debug(not self.app.debug)
        self.say(self.row_text())
