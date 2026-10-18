"""The screens around the story: section 1 of aidocks/plans/menus_plan.md.

    the opening      "Codename Cygnus" and one of the original's loading messages, then
                     the first time only, the headphones notice
    the main menu    Episodes, Settings, Credits, Quit; Escape quits too
    Episodes         Mission 1's episodes, each by its number and title; Enter opens its
                     own screen, which says its description and offers Start and, where
                     there is one, Preview next episode
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
from .episode_end import PreviewScreen, credit_lines
from .episode_screen import EpisodeScreen, RestartQuestion
from .progress import IN_PROGRESS, NEW, Progress
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

    def __init__(self, app, story=None, progress=None):
        super().__init__(app)
        self.story = story or Story.shared()
        self.progress = progress if progress is not None else Progress.shared(self.story)

    def rows(self):
        rows = []
        going = self.progress.continue_episode()
        if going is not None:
            # First, so one Enter after starting the game gets back into the story.
            rows.append(Row('Continue %s' % going.title,
                            lambda: self.app.stack.push(continue_screen(self.app, self.story,
                                                                        self.progress, going))))
        return rows + [
            Row('Episodes', lambda: self.open(EpisodeList(self.app, self.story, self.progress),
                                              'episodes')),
            Row('Settings', lambda: self.open(SettingsScreen(self.app))),
            Row('Credits', lambda: self.open(CreditsScreen(self.app, self.story), 'credits')),
            Row('Quit', self.app.quit)]

    def back(self):
        """Escape on the main menu quits, as Quit does."""
        self.app.quit()


def continue_screen(app, story, progress, episode):
    """The episode, at the start of the state it was left in, with the variables then."""
    app.play_sound('play')
    state, variables = progress.place(episode)
    return EpisodeScreen(app, episode, story=story, variables=variables, at=state,
                         progress=progress)


def episode_name(episode):
    """ "Episode 2, Art Show" """
    return 'Episode %d, %s' % (episode.number, episode.title)


#: What the Locked row says when chosen, as the original's "Episode Locked" alert did.
LOCKED = 'You need to complete the previous episode before starting this one.'


class EpisodeList(Menu):
    """Mission 1's episodes, each with its state. Its old description, written for selling
    episodes, and Mission 2, never released, are left out."""

    name = 'episodes'
    title = 'Episodes. Mission 1.'

    def __init__(self, app, story, progress=None):
        super().__init__(app)
        self.story = story
        self.progress = progress if progress is not None else Progress.shared(story)

    def row_name(self, episode):
        """ "Episode 2, Art Show, in progress"; a new one by its name alone."""
        if self.progress.locked(episode):
            return '%s, locked' % episode_name(episode)
        state = self.progress.state_of(episode)
        return episode_name(episode) if state == NEW else '%s, %s' % (episode_name(episode), state)

    def rows(self):
        # Back at the top, as in every menu (the dev, 2026-10-18: "There should also bee a
        # back button in the episode list, at the top of the screen", and "The back button
        # should always appear first in any menu").
        return [Row('Back', self.back)] + [
            Row(lambda e=e: self.row_name(e),
                lambda e=e: self.open(EpisodeMenu(self.app, self.story, e, self.progress)))
            for e in self.story.playable_episodes()]


class EpisodeMenu(Menu):
    """One episode's own screen: Back, its description as a row of its own, then what can
    be done with it by its state, as the original's two buttons were
    (aidocks/plans/saves_plan.md):

        not started   Start
        in progress   Continue, Restart episode
        completed     Replay episode, Preview next episode
        locked        Locked, which says why when chosen (the dev, 2026-10-18: "For locked
                      episodes, a similar menu should open with the back button,
                      description, then the locked status after it")
    """

    name = 'episode menu'

    def __init__(self, app, story, episode, progress=None):
        super().__init__(app)
        self.story = story
        self.episode = episode
        self.progress = progress if progress is not None else Progress.shared(story)
        self.title = '%s.' % episode_name(episode)

    def rows(self):
        rows = [Row('Back', self.back)]
        description = self.episode.description.strip()
        if description:
            rows.append(Row(description, lambda: self.say(self.row_text())))
        state = self.progress.state_of(self.episode)
        if self.progress.locked(self.episode):
            rows.append(Row('Locked', lambda: self.say(LOCKED)))
        elif state == NEW:
            rows.append(Row('Start', self.start))
        elif state == IN_PROGRESS:
            if self.progress.place(self.episode) is not None:
                rows.append(Row('Continue', self.go_on))
            else:
                rows.append(Row('Start', self.start))
            rows.append(Row('Restart episode', self.ask_restart))
        else:
            rows.append(Row('Replay episode', self.ask_restart))
            if self.episode.preview and self.episode.preview in self.story.states:
                rows.append(Row('Preview next episode', lambda: self.open(
                    PreviewScreen(self.app, self.story, self.episode))))
        return rows

    def start(self):
        """The episode in this screen's place, so leaving it comes back to the list."""
        self.app.play_sound('play')
        self.stack.replace(EpisodeScreen(self.app, self.episode, story=self.story,
                                         variables=self.progress.start_variables(self.episode),
                                         progress=self.progress))

    def go_on(self):
        self.stack.replace(continue_screen(self.app, self.story, self.progress, self.episode))

    def ask_restart(self):
        self.app.play_sound('restart')
        self.stack.push(RestartQuestion(self.app, self.restart))

    def restart(self):
        """Restart or Replay: from the beginning, every later episode locked again."""
        began = self.progress.restart(self.episode)
        self.stack.replace(EpisodeScreen(self.app, self.episode, story=self.story,
                                         variables=began, progress=self.progress))
        self.say('Restarting %s.' % self.episode.title)


class CreditsScreen(Menu):
    """Reactive Studios' company credits, as the original's Info screen had them, and the
    port's line. Each episode's own credits come at its end (game/episode_end.py)."""

    name = 'credits'
    title = 'Credits.'
    #: A row of its own after Back, as an episode's description is (the dev, 2026-10-18:
    #: "Do the same with credits. Put the first part of that after the back button").
    INTRO = 'Codename Cygnus is a game by Reactive Studios.'

    def __init__(self, app, story):
        super().__init__(app)
        self.story = story

    def rows(self):
        return [Row('Back', self.back), Row(self.INTRO)] + [
            Row(line) for line in credit_lines(self.story.company_credits) + [PORT_CREDIT]]
