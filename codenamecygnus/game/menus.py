"""The screens around the story: section 1 of aidocks/plans/menus_plan.md.

    the opening      "Codename Cygnus" and one of the original's loading messages, then
                     the first time only, the headphones notice
    the main menu    Episodes, Settings, Credits, Quit; Escape quits too
    Episodes         Mission 1's episodes, each by its number and title; Enter opens its
                     own screen, which says its description and offers Start
    Credits          Reactive Studios' company credits, and a line for the port

Every one is a spoken menu (ui/menu.py), and each plays the original's interface sound at
the original's moment (app.py's SOUNDS). Continue, the episodes' states and locks, Restart
and the agent profile come with aidocks/plans/saves_plan.md; until then every episode is
open.
"""
from __future__ import annotations

import logging
import random

from ..ui.menu import Menu, Row
from ..ui.screens import Screen
from ..ui.settings_screen import SettingsScreen
from .episode_screen import EpisodeScreen
from .story import Story

log = logging.getLogger('menus')

#: The original's loading messages, from its en.lproj/Localizable.strings.
LOADING = ('Counting Stars...', 'Reticulating Splines...', 'Almost There...',
           'Folding Papers...', 'Adjusting Mainframe...', 'Baking Bagels...',
           'Measuring Squares...', 'Calculating Distance...')
#: Seconds the opening waits, so its message is heard, unless a key is pressed.
OPENING_SECONDS = 2.5
HEADPHONES = ('Headphones recommended. The acoustic experience of Codename Cygnus is best '
              'with the use of a high quality headset.')
#: The port's own line in Credits.
PORT_CREDIT = 'Windows port: tsatria03'


class Opening(Screen):
    """The game starting: its name and a loading message, then the headphones notice the
    first time, then the main menu. Any key goes on at once."""

    name = 'opening'

    def __init__(self, app, story=None, rng=random):
        super().__init__(app)
        self.story = story
        self.message = rng.choice(LOADING)
        self.call = None

    def opened(self):
        if self.call is None:
            self.say('Codename Cygnus. %s' % self.message)
            self.call = self.app.loop.after(OPENING_SECONDS, self.go_on)

    def handle_key(self, key, mods):
        self.go_on()
        return True

    def go_on(self):
        if self.stack.top is not self:
            return
        self.call.cancel()
        if self.app.settings.get('headphones_notice_shown'):
            self.stack.replace(MainMenu(self.app, self.story))
        else:
            self.stack.replace(HeadphonesNotice(self.app, self.story))

    def lines(self):
        return ['Codename Cygnus', '', self.message]


class HeadphonesNotice(Menu):
    """The first start only, as the original's kHeadphonesKey kept it."""

    name = 'headphones notice'
    title = HEADPHONES

    def __init__(self, app, story=None):
        super().__init__(app)
        self.story = story

    def rows(self):
        return [Row('Continue', self.go_on)]

    def back(self):
        self.go_on()

    def go_on(self):
        self.app.settings.set('headphones_notice_shown', True)
        self.stack.replace(MainMenu(self.app, self.story))


class MainMenu(Menu):
    name = 'main menu'
    title = 'Main menu.'

    def __init__(self, app, story=None):
        super().__init__(app)
        self.story = story or Story.shared()

    def rows(self):
        return [Row('Episodes', lambda: self.open(EpisodeList(self.app, self.story), 'episodes')),
                Row('Settings', lambda: self.open(SettingsScreen(self.app))),
                Row('Credits', lambda: self.open(CreditsScreen(self.app, self.story), 'credits')),
                Row('Quit', self.app.quit)]

    def back(self):
        """Escape on the main menu quits, as Quit does."""
        self.app.quit()


def episode_name(episode):
    """ "Episode 2, Art Show" """
    return 'Episode %d, %s' % (episode.number, episode.title)


class EpisodeList(Menu):
    """Mission 1's episodes. Its old description, written for selling episodes, and
    Mission 2, never released, are left out."""

    name = 'episodes'
    title = 'Episodes. Mission 1.'

    def __init__(self, app, story):
        super().__init__(app)
        self.story = story

    def rows(self):
        # Back at the top (the dev, 2026-10-18: "There should also bee a back button in the
        # episode list, at the top of the screen").
        return [Row('Back', self.back)] + [
            Row(episode_name(e), lambda e=e: self.open(EpisodeMenu(self.app, self.story, e)))
            for e in self.story.playable_episodes()]


class EpisodeMenu(Menu):
    """One episode's own screen: its description first, then what can be done with it."""

    name = 'episode menu'

    def __init__(self, app, story, episode):
        super().__init__(app)
        self.story = story
        self.episode = episode
        self.title = '%s. %s' % (episode_name(episode), episode.description.strip())

    def rows(self):
        return [Row('Start', self.start)]

    def start(self):
        """The episode in this screen's place, so leaving it comes back to the list."""
        self.app.play_sound('play')
        self.stack.replace(EpisodeScreen(self.app, self.episode, story=self.story))


def credit_lines(credits):
    """Credits as rows: "CEO: Jonathon Myers", or a heading alone, such as "Voice actors"."""
    out = []
    for c in credits:
        title, credit = c.get('title', '').strip(), c.get('credit', '').strip()
        if title and credit:
            out.append('%s: %s' % (title, credit))
        elif credit or title:
            text = credit or title
            out.append(text.capitalize() if text.isupper() else text)
    return out


class CreditsScreen(Menu):
    """Reactive Studios' company credits, as the original's Info screen had them, and the
    port's line. Each episode's own credits come at its end (section 3)."""

    name = 'credits'
    title = 'Credits. Codename Cygnus is a game by Reactive Studios.'

    def __init__(self, app, story):
        super().__init__(app)
        self.story = story

    def rows(self):
        return [Row(line) for line in credit_lines(self.story.company_credits) + [PORT_CREDIT]]
