"""A stand-in main menu, until aidocks/plans/menus_plan.md builds the real one.

It is there so the game can be tried by ear: Episodes, Settings and Quit, with Escape
quitting too. Episodes lists all eight episodes of Mission 1, every one open, and Enter
starts one; leaving it comes back to the list (the dev, 2026-10-17: "Can you please make
an interactive episode chooser so I can test it without typing any commands?"). The menus
plan replaces it with Continue, Episodes, Agent profile, Settings, Credits and Quit, and
the saves plan brings the locking.
"""
from __future__ import annotations

from ..ui.menu import Menu, Row
from ..ui.settings_screen import SettingsScreen
from .episode_screen import EpisodeScreen
from .story import Story


class StandInMainMenu(Menu):
    name = 'main menu'
    title = 'Codename Cygnus. Main menu.'

    def rows(self):
        return [Row('Episodes', lambda: self.stack.push(EpisodeChooser(self.app))),
                Row('Settings', lambda: self.stack.push(SettingsScreen(self.app))),
                Row('Quit', self.app.quit)]

    def back(self):
        self.app.quit()


class EpisodeChooser(Menu):
    name = 'episodes'
    title = 'Episodes. Mission 1.'

    def __init__(self, app, story=None):
        super().__init__(app)
        self.story = story or Story.shared()

    def rows(self):
        return [Row('Episode %d, %s' % (e.number, e.title), lambda e=e: self.play(e))
                for e in self.story.playable_episodes()]

    def play(self, episode):
        self.stack.push(EpisodeScreen(self.app, episode, story=self.story))
