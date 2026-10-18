"""The key map: the agreed defaults, exact modifiers, rebinding and the keys file."""
import _quiet  # noqa: F401  first, before any of the game

import json
import os
import tempfile

from codenamecygnus.platform.keymap import ACTION_IDS, KeyMap, binding, binding_text


def path():
    return os.path.join(tempfile.mkdtemp(dir=_quiet.FOLDER), 'config', 'keys.json')


def test_the_agreed_keys_are_the_defaults():
    k = KeyMap(path())
    expected = {
        'up': 'previous_choice', 'down': 'next_choice', 'return': 'choose', 'c': 'repeat_choices',
        'p': 'pause_menu', 'r': 'replay', 'left': 'back', 'right': 'forward', 's': 'skip',
        'h': 'heading', 'v': 'speech_recognition', 'page up': 'ambience_up',
        'page down': 'ambience_down',
    }
    for key, action in expected.items():
        assert k.action_for(key) == action, (key, k.action_for(key))
    assert k.action_for('home', ['shift']) == 'master_up'
    assert k.action_for('end', ['shift']) == 'master_down'
    assert k.action_for('page up', ['shift']) == 'decision_up'
    assert k.action_for('page down', ['shift']) == 'decision_down'


def test_modifiers_must_match_exactly():
    k = KeyMap(path())
    assert k.action_for('home') is None             # plain Home is for menus
    assert k.action_for('page up', ['ctrl']) is None
    assert k.action_for('page up', ['shift', 'ctrl']) is None


def test_debug_keys_work_only_in_debug_mode():
    k = KeyMap(path())
    assert k.action_for('f2') is None and 'debug_skip' not in k.actions
    k.debug = True
    assert k.action_for('f2') == 'debug_skip'
    assert k.action_for('f3') == 'debug_jump'
    assert k.action_for('f4') == 'debug_state'


def test_binding_names_modifiers_first():
    assert binding('page up', ['shift']) == 'shift+page up'
    assert binding('h', ['alt', 'shift']) == 'shift+alt+h'
    assert binding_text('shift+page up') == 'Shift plus Page Up'


def test_rebinding_takes_the_key_off_whatever_had_it():
    p = path()
    k = KeyMap(p)
    k.set_binding('heading', 'c')
    assert k.action_for('c') == 'heading'
    assert k.bindings['repeat_choices'] == []
    assert KeyMap(p).action_for('c') == 'heading'


def test_a_second_key_can_be_added():
    k = KeyMap(path())
    k.set_binding('replay', 'p', replace=False)
    assert k.action_for('p') == 'replay' and k.action_for('r') == 'replay'


def test_every_action_is_in_the_keys_file_from_the_first_start():
    p = path()
    KeyMap(p)
    with open(p, encoding='utf-8') as fh:
        assert list(json.load(fh)) == ACTION_IDS


def test_reset_puts_every_key_back():
    k = KeyMap(path())
    k.clear('replay')
    k.reset()
    assert k.action_for('r') == 'replay'


def test_there_is_no_pause_key_and_an_old_one_is_dropped():
    p = path()
    os.makedirs(os.path.dirname(p))
    with open(p, 'w', encoding='utf-8') as fh:
        json.dump({'pause': ['space'], 'replay': ['r']}, fh)
    k = KeyMap(p)
    assert k.action_for('space') is None and 'pause' not in k.actions
    assert k.action_for('p') == 'pause_menu', 'the new action took the old binding'
    k.save()
    with open(p, encoding='utf-8') as fh:
        assert 'pause' not in json.load(fh)


def test_a_damaged_keys_file_falls_back_on_its_backup():
    p = path()
    k = KeyMap(p)
    k.set_binding('heading', 'j')
    k.set_binding('replay', 'k')            # the backup now holds heading on J
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write('[broken')
    again = KeyMap(p)
    assert again.action_for('j') == 'heading'
    assert os.path.exists(p + '.damaged')


if __name__ == '__main__':
    _quiet.run_tests(globals())
