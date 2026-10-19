"""Hear the audio by ear, before the story engine exists. Not a test.

    python tests/interact/audio_check.py                   from the Prologue's first scene
    python tests/interact/audio_check.py 016F_contactMark  from any state, by its name

It plays a state as the game will: the background, the voice, and once the voice has
finished, the decision loop if the state has one. N goes on to the next state, along the
first way out, so a scene change can be heard: the same background carries on, a different
one cuts over. Everything is spoken through the screen reader.

    N                           the next state
    Space                       pause and resume
    R                           the voice again from its start
    Left and Right              the Seek step back or forward, 10 seconds at first
    Shift+Home and Shift+End    master volume, by the Volume step
    Page Up and Page Down       ambience
    Shift+Page Up and Down      decision sound
    I                           say the state's name and what it plays
    Escape                      quit

It keeps its own save, in %APPDATA%\\CodenameCygnus\\audio_check, so your volumes in the
game are not changed. The plan is aidocks/plans/audio_plan.md.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
os.environ.setdefault('CYGNUS_USER_DIR',
                      os.path.join(os.environ.get('APPDATA') or os.path.expanduser('~'),
                                   'CodenameCygnus', 'audio_check'))
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

import pygame  # noqa: E402

from codenamecygnus import paths  # noqa: E402
from codenamecygnus.game.recordings import Recordings  # noqa: E402
from codenamecygnus.platform.audio import Audio  # noqa: E402
from codenamecygnus.platform.keymap import mods_from_pygame  # noqa: E402
from codenamecygnus.platform.settings import Settings  # noqa: E402
from codenamecygnus.platform.speech import Speech  # noqa: E402


def layers(state):
    voice = back = decision = None
    for m in state['media']:
        name = m['file_name'].lower()
        if name.startswith('back_'):
            back = m['file_name']               # the last listed is the one heard
        elif name.startswith('decision_'):
            decision = m['file_name']
        else:
            voice = m['file_name']
    return voice, back, decision


def main():
    with open(os.path.join(paths.text(), 'states.json'), encoding='utf-8') as f:
        story = json.load(f)
    states = {s['name']: s for s in story['states']}
    out = {}
    for t in story['transitions']:
        out.setdefault(t['origin'], []).append(t)
    name = sys.argv[1] if len(sys.argv) > 1 else '001introOpen'
    if name not in states:
        print('There is no state called %s.' % name)
        return 1

    speech = Speech.shared()
    pygame.display.init()
    pygame.display.set_mode((400, 200))
    pygame.display.set_caption('Codename Cygnus audio check')
    audio = Audio(Settings(), pygame)
    recordings = Recordings()
    now = {'name': name}

    def describe():
        voice, back, decision = layers(states[now['name']])
        return 'State %s. Voice %s. Background %s. Decision sound %s.' % (
            now['name'], voice or 'none', back or 'none', decision or 'none')

    def voice_ended():
        _voice, _back, decision = layers(states[now['name']])
        if decision:
            audio.start_decision(recordings.find(decision))
            speech.speak('The voice has finished; the decision loop plays. N for the next state.')
        else:
            speech.speak('The voice has finished. N for the next state.')

    def play(state_name):
        now['name'] = state_name
        audio.stop_decision()
        voice, back, _decision = layers(states[state_name])
        audio.set_background(recordings.find(back) if back else None)
        if voice:
            audio.play_voice(recordings.find(voice), on_end=voice_ended)
        else:
            audio.stop_voice()
            voice_ended()

    def next_state():
        for t in out.get(now['name'], []):
            target = t.get('destination') or (t['conditions'][0]['destination_else']
                                              if t.get('conditions') else None)
            if target:
                speech.speak('Next: %s' % target)
                play(target)
                return
        speech.speak('This state leads nowhere.')

    speech.speak('Audio check. %s' % describe())
    play(name)
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                key = pygame.key.name(event.key)
                mods = mods_from_pygame(event.mod, pygame)
                shift = mods == ['shift']
                if key == 'escape':
                    running = False
                elif key == 'n' and not mods:
                    next_state()
                elif key == 'space' and not mods:
                    if audio.paused:
                        audio.resume()
                        speech.speak('Resumed.')
                    else:
                        audio.pause()
                        speech.speak('Paused.')
                elif key == 'r' and not mods:
                    audio.replay()
                elif key == 'left' and not mods:
                    audio.seek(-audio.settings.get('seek_step'))
                elif key == 'right' and not mods:
                    audio.seek(audio.settings.get('seek_step'))
                elif key == 'home' and shift:
                    speech.speak(audio.step_volume('master_volume', 1))
                elif key == 'end' and shift:
                    speech.speak(audio.step_volume('master_volume', -1))
                elif key == 'page up':
                    speech.speak(audio.step_volume('decision_volume' if shift else 'ambience_volume', 1))
                elif key == 'page down':
                    speech.speak(audio.step_volume('decision_volume' if shift else 'ambience_volume', -1))
                elif key == 'i':
                    speech.speak(describe())
        audio.update()
        clock.tick(60)
    audio.close()
    pygame.display.quit()
    return 0


if __name__ == '__main__':
    sys.exit(main())
