"""The safe JSON files: written whole, backed up, and damaged ones set aside."""
import _quiet  # noqa: F401  first, before any of the game

import json
import os
import tempfile

from codenamecygnus.platform.files import JsonFile


def folder():
    return tempfile.mkdtemp(dir=_quiet.FOLDER)


def test_a_new_file_starts_empty_and_is_written_whole():
    path = os.path.join(folder(), 'config', 'settings.json')
    f = JsonFile(path)
    assert f.data == {}
    f.data['a'] = 1
    assert f.write()
    with open(path, encoding='utf-8') as fh:
        assert json.load(fh) == {'a': 1}
    assert not os.path.exists(path + '.tmp')


def test_the_file_before_each_write_is_kept_as_bak():
    path = os.path.join(folder(), 'save.json')
    f = JsonFile(path)
    f.data['n'] = 1
    f.write()
    f.data['n'] = 2
    f.write()
    with open(path + '.bak', encoding='utf-8') as fh:
        assert json.load(fh) == {'n': 1}


def test_a_damaged_file_is_set_aside_and_the_backup_carries_on():
    path = os.path.join(folder(), 'save.json')
    f = JsonFile(path)
    f.data['n'] = 1
    f.write()
    f.data['n'] = 2
    f.write()
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write('{ not json')
    g = JsonFile(path)
    assert g.data == {'n': 1} and g.recovered
    assert os.path.exists(path + '.damaged')


def test_an_empty_file_counts_as_new():
    path = os.path.join(folder(), 'save.json')
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write('  \n')
    assert JsonFile(path).data == {}


def test_a_byte_order_mark_is_allowed():
    path = os.path.join(folder(), 'save.json')
    with open(path, 'w', encoding='utf-8-sig') as fh:
        fh.write('{"a": 1}')
    assert JsonFile(path).data == {'a': 1}


def test_keys_are_written_in_the_order_given():
    path = os.path.join(folder(), 'save.json')
    f = JsonFile(path, order=['z', 'a'])
    f.data = {'a': 1, 'b': 2, 'z': 3}
    f.write()
    with open(path, encoding='utf-8') as fh:
        assert list(json.load(fh)) == ['z', 'a', 'b']


if __name__ == '__main__':
    _quiet.run_tests(globals())
