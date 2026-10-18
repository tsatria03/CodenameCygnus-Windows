"""Debug mode's screens and report: section 4 of aidocks/plans/story_engine_plan.md.

Debug mode is for source runs only (aidocks/plans/foundation_plan.md), and its keys are
on F2 to F4 so they never clash with the story's:

    F2  skip the recording, heard or not, never marking it heard (episode_screen.py)
    F3  jump to any state: type or paste part of its name, then Enter
    F4  the state's name, the four trait scores and every story flag that is set

F3's names are the ones in analysis/script/, so a state found there can be jumped to.
"""
from __future__ import annotations

from ..platform.clipboard import Clipboard
from ..ui.menu import Menu, Row
from ..ui.screens import Screen
from .story import TRAITS

#: More matches than this, and the search asks for more of the name.
MOST_MATCHES = 40


def state_report(run):
    """F4: "State 016F_contactMark. Openness 1, ... Flags: event.m1e1_cardsWin 1, ..."."""
    traits = ', '.join('%s %d' % (t, run.trait(t)) for t in TRAITS)
    flags = sorted((k, v) for k, v in run.variables.items() if k not in TRAITS)
    flag_text = ', '.join('%s %d' % kv for kv in flags) if flags else 'none'
    return 'State %s. %s. Flags: %s.' % (run.current.name, traits, flag_text)


def matches(story, query):
    """The state names holding ``query``, in any letter case; an exact name alone if one
    is exact."""
    q = query.lower()
    exact = [n for n in story.states if n.lower() == q]
    if exact:
        return exact
    return sorted(n for n in story.states if q in n.lower())


class JumpScreen(Screen):
    """F3: type part of a state's name, Enter to jump, Escape to go back to the story.

    Ctrl+V pastes a name, such as one copied from analysis/script/ or given to try; Ctrl+C
    copies what is typed and Ctrl+X cuts it (the dev, 2026-10-18: "add the ability to
    cut/copy/paste in the input prompt so I don't have to hand type the states")."""

    name = 'debug jump'

    def __init__(self, app, episode_screen, clipboard=None):
        super().__init__(app)
        self.episode_screen = episode_screen
        self.clipboard = clipboard if clipboard is not None else Clipboard()
        self.query = ''

    def opened(self):
        if self.query:
            self.say('Jump to a state. %s' % self.query)
        else:
            self.say('Jump to a state. Type part of its name, then Enter.')

    def handle_key(self, key, mods):
        if key == 'escape' and not mods:
            self.stack.pop()
            self.say('Canceled.')       # the dev, 2026-10-18: "pressing escape ... should say canceled"
        elif key in ('return', 'enter') and not mods:
            self.search()
        elif key == 'backspace' and not mods:
            if self.query:
                gone, self.query = self.query[-1], self.query[:-1]
                self.say(gone)
        elif mods == ['ctrl'] and key in ('v', 'c', 'x'):
            {'v': self.paste, 'c': self.copy, 'x': self.cut}[key]()
        elif key == '-' and mods == ['shift']:
            self.type('_')
        elif len(key) == 1 and key.isalnum() and mods in ([], ['shift']):
            self.type(key.upper() if mods else key)
        else:
            self.say(self.query or 'Nothing typed yet.')
        return True

    def type(self, char):
        self.query += char
        self.say(char)

    def paste(self):
        """Add the clipboard's text, its first line only and without spaces around it, so
        a name copied with its line ending or a "State: " before it still matches."""
        text = self.clipboard.get_text().strip().splitlines()
        text = text[0].strip() if text else ''
        if text.lower().startswith('state:'):
            text = text[len('state:'):].strip()
        if not text:
            return self.say('The clipboard has no text.')
        self.query += text
        self.say('Pasted %s' % text)

    def copy(self):
        if not self.query:
            return self.say('Nothing typed yet.')
        if self.clipboard.set_text(self.query):
            self.say('Copied %s' % self.query)
        else:
            self.say('Could not copy.')

    def cut(self):
        if not self.query:
            return self.say('Nothing typed yet.')
        if self.clipboard.set_text(self.query):
            self.say('Cut %s' % self.query)
            self.query = ''
        else:
            self.say('Could not cut.')

    def search(self):
        if not self.query:
            return self.say('Nothing typed yet.')
        found = matches(self.episode_screen.story, self.query)
        if not found:
            self.say('No state has %s in its name.' % self.query)
        elif len(found) == 1:
            self.stack.pop()
            self.episode_screen.jump(found[0])
        elif len(found) > MOST_MATCHES:
            self.say('%d states match. Type more of the name.' % len(found))
        else:
            self.stack.push(MatchMenu(self.app, self, found))

    def lines(self):
        return ['Jump to a state', '', 'Name: ' + self.query]


class MatchMenu(Menu):
    """The states a search found; Enter jumps, Escape goes back to the search."""

    name = 'debug matches'

    def __init__(self, app, jump_screen, names):
        super().__init__(app)
        self.jump_screen = jump_screen
        self.names = names
        self.title = '%d states match.' % len(names)

    def rows(self):
        return [Row(n, lambda n=n: self.jump(n)) for n in self.names]

    def jump(self, name):
        self.stack.pop()                    # this list
        self.stack.pop()                    # the search
        self.jump_screen.episode_screen.jump(name)
