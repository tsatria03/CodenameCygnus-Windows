"""A spoken menu: the shape of every menu screen in the game.

    Up and Down     move, each row spoken with its place: "Settings, 1 of 2"
    Home and End    the first row and the last
    Enter           choose the row
    Escape          go back
    any other key   say the row again

Each move cuts off what was being said, so fast arrowing never builds a backlog. Opening
the menu says its title, then its row without cutting the title off
(aidocks/plans/foundation_plan.md).
"""
from __future__ import annotations

from .screens import Screen


class Row:
    """One row: its text, which may change, and what Enter on it does."""

    def __init__(self, text, action=None):
        self._text = text
        self.action = action

    @property
    def text(self):
        return self._text() if callable(self._text) else self._text


class Menu(Screen):
    name = 'menu'
    title = ''

    def __init__(self, app):
        super().__init__(app)
        self.index = 0

    def rows(self):
        """The rows, worked out each time, so a row can come and go."""
        return []

    def row_text(self, i=None):
        rows = self.rows()
        if not rows:
            return 'Nothing here.'
        i = self.index if i is None else i
        return '%s, %d of %d' % (rows[i].text, i + 1, len(rows))

    def opened(self):
        self._clamp()
        if self.title:
            self.say(self.title)
            self.say(self.row_text(), interrupt=False)
        else:
            self.say(self.row_text())

    def _clamp(self):
        count = len(self.rows())
        self.index = min(self.index, max(0, count - 1))

    def move_to(self, i):
        rows = self.rows()
        if not rows:
            return
        self.index = i % len(rows)
        self.say(self.row_text())

    def back(self):
        """Escape: close this menu."""
        self.stack.pop()

    def handle_key(self, key, mods):
        if mods:
            return False
        rows = self.rows()
        if key == 'up':
            self.move_to(self.index - 1)
        elif key == 'down':
            self.move_to(self.index + 1)
        elif key == 'home':
            self.move_to(0)
        elif key == 'end':
            self.move_to(len(rows) - 1)
        elif key in ('return', 'enter'):
            self._clamp()
            if rows and rows[self.index].action is not None:
                rows[self.index].action()
        elif key == 'escape':
            self.back()
        else:
            self.say(self.row_text())
        return True

    def lines(self):
        out = [self.title, ''] if self.title else []
        for i, row in enumerate(self.rows()):
            out.append('%s %s' % ('>' if i == self.index else ' ', row.text))
        return out
