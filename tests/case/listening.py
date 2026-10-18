"""Speech recognition: the episode screen listening, with a stand-in for the microphone,
and the recogniser's grammar for every choice in the story. No microphone is opened.
"""
import _quiet  # noqa: F401  first, before any of the game

from episode import STORY, end_voice, jump, key, start

from codenamecygnus.game.episode_screen import (BLOCKED_TEXT, LISTENING, NO_MICROPHONE_TEXT,
                                                NOT_CAUGHT, NOT_LISTENING)
from codenamecygnus.platform import runloop
from codenamecygnus.platform.listener import (BLOCKED, NO_MICROPHONE, Listener,
                                              MicrophoneError, Recogniser, words_of)


class FakeListener:
    """Notes what it was asked to listen for; ``hear`` queues something said."""

    def __init__(self, error=None):
        self.error = error
        self.listening = False
        self.phrases = None
        self.others = None
        self.starts = 0
        self.said = []

    def start(self, phrases, others=()):
        self.starts += 1
        if self.error:
            raise MicrophoneError(self.error)
        self.phrases, self.others, self.listening = list(phrases), list(others), True
        return True

    def stop(self):
        self.listening = False

    def poll(self):
        out, self.said = self.said, []
        return out

    def hear(self, phrase, words=None):
        self.said.append((phrase, words or (phrase or 'um').lower()))


def listening(episode_id='1.1.1', error=None, on=True):
    app, screen = start(episode_id)
    app._listener = FakeListener(error)
    app.settings.set('speech_recognition', on)
    return app, screen


def at(app, screen, name):
    jump(app, screen, name)
    end_voice(app)


def test_off_by_default_it_never_listens():
    app, screen = listening(on=False)
    at(app, screen, '012introRejectPrompt')
    assert app._listener.starts == 0 and LISTENING not in app.speech.said


def test_at_a_choice_it_says_listening_after_the_first_choice():
    app, screen = listening()
    at(app, screen, '012introRejectPrompt')
    assert app.speech.heard[-2:] == [('Charismatic', False), (LISTENING, False)]
    assert app._listener.listening and app._listener.phrases == ['CHARISMATIC', 'HOSTILE']
    assert 'TWO CARDS' in app._listener.others
    assert '(listening)' in screen.lines()


def test_a_word_heard_makes_its_choice_and_says_it():
    app, screen = listening()
    at(app, screen, '012introRejectPrompt')
    app._listener.hear('HOSTILE')
    screen.update()
    hostile = next(c for c in STORY.choices('012introRejectPrompt') if c.text == 'HOSTILE')
    assert screen.run.current.name == hostile.destination
    assert app.speech.said[-1] == 'Hostile' and not app._listener.listening


def test_speech_that_is_no_choice_is_not_caught_and_listening_goes_on():
    app, screen = listening()
    at(app, screen, '012introRejectPrompt')
    app._listener.hear(None, 'um')
    screen.update()
    assert app.speech.said[-1] == NOT_CAUGHT
    assert app._listener.listening and screen.run.current.name == '012introRejectPrompt'


def test_after_15_seconds_it_stops_and_c_listens_again():
    app, screen = listening()
    at(app, screen, '012introRejectPrompt')
    app.loop.pump(runloop.clock() + 14.5)
    assert app._listener.listening
    app.loop.pump(runloop.clock() + 15.5)
    assert not app._listener.listening and app.speech.said[-1] == NOT_LISTENING
    assert screen.offered and app.audio.decision is not None, 'the choice stays open'
    key(app, 'c')
    assert app.speech.said[-2:] == ['Charismatic or Hostile.', LISTENING]
    assert app._listener.listening and app._listener.starts == 2


def test_a_hidden_choice_can_be_spoken():
    app, screen = listening('1.8.1')
    at(app, screen, '013drinkDruggedPrompt_m1e8')
    assert 'HER DRINK' in app._listener.phrases
    app._listener.hear('HER DRINK')
    screen.update()
    assert screen.run.current.name == '014AherDrinkhiddenResponse_m1e8'


def test_a_timed_choice_listens_for_its_whole_clock():
    app, screen = listening('1.8.1')
    at(app, screen, '009drinkPrompt_m1e8')
    assert screen.listen_timer is None and app._listener.listening
    app.loop.pump(runloop.clock() + 6.5)
    assert app._listener.listening and NOT_LISTENING not in app.speech.said
    app.loop.pump(runloop.clock() + 7.5)
    assert screen.run.current.name == '010Ctimeout_m1e8' and not app._listener.listening


def test_pausing_stops_listening_and_resuming_goes_on_quietly():
    real, now = runloop.clock, [runloop.clock()]
    runloop.clock = lambda: now[0]                  # a clock the test moves on
    try:
        app, screen = listening()
        at(app, screen, '012introRejectPrompt')
        now[0] += 10
        key(app, 'escape')                          # the pause menu
        assert not app._listener.listening
        now[0] += 60
        key(app, 'escape')                          # Resume
        assert app._listener.listening and app.speech.said.count(LISTENING) == 1
        now[0] += 4.5
        app.loop.pump()
        assert app._listener.listening, 'it had 5 seconds left'
        now[0] += 1
        app.loop.pump()
        assert not app._listener.listening and app.speech.said[-1] == NOT_LISTENING
    finally:
        runloop.clock = real


def test_turned_on_in_the_pause_menus_settings_it_listens_on_resuming():
    app, screen = listening(on=False)
    at(app, screen, '012introRejectPrompt')
    key(app, 'escape')
    app.settings.set('speech_recognition', True)
    key(app, 'escape')
    assert app._listener.listening and app.speech.said[-1] == LISTENING


def test_v_turns_it_on_at_a_waiting_choice_and_cannot_turn_it_off_while_listening():
    app, screen = listening(on=False)
    at(app, screen, '012introRejectPrompt')
    key(app, 'v')
    assert app.settings.get('speech_recognition') is True
    assert app.speech.said[-2:] == ['Speech recognition on.', LISTENING]
    assert app._listener.listening
    key(app, 'v')                                   # as the original's button, disabled
    assert app.speech.said[-1] == LISTENING and app._listener.listening
    assert app.settings.get('speech_recognition') is True
    app.loop.pump(runloop.clock() + 15.5)           # listening over: V works again
    key(app, 'v')
    assert app.speech.said[-1] == 'Speech recognition off.'
    assert app.settings.get('speech_recognition') is False


def test_v_while_the_story_plays_only_turns_it_on():
    app, screen = listening(on=False)
    key(app, 'v')
    assert app.speech.said[-1] == 'Speech recognition on.' and app._listener.starts == 0


def test_r_and_the_keys_stop_listening():
    app, screen = listening()
    at(app, screen, '012introRejectPrompt')
    key(app, 'r')
    assert not app._listener.listening
    end_voice(app)
    assert app._listener.listening
    key(app, 'return')
    assert not app._listener.listening


def test_no_microphone_is_said_once_a_session():
    app, screen = listening(error=NO_MICROPHONE)
    at(app, screen, '012introRejectPrompt')
    assert app.speech.said[-1] == NO_MICROPHONE_TEXT and not screen.listening
    key(app, 'c')
    assert app.speech.said.count(NO_MICROPHONE_TEXT) == 1 and app._listener.starts == 2
    assert app.settings.get('speech_recognition') is True, 'the setting stays on'


def test_a_blocked_microphone_says_so():
    app, screen = listening(error=BLOCKED)
    at(app, screen, '012introRejectPrompt')
    assert app.speech.said[-1] == BLOCKED_TEXT


# ---- the recogniser, with no microphone ----------------------------------
RECOGNISER = []


def recogniser():
    if not RECOGNISER:
        RECOGNISER.append(Recogniser())
    return RECOGNISER[0]


def test_words_are_spelt_as_the_dictionary_has_them():
    assert words_of("DELPHI'S") == ['delphis'] and words_of('TWO CARDS') == ['two', 'cards']


def test_every_choice_in_the_story_can_be_listened_for():
    r = recogniser()
    others = STORY.choice_texts()
    for name in STORY.states:
        phrases = [c.text for c in STORY.choices(name, include_hidden=True)]
        if phrases:
            heard = r.limit(phrases, others)
            assert len(heard) == len(set(heard)) == len({' '.join(words_of(p)) for p in phrases}), name


def test_silence_is_heard_as_nothing():
    r = recogniser()
    r.limit(['BOLD', 'CLEVER'], STORY.choice_texts())
    assert r.feed(bytes(r.frame_bytes * 100)) == []


class SilentMicrophone:
    def __init__(self, frame_bytes):
        self.frame_bytes = frame_bytes
        self.closed = False

    def read(self):
        return [bytes(self.frame_bytes)] * 10

    def close(self):
        self.closed = True


def test_the_listener_opens_the_microphone_only_while_listening():
    opened = []

    def microphone(frame_bytes):
        opened.append(SilentMicrophone(frame_bytes))
        return opened[-1]

    listener = Listener(recogniser(), microphone)
    assert listener.poll() == [] and not opened
    assert listener.start(['GRAB IT', 'HANG ON'], STORY.choice_texts())
    assert listener.listening and listener.poll() == []
    listener.stop()
    assert opened[0].closed and not listener.listening


if __name__ == '__main__':
    _quiet.run_tests(globals())
