"""Listening for a choice's words: aidocks/plans/speech_recognition_plan.md.

``Listener.start`` opens the default microphone and limits PocketSphinx to the phrases
given, such as ``['BOLD', 'CLEVER', 'ATHLETIC']``; ``poll``, called once a frame, gives
back what was said since. The microphone is open only between ``start`` and ``stop``, and
nothing it hears is written anywhere or leaves the computer.

A grammar always picks one of its phrases, even for a cough, so the grammar holds other
words too, every other choice word and a few short ones such as "um"; hearing one of
those is speech that matches no choice. The microphone's blocks wait in a queue, filled
by sounddevice's own thread, and are decoded on the main thread in ``poll``.
"""
from __future__ import annotations

import logging
import queue
import re

log = logging.getLogger('listener')

SAMPLE_RATE = 16000
#: Why the microphone cannot be used.
NO_MICROPHONE, BLOCKED = 'none', 'blocked'
#: Short words a player might say that are no choice, so they are not heard as one.
FILLERS = ('the', 'a', 'um', 'uh', 'oh', 'okay', 'what', 'well', 'so', 'and', 'hmm', 'hey',
           'i', 'huh')
#: Windows' microphone privacy setting, the machine's and the user's.
PRIVACY_KEY = r'Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone'


class MicrophoneError(Exception):
    """The microphone cannot be used: ``kind`` is NO_MICROPHONE or BLOCKED."""

    def __init__(self, kind, detail=''):
        super().__init__(detail or kind)
        self.kind = kind


def words_of(phrase):
    """A phrase as the dictionary spells it: "DELPHI'S" as ``['delphis']``."""
    return re.findall(r'[a-z]+', phrase.lower().replace("'", ''))


def privacy_blocked():
    """Whether Windows' privacy settings keep desktop apps from the microphone."""
    try:
        import winreg
    except ImportError:
        return False
    places = ((winreg.HKEY_LOCAL_MACHINE, PRIVACY_KEY), (winreg.HKEY_CURRENT_USER, PRIVACY_KEY),
              (winreg.HKEY_CURRENT_USER, PRIVACY_KEY + r'\NonPackaged'))
    for root, path in places:
        try:
            with winreg.OpenKey(root, path) as key:
                value, _kind = winreg.QueryValueEx(key, 'Value')
        except OSError:
            continue
        if str(value).lower() == 'deny':
            log.info('the microphone is denied at %s', path)
            return True
    return False


def microphone_name():
    """The default input device's name, or None when there is none."""
    try:
        import sounddevice
        return sounddevice.query_devices(kind='input')['name']
    except Exception:
        return None


class Microphone:
    """The default input device, 16 kHz, 16-bit, one channel, in blocks of ``frame_bytes``."""

    def __init__(self, frame_bytes):
        if privacy_blocked():
            raise MicrophoneError(BLOCKED)
        try:
            import sounddevice
            sounddevice.query_devices(kind='input')
            self.blocks = queue.Queue()
            self.stream = sounddevice.RawInputStream(
                samplerate=SAMPLE_RATE, channels=1, dtype='int16',
                blocksize=frame_bytes // 2, callback=self.heard)
            self.stream.start()
        except MicrophoneError:
            raise
        except Exception as error:
            raise MicrophoneError(NO_MICROPHONE, str(error)) from error

    def heard(self, data, frames, time, status):
        # On sounddevice's thread: only queue the block.
        self.blocks.put(bytes(data))

    def read(self):
        """Every block heard since the last read."""
        out = []
        while True:
            try:
                out.append(self.blocks.get_nowait())
            except queue.Empty:
                return out

    def close(self):
        try:
            self.stream.stop()
            self.stream.close()
        except Exception:
            log.exception('closing the microphone')


class Recogniser:
    """PocketSphinx limited to a few phrases, fed 16 kHz, 16-bit mono sound."""

    def __init__(self):
        from pocketsphinx import Decoder, Endpointer
        self._endpointer = Endpointer
        self.decoder = Decoder(lm=None, loglevel='FATAL')
        self.endpointer = Endpointer(sample_rate=SAMPLE_RATE)
        self.frame_bytes = self.endpointer.frame_bytes
        self.pending = b''
        self.known = {}             # a word -> whether the dictionary has it

    def knows(self, word):
        """Whether the dictionary has ``word``, adding a possessive such as "delphis"."""
        if word not in self.known:
            ok = self.decoder.lookup_word(word) is not None
            if not ok and word.endswith('s'):
                base = self.decoder.lookup_word(word[:-1])
                if base is not None:
                    self.decoder.add_word(word, base + ' Z', True)
                    ok = True
            self.known[word] = ok
        return self.known[word]

    def limit(self, phrases, others=()):
        """Hear only ``phrases`` from now on, with ``others`` as speech that is none of
        them. Returns the phrases it can hear, each as its words joined by spaces."""
        usable = []
        for phrase in phrases:
            words = words_of(phrase)
            if words and all(self.knows(w) for w in words):
                usable.append(' '.join(words))
            else:
                log.warning('cannot listen for %r: a word is not in the dictionary', phrase)
        taken = {w for p in usable for w in p.split()}
        extra = sorted({w for o in list(others) + list(FILLERS) for w in words_of(o)
                        if w not in taken and self.knows(w)})
        if not usable:
            return []
        lines = ['#JSGF V1.0;', 'grammar choices;']
        if extra:
            lines += ['public <said> = <choice> | <other>;',
                      '<other> = %s;' % ' | '.join(extra)]
        else:
            lines.append('public <said> = <choice>;')
        lines.append('<choice> = %s;' % ' | '.join(sorted(set(usable))))
        self.decoder.add_jsgf_string('choices', '\n'.join(lines) + '\n')
        self.decoder.activate_search('choices')
        self.reset()
        return usable

    def reset(self):
        """Forget any speech half heard, as listening starts again."""
        self.endpointer = self._endpointer(sample_rate=SAMPLE_RATE)
        self.pending = b''

    def feed(self, data):
        """Sound from the microphone; every utterance that ended in it, as the words heard
        joined by spaces, or '' for speech it could make nothing of."""
        self.pending += data
        out = []
        while len(self.pending) >= self.frame_bytes:
            frame, self.pending = self.pending[:self.frame_bytes], self.pending[self.frame_bytes:]
            was_speech = self.endpointer.in_speech
            speech = self.endpointer.process(frame)
            if speech is None:
                continue
            if not was_speech:
                self.decoder.start_utt()
            self.decoder.process_raw(speech, False, False)
            if not self.endpointer.in_speech:
                self.decoder.end_utt()
                hyp = self.decoder.hyp()
                out.append(' '.join(hyp.hypstr.split()) if hyp is not None else '')
        return out


class Listener:
    """The microphone and the recogniser together, open only while listening."""

    def __init__(self, recogniser=None, microphone=Microphone):
        self.recogniser = recogniser            # loaded at the first listen
        self.open_microphone = microphone
        self.microphone = None
        self.phrases = {}                       # the words heard -> the phrase given

    @property
    def listening(self):
        return self.microphone is not None

    def start(self, phrases, others=()):
        """Listen for these phrases until ``stop``; False when none of them can be heard.
        Raises MicrophoneError."""
        self.stop()
        if self.recogniser is None:
            self.recogniser = Recogniser()
        heard = set(self.recogniser.limit(list(phrases), others))
        self.phrases = {}
        for phrase in phrases:
            words = ' '.join(words_of(phrase))
            if words in heard:
                self.phrases.setdefault(words, phrase)
        if not self.phrases:
            return False
        self.microphone = self.open_microphone(self.recogniser.frame_bytes)
        log.info('listening for %s', ', '.join(self.phrases.values()))
        return True

    def stop(self):
        if self.microphone is not None:
            self.microphone.close()
            self.microphone = None
            log.info('no longer listening')

    def poll(self):
        """What was said since the last poll: (the phrase, or None for speech that is no
        phrase, and the words the recogniser picked), oldest first."""
        if self.microphone is None:
            return []
        out = []
        for block in self.microphone.read():
            for words in self.recogniser.feed(block):
                out.append((self.phrases.get(words), words))
        if out:
            log.info('heard %s', ', '.join(repr(w) for _p, w in out))
        return out
