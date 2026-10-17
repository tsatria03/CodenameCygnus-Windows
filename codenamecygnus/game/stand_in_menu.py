"""A stand-in main menu, until aidocks/plans/menus_plan.md builds the real one.

It is there so the foundation's speech, keys, settings and window can be tried by ear:
Settings and Quit, with Escape quitting too. The menus plan replaces it with Continue,
Episodes, Agent profile, Settings, Credits and Quit.
"""
from __future__ import annotations

from ..ui.menu import Menu, Row
from ..ui.settings_screen import SettingsScreen


class StandInMainMenu(Menu):
    name = 'main menu'
    title = 'Codename Cygnus. Main menu.'

    def rows(self):
        return [Row('Settings', lambda: self.stack.push(SettingsScreen(self.app))),
                Row('Quit', self.app.quit)]

    def back(self):
        self.app.quit()
