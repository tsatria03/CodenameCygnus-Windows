"""The main loop, the options, the logs and the crash file, on SDL's dummy window."""
import _quiet  # noqa: F401  first, before any of the game

import importlib.util
import os
import types

import pygame

from codenamecygnus import paths
from codenamecygnus.app import App
from codenamecygnus.game.stand_in_menu import StandInMainMenu
from codenamecygnus.platform.keymap import KeyMap
from codenamecygnus.platform.runloop import RunLoop
from codenamecygnus.platform.settings import Settings

ENTRY = os.path.join(_quiet.ROOT, 'CodenameCygnus.py')


def entry():
    spec = importlib.util.spec_from_file_location('cygnus_entry', ENTRY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Ear:
    def __init__(self):
        self.said = []
        self.last = ''

    def speak(self, text, interrupt=True):
        self.said.append(text)
        self.last = text
        return True


def test_the_options_are_read():
    o = entry().parse_args(['--debug', '--episode', '1.3.1', '--state', 'm1e3_start', '-v',
                            '--exit-after', '2.5'])
    assert o.debug and o.episode == '1.3.1' and o.state == 'm1e3_start' and o.verbose
    assert o.exit_after == 2.5


def test_the_game_runs_and_quits_by_itself_after_exit_after():
    options = types.SimpleNamespace(debug=False, episode=None, state=None, verbose=False,
                                    exit_after=0.3)
    app = App(options, speech=Ear(), settings=Settings(paths.user_path('a', 'settings.json')),
              keymap=KeyMap(paths.user_path('a', 'keys.json')), loop=RunLoop())
    app.run(StandInMainMenu(app), pygame)
    assert not app.running
    assert app.speech.said[:2] == ['Codename Cygnus. Main menu.', 'Episodes']


def test_quit_on_the_stand_in_menu_ends_the_game():
    options = types.SimpleNamespace(debug=False, episode=None, state=None, verbose=False, exit_after=None)
    app = App(options, speech=Ear(), settings=Settings(paths.user_path('b', 'settings.json')),
              keymap=KeyMap(paths.user_path('b', 'keys.json')), loop=RunLoop())
    menu = StandInMainMenu(app)
    app.stack.push(menu)
    menu.handle_key('end', [])
    assert app.speech.said[-1] == 'Quit'
    menu.handle_key('return', [])
    assert not app.running


def test_each_run_keeps_the_run_before_as_log_old():
    e = entry()
    folder = paths.logs_dir()
    with open(os.path.join(folder, 'log.txt'), 'w', encoding='utf-8') as fh:
        fh.write('the run before\n')
    import logging
    e.start_log(False)
    logging.getLogger('test').info('this run')
    for h in list(logging.getLogger().handlers):
        h.close()
        logging.getLogger().removeHandler(h)
    with open(os.path.join(folder, 'log.old.txt'), encoding='utf-8') as fh:
        assert fh.read() == 'the run before\n'
    with open(os.path.join(folder, 'log.txt'), encoding='utf-8') as fh:
        assert 'this run' in fh.read()


def test_an_error_writes_crash_txt():
    e = entry()
    path = e.write_crash('Traceback: something broke\n')
    assert path == os.path.join(paths.logs_dir(), 'crash.txt')
    with open(path, encoding='utf-8') as fh:
        text = fh.read()
    assert text.startswith('Codename Cygnus stopped because of an error.')
    assert 'something broke' in text and 'Running from: source' in text


if __name__ == '__main__':
    _quiet.run_tests(globals())
