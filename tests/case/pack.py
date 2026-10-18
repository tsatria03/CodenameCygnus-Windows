"""The mission pack and its download, with made-up recordings and a stand-in for the network:
nothing is downloaded, and the real recordings are never packed."""
import _quiet  # noqa: F401  first, before any of the game

import io
import os
import tempfile

from episode import READY, STORY, key, make_app

from codenamecygnus.app import SOUNDS
from codenamecygnus.game import download as downloads
from codenamecygnus.game import pack as packs
from codenamecygnus.game.download import Download, DownloadScreen
from codenamecygnus.game.menus import EpisodeMenu, MainMenu
from codenamecygnus.game.progress import Progress
from codenamecygnus.game.recordings import Recordings

RECORDINGS = {os.path.join('episodes', 'e1', '001A_Intro.mp3'): b'ID3 first voice' * 50,
              os.path.join('sources', 'back_casino.mp3'): b'a background' * 80,
              os.path.join('teasers', 'm1e2.mp3'): b'a preview'}


def folder():
    return tempfile.mkdtemp(dir=_quiet.FOLDER)


def source():
    """A made-up missions/m1 folder."""
    root = folder()
    for rel, data in RECORDINGS.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)
    return root


def built():
    dest = os.path.join(folder(), 'm1.dat')
    assert packs.write_pack(source(), dest) == 3
    return dest


def test_a_pack_gives_back_every_recording_by_its_key():
    pack = packs.Pack(built())
    assert sorted(pack.keys()) == ['001a_intro', 'back_casino', 'm1e2']
    assert pack.read('back_casino') == RECORDINGS[os.path.join('sources', 'back_casino.mp3')]
    assert pack.read('m1e2') == b'a preview'


def test_a_pack_hides_its_recordings_and_index():
    with open(built(), 'rb') as f:
        data = f.read()
    assert data.startswith(packs.MAGIC)
    assert b'first voice' not in data and b'back_casino' not in data


def test_a_damaged_recording_or_a_file_that_is_no_pack_is_refused():
    path = built()
    pack = packs.Pack(path)
    offset, _length = pack.index['001a_intro']
    with open(path, 'r+b') as f:
        f.seek(pack.start + offset + packs.NONCE + 3)
        byte = f.read(1)
        f.seek(-1, 1)
        f.write(bytes([byte[0] ^ 1]))
    try:
        pack.read('001a_intro')
        raise AssertionError('a damaged recording was read')
    except packs.PackError:
        pass
    other = os.path.join(folder(), 'm1.dat')
    with open(other, 'wb') as f:
        f.write(b'not a pack at all')
    try:
        packs.Pack(other)
        raise AssertionError('a file that is no pack was opened')
    except packs.PackError:
        pass


def test_the_info_holds_the_size_and_fingerprint():
    path = built()
    info_file = os.path.join(folder(), 'm1_pack.json')
    info = packs.write_info(path, info_file)
    assert packs.read_info(info_file) == info
    assert info['size'] == os.path.getsize(path) and len(info['sha256']) == 64
    assert info['url'].endswith('/releases/download/mission-1/m1.dat')


def audio_folder(loose_missions):
    """A game/data/audio with the menu sounds, and the missions too if asked."""
    root = folder()
    menu = os.path.join(root, 'others', 'interface')
    os.makedirs(menu)
    with open(os.path.join(menu, 'Sound A.mp3'), 'wb') as f:
        f.write(b'menu')
    if loose_missions:
        path = os.path.join(root, 'missions', 'm1', 'episodes', 'e1', '001A_Intro.mp3')
        os.makedirs(os.path.dirname(path))
        with open(path, 'wb') as f:
            f.write(b'loose voice')
    return root


def test_with_no_loose_missions_the_recordings_come_from_the_pack():
    recordings = Recordings(audio_folder(False), pack=packs.Pack(built()))
    assert recordings.has_missions and recordings.loose_missions == 0
    voice = recordings.find('001A_Intro.m4a')
    assert voice.data == RECORDINGS[os.path.join('episodes', 'e1', '001A_Intro.mp3')]
    assert recordings.find('m1e2_teaser').data == b'a preview'
    assert recordings.menu_sound('Sound A').path.endswith('Sound A.mp3')


def test_loose_missions_win_and_none_at_all_means_nothing_to_play():
    loose = Recordings(audio_folder(True), pack=packs.Pack(built()))
    assert loose.pack is None and loose.find('001A_Intro.m4a').path.endswith('001A_Intro.mp3')
    empty = Recordings(audio_folder(False), pack=None)
    assert not empty.has_missions and empty.find('001A_Intro.m4a') is None


def test_a_pack_of_the_wrong_size_is_not_used():
    path = built()
    real_installed, real_built = packs.installed_path, packs.built_path
    packs.installed_path, packs.built_path = (lambda: path), (lambda: os.path.join(folder(), 'none'))
    try:
        size = os.path.getsize(path)
        assert packs.find_pack({'size': size, 'sha256': 'x'}) is not None
        assert packs.find_pack({'size': size + 1, 'sha256': 'x'}) is None
    finally:
        packs.installed_path, packs.built_path = real_installed, real_built


class Network:
    """Stands in for urllib: hands over ``data``, or raises ``error``."""

    def __init__(self, data, error=None):
        self.data, self.error, self.calls = data, error, 0

    def __call__(self, url):
        self.calls += 1
        if self.error:
            raise self.error
        net = self

        class Response(io.BytesIO):
            headers = {'Content-Length': str(len(net.data))}
        return Response(self.data)


def served():
    """A pack, its info, and where a download of it goes."""
    path = built()
    info = packs.write_info(path, os.path.join(folder(), 'm1_pack.json'))
    with open(path, 'rb') as f:
        data = f.read()
    return data, info, os.path.join(folder(), 'missions', 'm1.dat')


def test_a_download_is_checked_then_renamed():
    data, info, dest = served()
    d = Download(info, dest, Network(data))
    d.run()
    assert d.state == downloads.DONE and d.percent == 100
    assert os.path.isfile(dest) and not os.path.isfile(dest + '.part')


def test_a_damaged_download_is_fetched_again_then_given_up():
    data, info, dest = served()
    network = Network(data[:-1] + b'!')
    d = Download(info, dest, network)
    d.run()
    assert d.state == downloads.FAILED and network.calls == downloads.TRIES
    assert not os.path.isfile(dest) and not os.path.isfile(dest + '.part')


def test_a_failed_connection_says_why():
    _data, info, dest = served()
    d = Download(info, dest, Network(b'', OSError('no connection')))
    d.run()
    assert d.state == downloads.FAILED and d.error == 'no connection'


def no_missions():
    """The shared recordings, with nothing to play."""
    Recordings._shared = Recordings(audio_folder(False), pack=None)


def test_an_episode_offers_the_download_until_mission_1_is_there():
    no_missions()
    try:
        app = make_app()
        screen = EpisodeMenu(app, STORY, STORY.episodes['1.1.1'], Progress.shared(STORY))
        rows = [r.text for r in screen.rows()]
        assert rows[0] == 'Back' and rows[-1] == 'Download Mission 1'
        locked = EpisodeMenu(app, STORY, STORY.episodes['1.2.1'], Progress.shared(STORY))
        assert [r.text for r in locked.rows()][-1] == 'Start'
    finally:
        Recordings._shared = READY


def test_the_download_row_plays_the_stores_sound():
    no_missions()
    try:
        app = make_app()
        screen = EpisodeMenu(app, STORY, STORY.episodes['1.1.1'], Progress.shared(STORY))
        opened = []
        screen.open = lambda opening, sound='open': opened.append((type(opening), sound))
        screen.rows()[-1].action()                  # nothing downloads: open is a stand-in
        assert opened == [(DownloadScreen, 'download')]
        assert SOUNDS['download'] == '1930Radio D'
    finally:
        Recordings._shared = READY


def test_the_download_screen_says_how_it_goes_and_loads_the_pack():
    no_missions()
    try:
        data, info, dest = served()
        app = make_app()
        menu = EpisodeMenu(app, STORY, STORY.episodes['1.1.1'], Progress.shared(STORY))
        app.stack.push(menu)
        done = []
        screen = DownloadScreen(app, on_done=lambda: done.append(1), fetch=Network(data),
                                info=info, dest=dest)
        app.stack.push(screen)
        screen.download.thread.join(10)
        screen.update()
        assert app.stack.top is menu and done == [1]
        assert 'Downloading Mission 1. Escape cancels.' in app.speech.said
        assert 'Mission 1 is downloaded.' in app.speech.said
        assert Recordings.shared().has_missions
        assert [r.text for r in menu.rows()][-1] == 'Start'
    finally:
        Recordings._shared = READY


def test_every_10_percent_plays_the_push_sound_and_says_how_far():
    no_missions()
    try:
        _data, info, dest = served()
        app = make_app()
        kinds = []
        app.play_sound = kinds.append
        screen = DownloadScreen(app, info=info, dest=dest)
        screen.download = Download(info, dest, Network(b''))   # never started
        screen.said_state = downloads.DOWNLOADING
        screen.download.got = screen.download.total * 35 // 100
        screen.update()
        screen.update()                             # still 30: nothing again
        assert kinds == ['progress'] and app.speech.said == ['30 percent.']
        screen.download.got = screen.download.total * 41 // 100
        screen.update()
        assert kinds == ['progress'] * 2 and app.speech.said[-1] == '40 percent.'
        assert SOUNDS['progress'] == '00000Push'
    finally:
        Recordings._shared = READY


def test_escape_cancels_the_download():
    no_missions()
    try:
        _data, info, dest = served()
        app = make_app()
        app.stack.push(MainMenu(app, STORY))
        screen = DownloadScreen(app, fetch=Network(b'', OSError('slow')), info=info, dest=dest)
        screen.download = Download(info, dest, Network(b''))   # running, never started
        app.stack.push(screen)
        key(app, 'escape')
        assert app.speech.said[-1] == 'Download canceled.' and screen.download.cancelled
    finally:
        Recordings._shared = READY


def test_without_its_info_the_game_cannot_download():
    no_missions()
    try:
        app = make_app()
        app.stack.push(DownloadScreen(app, info=None, dest=os.path.join(folder(), 'm1.dat')))
        assert app.speech.said[-1].startswith('Mission 1 cannot be downloaded')
    finally:
        Recordings._shared = READY


if __name__ == '__main__':
    _quiet.run_tests(globals())
