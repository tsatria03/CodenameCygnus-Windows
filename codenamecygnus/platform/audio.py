"""Everything the game plays, through pygame's mixer (aidocks/plans/audio_plan.md).

Three layers play a story state, as the original's sound manager did, plus the menus'
interface sounds:

* **The voice** streams through ``pygame.mixer.music``, the only pygame player that can
  start partway through a file, which replaying, skipping 5 seconds back or forward and S
  need. When it reaches its end, the story is told (``on_end``).
* **The background** loops on channel 0. A state with the same background lets it carry
  on untouched; a different one stops the old at once and starts the new; a state with
  none stops it. That is the original's own hard cut, read from its code.
* **The decision loop** loops on channel 1 while a choice waits, starting once the
  question's recording has finished, and stops when a choice is made.
* **The menu sounds** play once on channel 2.

Space and Escape pause all of them together. pygame says a paused voice is not playing, so
this keeps its own note of pausing, and a pause is never taken for the voice ending.

Three volumes, each 0 to 100 in tens, are kept in the settings: master moves everything,
ambience the background and decision the decision loop. A percentage becomes a gain
squared, so each step sounds about as big as the last.

If no sound device can be opened, everything here does nothing and the game carries on,
silent, with the log saying why.
"""
from __future__ import annotations

import io
import logging
import struct
import time

log = logging.getLogger('audio')

BACKGROUND, DECISION, MENU = 0, 1, 2
#: Seconds the voice skips with Left and Right.
SKIP_SECONDS = 5.0
#: Seconds after the voice starts before pygame's "not playing" is believed, since the
#: stream can take a moment to begin.
START_GRACE = 0.25
#: The volumes as they are spoken (the dev, 2026-10-18: "rename the following volume
#: settings to this. Backround ambience volume, Decision loop volume").
VOLUME_LABELS = {'master_volume': 'Master volume',
                 'ambience_volume': 'Background ambience volume',
                 'decision_volume': 'Decision loop volume'}

_BITRATES = {1: (0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320),
             2: (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160)}
_RATES = {3: (44100, 48000, 32000), 2: (22050, 24000, 16000), 0: (11025, 12000, 8000)}


def mp3_length(data):
    """An MP3's length in seconds, from its own headers, or None if it cannot be read.

    pygame cannot say how long a streamed MP3 is. The first frame says the bitrate and
    sample rate, and a Xing, Info or VBRI header after it says how many frames there are;
    without one, the file is taken to be at one bitrate throughout."""
    offset = 0
    if data[:3] == b'ID3' and len(data) >= 10:
        size = data[6] << 21 | data[7] << 14 | data[8] << 7 | data[9]
        offset = 10 + size
    while offset + 4 <= len(data):
        if data[offset] == 0xFF and (data[offset + 1] & 0xE0) == 0xE0:
            header = struct.unpack('>I', data[offset:offset + 4])[0]
            version = (header >> 19) & 3          # 3 MPEG-1, 2 MPEG-2, 0 MPEG-2.5
            layer = (header >> 17) & 3            # 1 is Layer III
            bitrate_index = (header >> 12) & 15
            rate_index = (header >> 10) & 3
            if version != 1 and layer == 1 and 0 < bitrate_index < 15 and rate_index < 3:
                break
        offset += 1
    else:
        return None
    mono = ((header >> 6) & 3) == 3
    mpeg1 = version == 3
    bitrate = _BITRATES[1 if mpeg1 else 2][bitrate_index] * 1000
    rate = _RATES[version][rate_index]
    samples_per_frame = 1152 if mpeg1 else 576
    side = (17 if mono else 32) if mpeg1 else (9 if mono else 17)
    xing = offset + 4 + side
    if data[xing:xing + 4] in (b'Xing', b'Info'):
        flags = struct.unpack('>I', data[xing + 4:xing + 8])[0]
        if flags & 1:
            frames = struct.unpack('>I', data[xing + 8:xing + 12])[0]
            return frames * samples_per_frame / rate
    vbri = offset + 4 + 32
    if data[vbri:vbri + 4] == b'VBRI':
        frames = struct.unpack('>I', data[vbri + 14:vbri + 18])[0]
        return frames * samples_per_frame / rate
    return (len(data) - offset) * 8 / bitrate


def percent_gain(percent):
    """A volume percentage as the gain pygame takes, from 0.0 to 1.0."""
    return (max(0, min(100, percent)) / 100.0) ** 2


class Audio:
    _shared = None

    @classmethod
    def shared(cls, settings=None, pygame=None):
        if cls._shared is None:
            cls._shared = Audio(settings, pygame)
        return cls._shared

    def __init__(self, settings, pygame=None, clock=time.perf_counter):
        self.settings = settings
        self.clock = clock
        self.pg = pygame
        self.ok = False
        self.paused = False
        # the voice
        self.voice = None               # the Recording playing, or None
        self.voice_length = None        # seconds, or None when unknown
        self.voice_offset = 0.0         # where in the file the stream last started
        self.voice_started = 0.0        # the clock when it did
        self.paused_at = None           # the clock when the voice was paused
        self.on_end = None
        self._end_soon = False          # a voice that could not play ends at the next update
        # the loops
        self.background = None          # the background Recording's name, or None
        self.decision = None
        self._sounds = {}               # name -> pygame Sound, for the loops
        if pygame is not None:
            self.open(pygame)

    # ---- the device ------------------------------------------------------
    def open(self, pygame):
        self.pg = pygame
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 1024)
            pygame.mixer.set_num_channels(8)
            pygame.mixer.set_reserved(3)
            self.ok = True
            log.info('sound device open: %s', pygame.mixer.get_init())
        except Exception as error:
            log.error('no sound device could be opened, so the game is silent: %s', error)
            self.ok = False
        self.apply_volumes()

    def close(self):
        if self.ok:
            self.stop_all()
            self.pg.mixer.quit()
            self.ok = False

    # ---- volumes ---------------------------------------------------------
    def percent(self, key):
        return self.settings.get(key) if self.settings is not None else 100

    def gain(self, layer):
        master = percent_gain(self.percent('master_volume'))
        if layer == BACKGROUND:
            return master * percent_gain(self.percent('ambience_volume'))
        if layer == DECISION:
            return master * percent_gain(self.percent('decision_volume'))
        return master

    def apply_volumes(self):
        if not self.ok:
            return
        self.pg.mixer.music.set_volume(self.gain(None))
        for layer in (BACKGROUND, DECISION, MENU):
            self.pg.mixer.Channel(layer).set_volume(self.gain(layer))

    def step_volume(self, key, step):
        """Move a volume one step of ten up (1) or down (-1); what to say, such as
        "Background ambience volume 60 percent". At either end it stays, and says so."""
        now = self.percent(key)
        new = max(0, min(100, now + 10 * step))
        if new != now:
            self.settings.set(key, new)
            self.apply_volumes()
        return '%s %d percent' % (VOLUME_LABELS[key], new)

    # ---- loading ---------------------------------------------------------
    def _bytes(self, recording):
        if recording.data is not None:
            return recording.data
        with open(recording.path, 'rb') as f:
            return f.read()

    def _sound(self, recording):
        sound = self._sounds.get(recording.name)
        if sound is None:
            if recording.data is not None:
                sound = self.pg.mixer.Sound(file=io.BytesIO(recording.data))
            else:
                sound = self.pg.mixer.Sound(recording.path)
            self._sounds[recording.name] = sound
        return sound

    # ---- the voice ------------------------------------------------------
    def play_voice(self, recording, start=0.0, on_end=None):
        """Play a state's voice from ``start`` seconds; ``on_end`` is called when it ends.
        A missing recording ends at once, so the story never waits on silence."""
        self.on_end = on_end
        self.voice = recording
        self._end_soon = False
        if recording is None or not self.ok:
            self.voice_length = 0.0
            self._end_soon = True
            return
        try:
            data = self._bytes(recording)
            self.voice_length = mp3_length(data)
            if recording.data is not None:
                self.pg.mixer.music.load(io.BytesIO(data), 'mp3')
            else:
                self.pg.mixer.music.load(recording.path)
            self._start_stream(max(0.0, start))
        except Exception:
            log.exception('could not play %s', recording.name)
            self._end_soon = True

    def _start_stream(self, at):
        self.pg.mixer.music.play(start=at)
        self.voice_offset = at
        self.voice_started = self.clock()
        if self.paused:
            self.pg.mixer.music.pause()
            self.paused_at = self.clock()

    def position(self):
        """Seconds into the voice, counting no time while paused."""
        if self.voice is None:
            return 0.0
        now = self.paused_at if self.paused and self.paused_at is not None else self.clock()
        return self.voice_offset + max(0.0, now - self.voice_started)

    def seek(self, delta):
        """Skip ``delta`` seconds back or forward in the voice. Skipping past the end ends
        it, as reaching the end does; skipping before the start goes to the start."""
        if self.voice is None or not self.ok:
            return
        target = max(0.0, self.position() + delta)
        if self.voice_length is not None and target >= self.voice_length:
            self._finish_voice()
            return
        self._start_stream(target)

    def replay(self):
        """The voice again from its start."""
        if self.voice is not None and self.ok:
            self._end_soon = False
            self._start_stream(0.0)

    def stop_voice(self):
        self.voice = None
        self.on_end = None
        self._end_soon = False
        if self.ok:
            self.pg.mixer.music.stop()

    def _finish_voice(self):
        if self.ok:
            self.pg.mixer.music.stop()
        callback = self.on_end
        self.voice = None
        self.on_end = None
        self._end_soon = False
        if callback is not None:
            callback()

    def update(self):
        """Called once a frame: tells the story when its voice has ended."""
        if self.voice is None and not self._end_soon:
            return
        if self._end_soon:
            if not self.paused:
                self._finish_voice()
            return
        if self.paused or not self.ok:
            return
        if self.clock() - self.voice_started < START_GRACE:
            return
        if not self.pg.mixer.music.get_busy():
            self._finish_voice()

    # ---- the loops -------------------------------------------------------
    def set_background(self, recording):
        """The state's background: the same one carries on, another cuts over, None stops it."""
        name = recording.name if recording is not None else None
        if name == self.background:
            return
        if self.ok:
            self.pg.mixer.Channel(BACKGROUND).stop()
        if self.background is not None and self.background != self.decision:
            # A background is decoded whole, up to 14 MB for the longest; keep only the
            # one playing, rather than every scene's.
            self._sounds.pop(self.background, None)
        self.background = None
        if recording is None or not self.ok:
            return
        try:
            self.pg.mixer.Channel(BACKGROUND).play(self._sound(recording), loops=-1)
            self.background = name
            if self.paused:
                self.pg.mixer.Channel(BACKGROUND).pause()
        except Exception:
            log.exception('could not play the background %s', name)

    def start_decision(self, recording):
        """Loop the decision sound while a choice waits."""
        self.stop_decision()
        if recording is None or not self.ok:
            return
        try:
            self.pg.mixer.Channel(DECISION).play(self._sound(recording), loops=-1)
            self.decision = recording.name
            if self.paused:
                self.pg.mixer.Channel(DECISION).pause()
        except Exception:
            log.exception('could not play the decision sound %s', recording.name)

    def stop_decision(self):
        if self.ok:
            self.pg.mixer.Channel(DECISION).stop()
        self.decision = None

    def play_menu(self, recording):
        """An interface sound, once."""
        if recording is None or not self.ok:
            return
        try:
            self.pg.mixer.Channel(MENU).play(self._sound(recording))
        except Exception:
            log.exception('could not play the menu sound %s', recording.name)

    # ---- pausing ---------------------------------------------------------
    def pause(self):
        """Pause every layer together."""
        if self.paused:
            return
        self.paused = True
        self.paused_at = self.clock()
        if self.ok:
            self.pg.mixer.music.pause()
            self.pg.mixer.Channel(BACKGROUND).pause()
            self.pg.mixer.Channel(DECISION).pause()

    def resume(self):
        """Resume every layer together, the voice from where it paused."""
        if not self.paused:
            return
        if self.paused_at is not None:
            self.voice_started += self.clock() - self.paused_at
        self.paused = False
        self.paused_at = None
        if self.ok:
            self.pg.mixer.music.unpause()
            self.pg.mixer.Channel(BACKGROUND).unpause()
            self.pg.mixer.Channel(DECISION).unpause()

    def stop_all(self):
        """Stop every layer, as when leaving an episode."""
        self.stop_voice()
        self.set_background(None)
        self.stop_decision()
        self.paused = False
        self.paused_at = None
        self._sounds.clear()
