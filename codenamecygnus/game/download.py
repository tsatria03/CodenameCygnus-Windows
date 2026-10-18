"""Downloading Mission 1's recordings: section 2 of aidocks/plans/build_release_plan.md.

While no recordings are there, loose or in a pack (game/recordings.py), an episode's screen
offers "Download Mission 1" in place of its buttons, as the original's
DOWNLOAD button did, and Continue in the main menu downloads first.

The download runs on a thread of its own, with Python's own urllib, into m1.dat.part in
the save folder's missions folder. The screen says how far it has got every 10 percent,
Enter says it at any time, and Escape cancels, deleting the part. Once it is whole it is
checked against the fingerprint the game carries (game/pack.py's m1_pack.json), fetched
again if it is damaged, up to three times in all, and only then renamed m1.dat, so a cut
connection never leaves a broken pack. The thread only ever touches its own fields and the
part file; the screen, on the main thread, does the speaking and loads the pack.
"""
from __future__ import annotations

import logging
import os
import threading
import urllib.request

from ..ui.screens import Screen
from . import pack as packs
from .recordings import Recordings

log = logging.getLogger('download')

#: Tries in all, for a download whose fingerprint is wrong.
TRIES = 3
CHUNK = 256 * 1024
TIMEOUT = 30

DOWNLOADING, CHECKING, DONE, FAILED, CANCELLED = 'downloading', 'checking', 'done', 'failed', 'cancelled'


def missions_ready():
    """Whether Mission 1's recordings are here to play."""
    return Recordings.shared().has_missions


#: The row an episode's screen offers, without the size (the dev, 2026-10-18: "Please
#: remove the size lable").
OFFER = 'Download Mission 1'


def open_url(url):
    return urllib.request.urlopen(url, timeout=TIMEOUT)


class Download:
    """One download of the pack, on a thread of its own."""

    def __init__(self, info, dest, fetch=open_url):
        self.info = info
        self.dest = dest
        self.part = dest + '.part'
        self.fetch = fetch
        self.state = DOWNLOADING
        self.got = 0
        self.total = info['size']
        self.attempt = 0
        self.error = ''
        self.cancelled = False
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.run, name='download', daemon=True)
        self.thread.start()

    def cancel(self):
        self.cancelled = True

    @property
    def percent(self):
        return int(self.got * 100 / self.total) if self.total else 0

    def run(self):
        try:
            os.makedirs(os.path.dirname(self.dest), exist_ok=True)
            for attempt in range(1, TRIES + 1):
                self.attempt = attempt
                self.state = DOWNLOADING
                self.got = 0
                self.fetch_once()
                if self.cancelled:
                    return self.give_up(CANCELLED)
                self.state = CHECKING
                if packs.fingerprint(self.part) == self.info['sha256']:
                    os.replace(self.part, self.dest)
                    log.info('mission pack downloaded to %s', self.dest)
                    self.state = DONE
                    return
                log.warning('the download was damaged, try %d of %d', attempt, TRIES)
                os.remove(self.part)
            self.error = 'it arrived damaged %d times' % TRIES
            self.give_up(FAILED)
        except Exception as error:
            log.exception('the download failed')
            self.error = str(getattr(error, 'reason', None) or error) or error.__class__.__name__
            self.give_up(CANCELLED if self.cancelled else FAILED)

    def fetch_once(self):
        with self.fetch(self.info.get('url') or packs.URL) as response, open(self.part, 'wb') as out:
            length = response.headers.get('Content-Length') if hasattr(response, 'headers') else None
            if length and length.isdigit():
                self.total = int(length)
            while not self.cancelled:
                block = response.read(CHUNK)
                if not block:
                    break
                out.write(block)
                self.got += len(block)

    def give_up(self, state):
        try:
            if os.path.isfile(self.part):
                os.remove(self.part)
        except OSError:
            log.exception('could not delete %s', self.part)
        self.state = state


class DownloadScreen(Screen):
    """Downloading the pack, with what it says as it goes. ``on_done`` is called once the
    pack is in and this screen has closed, such as Continue going on into the episode."""

    name = 'download'

    def __init__(self, app, on_done=None, fetch=open_url, info='unread', dest=None):
        super().__init__(app)
        self.on_done = on_done
        self.fetch = fetch
        self.info = packs.read_info() if info == 'unread' else info
        self.dest = dest or packs.installed_path()
        self.download = None
        self.said_tenth = 0             # the last tenth said
        self.said_state = None
        self.said_attempt = 1

    def opened(self):
        if self.download is None:
            self.begin()

    def closed(self):
        if self.running:
            self.download.cancel()

    @property
    def running(self):
        return self.download is not None and self.download.state in (DOWNLOADING, CHECKING)

    def begin(self):
        if self.info is None:
            self.say("Mission 1 cannot be downloaded: this copy of the game does not say "
                     "where its recordings are. Press Escape to go back.")
            return
        self.download = Download(self.info, self.dest, self.fetch)
        self.said_tenth, self.said_state, self.said_attempt = 0, DOWNLOADING, 1
        # Without its size, as the row has none (the dev, 2026-10-18: "I want the size lable
        # removed there as well").
        self.say('Downloading Mission 1. Escape cancels.')
        self.download.start()

    def progress_text(self):
        d = self.download
        if d is None:
            return 'Not downloading.'
        if d.state == CHECKING:
            return 'Checking the download.'
        if d.state == FAILED:
            return self.failed_text()
        return '%d percent.' % d.percent

    def failed_text(self):
        return ('The download failed: %s. Press Enter to try again, or Escape to go back.'
                % (self.download.error or 'no reason was given'))

    def update(self):
        d = self.download
        if d is None:
            return
        if d.attempt > self.said_attempt and d.state == DOWNLOADING:
            self.said_attempt = d.attempt
            self.said_tenth = 0
            self.say('The download was damaged, so it is starting again.')
        if d.state == DOWNLOADING:
            tenth = d.percent // 10
            if tenth > self.said_tenth and tenth < 10:
                self.said_tenth = tenth
                self.say('%d percent.' % (tenth * 10), interrupt=False)
        if d.state == self.said_state:
            return
        self.said_state = d.state
        if d.state == CHECKING:
            self.say('Checking the download.', interrupt=False)
        elif d.state == FAILED:
            self.say(self.failed_text())
        elif d.state == DONE:
            self.finish()

    def finish(self):
        try:
            pack = packs.Pack(self.dest)
        except Exception as error:
            log.exception('the downloaded pack will not open')
            self.download.state = FAILED
            self.download.error = str(error)
            self.said_state = FAILED
            return self.say(self.failed_text())
        Recordings.shared().use_pack(pack)
        self.stack.pop()
        self.say('Mission 1 is downloaded.', interrupt=False)
        if self.on_done is not None:
            self.on_done()

    def handle_key(self, key, mods):
        if mods:
            return False
        if key == 'escape':
            if self.running:
                self.download.cancel()
                log.info('download canceled')
                self.app.play_sound('back')
                self.stack.pop()
                self.say('Download canceled.')
            else:
                self.app.play_sound('back')
                self.stack.pop()
        elif key in ('return', 'enter') and self.download is not None and self.download.state == FAILED:
            self.begin()
        else:
            self.say(self.progress_text())
        return True

    def lines(self):
        out = ['Downloading Mission 1', '']
        if self.download is not None:
            d = self.download
            out.append(self.progress_text())
            out.append('%d of %d megabytes' % (d.got // (1 << 20), d.total // (1 << 20)))
        return out
