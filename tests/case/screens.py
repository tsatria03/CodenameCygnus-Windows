"""The spoken menus, the F1 key bindings screen and the Settings screen, by what they say."""
import _quiet  # noqa: F401  first, before any of the game

import os
import tempfile
import types

from codenamecygnus import paths
from codenamecygnus.app import App
from codenamecygnus.platform.keymap import KeyMap
from codenamecygnus.platform.runloop import RunLoop
from codenamecygnus.platform.settings import Settings
from codenamecygnus.ui.keybind_screen import KeyBindScreen
from codenamecygnus.ui.menu import Menu, Row
from codenamecygnus.ui.settings_screen import SettingsScreen


class Ear:
    """Stands in for the screen reader, and remembers what it was told."""

    def __init__(self):
        self.heard = []
        self.last = ''

    def speak(self, text, interrupt=True):
        self.heard.append((text, interrupt))
        self.last = text
        return True

    @property
    def said(self):
        return [t for t, _i in self.heard]


def make_app(debug=False):
    folder = tempfile.mkdtemp(dir=_quiet.FOLDER)
    options = types.SimpleNamespace(debug=debug, episode=None, state=None, verbose=False, exit_after=None)
    return App(options, speech=Ear(),
               settings=Settings(os.path.join(folder, 'settings.json')),
               keymap=KeyMap(os.path.join(folder, 'keys.json')), loop=RunLoop())


class TwoRows(Menu):
    title = 'Test menu.'

    def __init__(self, app):
        super().__init__(app)
        self.chosen = []

    def rows(self):
        return [Row('First', lambda: self.chosen.append(1)), Row('Second', lambda: self.chosen.append(2))]


def test_a_menu_says_its_title_then_its_row_without_cutting_the_title_off():
    app = make_app()
    app.stack.push(TwoRows(app))
    assert app.speech.heard == [('Test menu.', True), ('First', False)]


def test_moving_says_each_row_without_its_place_and_cuts_off():
    app = make_app()
    menu = TwoRows(app)
    app.stack.push(menu)
    menu.handle_key('down', [])
    menu.handle_key('down', [])                     # wraps round
    menu.handle_key('end', [])
    menu.handle_key('home', [])
    assert app.speech.heard[2:] == [('Second', True), ('First', True),
                                    ('Second', True), ('First', True)]


def test_enter_chooses_and_escape_goes_back():
    app = make_app()
    app.stack.push(TwoRows(app))
    menu = TwoRows(app)
    app.stack.push(menu)
    menu.handle_key('down', [])
    menu.handle_key('return', [])
    assert menu.chosen == [2]
    menu.handle_key('escape', [])
    assert app.stack.top is not menu and len(app.stack.screens) == 1


def test_any_other_key_says_the_row_again():
    app = make_app()
    menu = TwoRows(app)
    app.stack.push(menu)
    menu.handle_key('x', [])
    assert app.speech.said[-1] == 'First'


def test_f1_opens_the_key_bindings_and_holds_the_timers_until_it_closes():
    app = make_app()
    app.stack.push(TwoRows(app))
    app.key_down('f1', [])
    assert isinstance(app.stack.top, KeyBindScreen) and app.loop.held
    assert app.speech.said[-2].startswith('Key bindings.')
    app.key_down('escape', [])
    assert not isinstance(app.stack.top, KeyBindScreen) and not app.loop.held


def test_rebinding_on_the_f1_screen_takes_the_next_key_with_its_modifiers():
    app = make_app()
    app.stack.push(TwoRows(app))
    app.key_down('f1', [])
    screen = app.stack.top
    while screen.action != 'heading':
        screen.handle_key('down', [])
    screen.handle_key('return', [])
    screen.handle_key('left shift', ['shift'])      # a modifier alone waits
    screen.handle_key('j', ['shift'])
    assert app.keymap.action_for('j', ['shift']) == 'heading'
    assert app.speech.said[-1] == 'Say where you are is now Shift plus J.'


def test_escape_f1_and_the_number_keys_cannot_be_rebound():
    app = make_app()
    app.key_down('f1', [])
    screen = app.stack.top
    for key in ('escape', 'f1', '3'):
        screen.handle_key('return', [])
        screen.handle_key(key, [])
        assert 'cannot be rebound' in app.speech.said[-1], (key, app.speech.said[-1])


def test_reset_asks_first_and_r_again_does_it():
    app = make_app()
    app.key_down('f1', [])
    screen = app.stack.top
    app.keymap.clear('pause')
    screen.handle_key('r', [])
    screen.handle_key('x', [])
    assert app.keymap.action_for('space') is None
    screen.handle_key('r', [])
    screen.handle_key('r', [])
    assert app.keymap.action_for('space') == 'pause'


def test_the_settings_screen_turns_debug_mode_on_and_remembers_it():
    app = make_app()
    settings = SettingsScreen(app)
    app.stack.push(settings)
    settings.handle_key('down', [])
    assert app.speech.said[-1] == 'Debug mode, currently off'
    settings.handle_key('return', [])
    assert app.debug and app.keymap.debug and app.settings.get('debug') is True
    assert app.speech.said[-1] == 'Debug mode, currently on'


def test_debug_mode_is_never_on_in_a_built_game():
    frozen = paths.FROZEN
    paths.FROZEN = True
    try:
        app = make_app(debug=True)
        assert not app.debug and not app.keymap.debug
        assert [r.text for r in SettingsScreen(app).rows()] == ['Back']
    finally:
        paths.FROZEN = frozen


def test_debug_on_the_command_line_lasts_one_run():
    app = make_app(debug=True)
    assert app.debug and app.settings.get('debug') is False


if __name__ == '__main__':
    _quiet.run_tests(globals())
