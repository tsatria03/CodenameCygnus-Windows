"""A spoken menu: the shape of every menu screen in the game.

    Up and Down     move, each row spoken by its text alone, such as "Settings"
    Left and Right  the same as Up and Down
    Home and End    the first row and the last
    Enter           choose the row
    Escape          go back
    any other key   say the row again

Each move cuts off what was being said, so fast arrowing never builds a backlog. Opening
the menu says its title, then its row without cutting the title off
(aidocks/plans/foundation_plan.md). Rows are not read with their place, such as "1 of 2"
(the dev, 2026-10-17: "The menu position readouts should be disabled"). Moving past the
last row wraps round to the first, and past the first to the last, and Left and Right move
as Up and Down do (the dev, 2026-10-17: "please enable menu wrapping, and left/right arrow
navigation").
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
        return rows[i].text

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
        """Escape: close this menu, with the original's back sound."""
        self.app.play_sound('back')
        self.stack.pop()

    def open(self, screen, sound='open'):
        """Open another screen on top, with its interface sound."""
        self.app.play_sound(sound)
        self.stack.push(screen)

    def handle_key(self, key, mods):
        if mods:
            return False
        rows = self.rows()
        if key in ('up', 'left'):
            self.move_to(self.index - 1)
        elif key in ('down', 'right'):
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
