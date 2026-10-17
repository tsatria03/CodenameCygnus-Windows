"""The settings file: every setting written from the first start, and bad values put back."""
import _quiet  # noqa: F401  first, before any of the game

import json
import os
import tempfile

from codenamecygnus.platform.settings import DEFAULTS, Settings


def path():
    return os.path.join(tempfile.mkdtemp(dir=_quiet.FOLDER), 'config', 'settings.json')


def test_every_setting_is_written_at_its_default_on_the_first_start():
    p = path()
    Settings(p)
    with open(p, encoding='utf-8') as fh:
        saved = json.load(fh)
    assert saved == DEFAULTS
    assert list(saved) == list(DEFAULTS)


def test_speech_recognition_starts_off():
    assert Settings(path()).get('speech_recognition') is False


def test_a_value_the_game_cannot_use_is_put_back():
    p = path()
    os.makedirs(os.path.dirname(p))
    with open(p, 'w', encoding='utf-8') as fh:
        json.dump({'master_volume': 55, 'ambience_volume': 'loud', 'debug': 1}, fh)
    s = Settings(p)
    assert s.get('master_volume') == 100
    assert s.get('ambience_volume') == 100
    assert s.get('debug') is False


def test_a_good_value_is_kept():
    p = path()
    Settings(p).set('decision_volume', 40)
    assert Settings(p).get('decision_volume') == 40


def test_set_refuses_a_bad_value():
    s = Settings(path())
    for key, value in (('master_volume', 105), ('master_volume', 33), ('debug', 'yes')):
        try:
            s.set(key, value)
        except ValueError:
            continue
        raise AssertionError('%s accepted %r' % (key, value))


def test_toggle_turns_a_setting_over_and_remembers_it():
    p = path()
    s = Settings(p)
    assert s.toggle('speech_recognition') is True
    assert Settings(p).get('speech_recognition') is True


def test_a_setting_the_game_no_longer_knows_is_left_alone():
    p = path()
    os.makedirs(os.path.dirname(p))
    with open(p, 'w', encoding='utf-8') as fh:
        json.dump({'something_old': 3}, fh)
    Settings(p)
    with open(p, encoding='utf-8') as fh:
        assert json.load(fh)['something_old'] == 3


if __name__ == '__main__':
    _quiet.run_tests(globals())
