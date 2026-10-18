"""Finding a recording by its story name, in a folder made for the test."""
import _quiet  # noqa: F401  first, before any of the game

import os
import tempfile

from codenamecygnus.game.recordings import Recordings, story_key


def tree(files):
    root = tempfile.mkdtemp(dir=_quiet.FOLDER)
    for rel in files:
        path = os.path.join(root, *rel.split('/'))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(b'\xff\xfb')
    return root


def test_a_story_name_is_found_as_its_mp3_in_any_folder():
    r = Recordings(tree(['missions/m1/episodes/e2/p2/016F_contactMark.mp3',
                         'missions/m1/sources/back_bar.mp3']))
    found = r.find('016F_contactMark.m4a')
    assert found is not None and found.path.endswith('016F_contactMark.mp3')
    assert r.find('back_bar.m4a').path.endswith(os.path.join('sources', 'back_bar.mp3'))


def test_letter_case_does_not_matter():
    r = Recordings(tree(['others/interface/1930Radio A.mp3']))
    assert r.menu_sound('1930radio a') is not None
    assert r.find('1930RADIO A.m4a') is not None


def test_a_preview_is_found_without_teaser():
    r = Recordings(tree(['missions/m1/teasers/m1e2.mp3']))
    assert story_key('m1e2_teaser.m4a') == 'm1e2'
    assert r.find('m1e2_teaser.m4a').path.endswith(os.path.join('teasers', 'm1e2.mp3'))


def test_a_missing_recording_is_none():
    assert Recordings(tree(['others/interface/Buy.mp3'])).find('nowhere.m4a') is None


def test_a_name_found_twice_takes_the_first_and_says_so():
    r = Recordings(tree(['a/same.mp3', 'b/same.mp3']))
    assert r.find('same.m4a').path.endswith(os.path.join('a', 'same.mp3'))
    assert 'same' in r.twice


def test_the_real_audio_folder_has_the_menu_sounds():
    r = Recordings()
    for name in ('1930Radio A', '1930Radio B', '1930Radio C', 'PushButton D', 'Sound A'):
        assert r.menu_sound(name) is not None, name


if __name__ == '__main__':
    _quiet.run_tests(globals())
