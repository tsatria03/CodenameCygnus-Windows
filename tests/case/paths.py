"""Where things are, and that every test keeps off the real save."""
import _quiet  # noqa: F401  first, before any of the game

import glob
import os

from codenamecygnus import paths

HERE = os.path.dirname(os.path.abspath(__file__))


def test_the_save_folder_is_the_tests_own():
    assert paths.user_dir() == _quiet.FOLDER
    assert paths.user_path('config', 'settings.json').startswith(_quiet.FOLDER)


def test_every_test_file_keeps_off_the_real_save():
    for path in glob.glob(os.path.join(HERE, '*.py')):
        if os.path.basename(path).startswith('_'):
            continue
        with open(path, encoding='utf-8') as fh:
            head = fh.read(2000)
        assert '\nimport _quiet' in head or head.startswith('import _quiet'), \
            '%s does not import _quiet first' % os.path.basename(path)


def test_the_quiet_settings_are_in_force():
    for key, value in _quiet.QUIET.items():
        assert os.environ.get(key) == value, key


def test_the_game_data_is_found_from_source():
    assert os.path.isdir(paths.text())
    assert os.path.isfile(os.path.join(paths.text(), 'states.json'))
    assert os.path.isdir(os.path.join(paths.audio(), 'others', 'menu'))


def test_the_nvda_client_is_where_speech_looks_for_it():
    assert os.path.isfile(paths.NVDA_DLL)


if __name__ == '__main__':
    _quiet.run_tests(globals())
