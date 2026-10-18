"""The end of an episode, its credits, and the previews: section 3 of
aidocks/plans/menus_plan.md.

When an episode's end state has played, the episode screen says "Episode complete!", the
episode's completion text and any achievements earned, then opens ``EndMenu``:

    Back                    to the menu the episode was started from
    Next episode, Art Show  the episode this one opens, the story so far carried on
    Preview next episode    the next episode's teaser, as the original's PREVIEW NEXT
    Credits                 this episode's credits, one row each

A row with nothing behind it is left out: Signum Cygni and Holiday Party have no next
episode, and so no preview. Back takes the plan's "Return to menu" row's place, since Back
is first in every menu and the two would do the same (aidocks/general/feedback_back_first.md).

A preview (``PreviewScreen``) plays the teaser's recording alone and comes back when it
ends; Enter or Escape stops it, and Space pauses it.
"""
from __future__ import annotations

import logging

from ..ui.menu import Menu, Row
from ..ui.screens import Screen

log = logging.getLogger('episode end')


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


class CreditList(Menu):
    """A list of credits, Back first."""

    name = 'credits'

    def __init__(self, app, title, credits, last=()):
        super().__init__(app)
        self.title = title
        self.lines = credit_lines(credits) + list(last)

    def rows(self):
        return [Row('Back', self.back)] + [Row(line) for line in self.lines]


class PreviewScreen(Screen):
    """The next episode's teaser, heard alone."""

    name = 'preview'

    def __init__(self, app, story, episode, recordings=None):
        super().__init__(app)
        from .recordings import Recordings
        self.story = story
        self.next = story.next_episode(episode)
        self.state = story.states.get(episode.preview)
        self.recordings = recordings or Recordings.shared()
        self.started = False
        self.paused = False

    def opened(self):
        if self.started:
            return
        self.started = True
        self.say('Preview of %s.' % (self.next.title if self.next else 'the next episode'))
        audio = self.app.audio
        audio.resume()                  # the episode under it may have been paused
        audio.stop_decision()
        audio.set_background(None)
        voice = self.state.voice if self.state is not None else None
        audio.play_voice(self.recordings.find(voice) if voice else None, on_end=self.ended)

    def ended(self):
        if self.stack.top is self:
            self.stack.pop()

    def closed(self):
        self.app.audio.stop_voice()
        if self.paused:
            self.app.audio.resume()

    def handle_key(self, key, mods):
        if key in ('escape', 'return', 'enter') and not mods:
            self.app.play_sound('back')
            self.stack.pop()
        elif key == 'space' and not mods:
            self.paused = not self.paused
            if self.paused:
                self.app.audio.pause()
                self.say('Paused.')
            else:
                self.app.audio.resume()
                self.say('Resumed.')
        return True

    def lines(self):
        return ['Preview of %s' % (self.next.title if self.next else 'the next episode'),
                '', '(paused)' if self.paused else '']


class EndMenu(Menu):
    """What comes after "Episode complete!"."""

    name = 'end of episode'
    title = 'Episode complete.'

    def __init__(self, app, episode_screen):
        super().__init__(app)
        self.episode_screen = episode_screen
        self.episode = episode_screen.episode
        self.story = episode_screen.story
        self.next = self.story.next_episode(self.episode)
        self.first = True

    def opened(self):
        if self.first:
            # Behind the completion text and the achievements, which nothing cuts off but
            # a key the player presses.
            self.first = False
            self.say(self.row_text(), interrupt=False)
        else:
            super().opened()

    def rows(self):
        rows = [Row('Back', self.back)]
        if self.next is not None:
            rows.append(Row('Next episode, %s' % self.next.title, self.next_episode))
        if self.episode.preview and self.episode.preview in self.story.states:
            rows.append(Row('Preview next episode', lambda: self.open(
                PreviewScreen(self.app, self.story, self.episode,
                              recordings=self.episode_screen.recordings))))
        if self.episode.credits:
            rows.append(Row('Credits', lambda: self.open(
                CreditList(self.app, 'Credits. %s.' % self.episode.title, self.episode.credits),
                'credits')))
        return rows

    def back(self):
        """Back to the menu the episode was started from."""
        self.app.play_sound('back')
        self.stack.pop()
        self.episode_screen.leave()

    def next_episode(self):
        self.app.play_sound('play')
        self.stack.pop()
        self.episode_screen.start_next(self.next)

    def lines(self):
        return ['Episode complete!', self.episode.completion_text.strip(), ''] + super().lines()[2:]
