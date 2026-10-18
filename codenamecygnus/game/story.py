"""The story's rules: states, where each goes next, and the story variables.

Section 1 of aidocks/plans/story_engine_plan.md. Nothing here plays a sound or reads a key;
the episode screen (section 2) drives it.

The data is the exported ``states.json`` and ``missions.json`` (aidocks/plans/story_export_plan.md):

* A **state** has media (a voice, a background and a decision sound, told apart by name),
  a script (headings, speech and sound directions), variables it sets, and achievements.
* Its **ways out** are, in the file's order:
  - ``auto``: go on by itself, once the voice has ended. With a condition, such as
    ``event.m1e2_serum==1``, it goes one way if the condition holds and the other if not.
    The first automatic way out wins, as in the original's
    ``-[CCStateMachine performAutoTransition]`` (0x100049c00).
  - ``manual``: a choice, spoken or picked with a key. A hidden one (``render: false``)
    can be said but is not offered.
  - ``auto-timeout``: where the story goes when a choice waits ``duration`` seconds.
* **Variables** are whole numbers by name. A state's ``value`` sets one, ``++`` raises it
  by one and ``--`` lowers it. A variable never set counts as 0, as a missing value did in
  the original, so ``event.m1e1_cardsWin==1`` is false for a player who lost at cards.
"""
from __future__ import annotations

import json
import logging
import os
import re

from .. import paths

log = logging.getLogger('story')

EXPRESSION = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_.]*)\s*(==|>=|<=|>|<)\s*(-?\d+)\s*$')
TRAITS = ('Openness', 'Predictability', 'Diplomacy', 'Activeness')


def holds(expression, variables):
    """Whether a condition such as ``Diplomacy>=0`` holds for these variables."""
    match = EXPRESSION.match(expression)
    if match is None:
        log.error('a condition that cannot be read: %r', expression)
        return False
    name, op, number = match.group(1), match.group(2), int(match.group(3))
    value = variables.get(name, 0)
    return {'==': value == number, '>=': value >= number, '<=': value <= number,
            '>': value > number, '<': value < number}[op]


def _kind(file_name):
    name = file_name.lower()
    if name.startswith('back_'):
        return 'background'
    if name.startswith('decision_'):
        return 'decision'
    return 'voice'


class Choice:
    """One choice: the word to say, where it leads, and whether it is offered."""

    def __init__(self, text, destination, hidden=False):
        self.text = text
        self.destination = destination
        self.hidden = hidden

    @property
    def spoken(self):
        """The word as the screen reader says it: "Charismatic", "Two cards"."""
        return self.text.capitalize()

    def __repr__(self):
        return 'Choice(%r -> %s%s)' % (self.text, self.destination, ', hidden' if self.hidden else '')


class State:
    def __init__(self, data):
        self.data = data
        self.name = data['name']
        self.voice = self.background = self.decision = None
        for medium in data.get('media', []):
            kind = _kind(medium['file_name'])
            # Where a state lists several backgrounds, each replaced the last in the
            # original, so the last listed is the one heard (aidocks/plans/audio_plan.md).
            setattr(self, kind, medium['file_name'])
        self.script = data.get('script', [])
        self.variables = data.get('variables', [])
        self.achievements = [a['achievement_id'] for a in data.get('achievements', [])]

    @property
    def heading(self):
        """The scene heading this state's script gives, or None."""
        for line in self.script:
            if line.get('type') == 'HEADING':
                return line.get('text', '').strip()
        return None

    @property
    def plays_nothing(self):
        return not (self.voice or self.background or self.decision)

    def __repr__(self):
        return 'State(%s)' % self.name


class Episode:
    def __init__(self, data, mission_id):
        self.data = data
        self.mission_id = mission_id
        self.id = data['episode_id']
        self.title = data['title']
        self.description = data.get('description', '')
        self.completion_text = data.get('completion_text', '')
        self.credits = data.get('credits', [])
        self.start = data.get('initial_state_name', '')
        self.end = data.get('end_state_name', '')
        self.preview = data.get('preview_state_name', '')
        self.preview_episode = data.get('preview_episode_id', '')
        lock = data.get('episode_lock', {})
        self.locked_at_first = bool(lock.get('is_locked'))
        self.locked_by = lock.get('locked_by_id', '')

    @property
    def number(self):
        """2 for episode 1.2.1."""
        return int(self.id.split('.')[1])

    @property
    def playable(self):
        return bool(self.start and self.end)

    def __repr__(self):
        return 'Episode(%s %s)' % (self.id, self.title)


class Story:
    _shared = None

    @classmethod
    def shared(cls):
        if cls._shared is None:
            cls._shared = Story()
        return cls._shared

    def __init__(self, folder=None):
        folder = folder or paths.text()
        with open(os.path.join(folder, 'states.json'), encoding='utf-8') as f:
            states = json.load(f)
        with open(os.path.join(folder, 'missions.json'), encoding='utf-8') as f:
            missions = json.load(f)
        self.states = {s['name']: State(s) for s in states['states']}
        self.ways_out = {}
        for t in states['transitions']:
            self.ways_out.setdefault(t['origin'], []).append(t)
        self.episodes = {}
        for mission in missions['missions']:
            for e in mission['episodes']:
                episode = Episode(e, mission['mission_id'])
                self.episodes[episode.id] = episode
        self.company_credits = missions.get('company_credits', {}).get('credits', [])
        log.info('story loaded: %d states, %d episodes', len(self.states), len(self.episodes))

    def state(self, name):
        return self.states[name]

    def playable_episodes(self):
        return [e for e in self.episodes.values() if e.playable]

    # ---- where a state goes ---------------------------------------------
    def next_state(self, name, variables):
        """Where ``name`` goes by itself once its voice has ended, or None when it waits for
        a choice or is an end."""
        for t in self.ways_out.get(name, []):
            if t['type'] != 'auto':
                continue
            if t.get('conditions'):
                c = t['conditions'][0]
                return c['destination_if'] if holds(c['expression'], variables) else c['destination_else']
            return t['destination']
        return None

    def choices(self, name, include_hidden=False):
        """The choices ``name`` offers, in order; the hidden ones only when asked for."""
        out = [Choice(t['text'], t['destination'], hidden=t.get('render') is False)
               for t in self.ways_out.get(name, []) if t['type'] == 'manual']
        return out if include_hidden else [c for c in out if not c.hidden]

    def timeout(self, name):
        """(seconds, where it goes) for a choice that times out, or None."""
        for t in self.ways_out.get(name, []):
            if t['type'] == 'auto-timeout':
                return float(t.get('duration', 7)), t['destination']
        return None


class Playthrough:
    """One run through an episode: where it is, and the variables so far.

    ``enter`` applies a state's variables and gives back what it earned; the episode screen
    plays it, then calls ``after_voice``, and ``choose`` or ``time_out`` when it waits.
    """

    def __init__(self, story, episode, variables=None):
        self.story = story
        self.episode = episode
        self.variables = dict(variables or {})
        self.current = None
        self.earned = []            # achievement ids earned so far in this run
        self.finished = False

    def start(self, at=None):
        return self.enter(at or self.episode.start)

    def enter(self, name):
        """Go to state ``name``: apply its variables, note its achievements, and return it."""
        state = self.story.state(name)
        self.current = state
        for op in state.variables:
            key = op['name']
            if op.get('command') == '++':
                self.variables[key] = self.variables.get(key, 0) + 1
            elif op.get('command') == '--':
                self.variables[key] = self.variables.get(key, 0) - 1
            elif 'value' in op:
                self.variables[key] = int(op['value'])
        for a in state.achievements:
            if a not in self.earned:
                self.earned.append(a)
        if name == self.episode.end:
            self.finished = True
        return state

    def after_voice(self):
        """The current state's voice has ended: the state it goes to by itself, entered, or
        None when it waits for a choice or the episode is over."""
        if self.finished:
            return None
        target = self.story.next_state(self.current.name, self.variables)
        return self.enter(target) if target else None

    @property
    def waiting(self):
        """Whether the current state waits for a choice."""
        return bool(self.story.choices(self.current.name, include_hidden=True)) and not self.finished

    def choices(self):
        return self.story.choices(self.current.name)

    def all_choices(self):
        return self.story.choices(self.current.name, include_hidden=True)

    def timeout(self):
        return self.story.timeout(self.current.name)

    def choose(self, choice):
        return self.enter(choice.destination)

    def time_out(self):
        out = self.timeout()
        return self.enter(out[1]) if out else None

    def trait(self, name):
        return self.variables.get(name, 0)
