"""Which screen reader or voice speaks, with stand-ins only: nothing here ever speaks."""
import _quiet  # noqa: F401  first, before any of the game

from codenamecygnus.platform import speech as speech_module
from codenamecygnus.platform.speech import Speech


class FakeNvda:
    def __init__(self, running):
        self.is_running = running
        self.said = []
        self.cancelled = 0

    def running(self):
        return self.is_running

    def speak(self, text, interrupt):
        if not self.is_running:
            return False
        if interrupt:
            self.cancelled += 1
        self.said.append(text)
        return True

    def stop(self):
        self.cancelled += 1


class FakePrism:
    def __init__(self, reader=None, voice=None):
        self.reader, self.voice = reader, voice
        self.said = []

    def speak_reader(self, text, interrupt):
        if self.reader:
            self.said.append((self.reader, text, interrupt))
            return self.reader
        return None

    def speak_voice(self, text, interrupt):
        if self.voice:
            self.said.append((self.voice, text, interrupt))
            return self.voice
        return None

    def current_reader(self):
        return None

    def current_voice(self):
        return None

    def stop(self):
        pass


def test_the_tests_never_reach_the_players_screen_reader():
    s = Speech()
    assert s.silent, 'CYGNUS_SILENT did not make the speech silent'
    assert s.speak('hello') is False
    assert s._prism is None, 'Prism was loaded in a silent run'
    assert s.which == 'none'


def test_nvda_speaks_first_when_it_is_running():
    nvda, prism = FakeNvda(True), FakePrism(reader='JAWS')
    s = Speech(nvda=nvda, prism=prism)
    assert s.speak('Settings')
    assert nvda.said == ['Settings'] and prism.said == []


def test_another_screen_reader_speaks_when_nvda_is_not_running():
    nvda, prism = FakeNvda(False), FakePrism(reader='JAWS', voice='SAPI')
    s = Speech(nvda=nvda, prism=prism)
    assert s.speak('hello', interrupt=False)
    assert prism.said == [('JAWS', 'hello', False)]


def test_a_voice_speaks_when_no_screen_reader_is_running():
    nvda, prism = FakeNvda(False), FakePrism(voice='SAPI')
    s = Speech(nvda=nvda, prism=prism)
    assert s.speak('hello')
    assert prism.said == [('SAPI', 'hello', True)]


def test_interrupt_cuts_off_and_waiting_does_not():
    nvda = FakeNvda(True)
    s = Speech(nvda=nvda, prism=FakePrism())
    s.speak('one', interrupt=True)
    s.speak('two', interrupt=False)
    assert nvda.cancelled == 1 and nvda.said == ['one', 'two']


def test_nothing_to_speak_through_is_not_an_error():
    s = Speech(nvda=FakeNvda(False), prism=FakePrism())
    assert s.speak('hello') is False


def test_the_last_line_is_kept_for_the_window():
    s = Speech()
    s.speak('Codename Cygnus. Main menu.')
    assert s.last == 'Codename Cygnus. Main menu.'


def test_only_windows_screen_readers_are_tried():
    assert 'ORCA' not in speech_module.READERS and 'VOICE_OVER' not in speech_module.READERS
    assert speech_module.VOICES == ('SAPI', 'ONE_CORE')


if __name__ == '__main__':
    _quiet.run_tests(globals())
