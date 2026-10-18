"""The player's progress through Mission 1, in ``saves/progress.json``: section 1 of
aidocks/plans/saves_plan.md.

For each episode played, the file keeps:

* its **state**: in progress or completed; an episode not in the file is new;
* the **variables it began with**, which Restart and Replay start it with again;
* the **variables it ended with**, once completed, which the episode it opens begins with,
  so every choice reaches the episodes that check it;
* while in progress, its **place**: the state the player was in, and the variables as they
  were before that state was entered, so continuing enters it again and applies its
  variables once, not twice.

``last`` is the episode played most recently, which the main menu's Continue goes back to.

Every player starts from scratch; nothing is read from the original's database
(aidocks/general/project_story_data_source.md). The file is written safely at every
change, which is every new state, about every 15 seconds in play.
"""
from __future__ import annotations

import logging

from .. import paths
from ..platform.files import JsonFile

log = logging.getLogger('progress')

NEW, IN_PROGRESS, COMPLETED = 'new', 'in progress', 'completed'


def _variables(value):
    """Whole-number variables from the file, leaving out anything else."""
    if not isinstance(value, dict):
        return {}
    return {k: v for k, v in value.items()
            if isinstance(k, str) and isinstance(v, int) and not isinstance(v, bool)}


class Progress:
    _shared = None

    @classmethod
    def shared(cls, story=None):
        if cls._shared is None:
            cls._shared = Progress(story=story)
        return cls._shared

    def __init__(self, path=None, story=None):
        from .story import Story
        self.story = story or Story.shared()
        self.file = JsonFile(path or paths.user_path('saves', 'progress.json'),
                             order=['last', 'episodes'])
        self.episodes = {}
        saved = self.file.data.get('episodes')
        for episode_id, entry in (saved.items() if isinstance(saved, dict) else ()):
            if episode_id in self.story.episodes and isinstance(entry, dict):
                self.episodes[episode_id] = self._clean(entry)
        last = self.file.data.get('last')
        self.last = last if last in self.episodes else None
        if self.file.recovered:
            self.save()

    @staticmethod
    def _clean(entry):
        state = entry.get('state') if entry.get('state') in (IN_PROGRESS, COMPLETED) else IN_PROGRESS
        out = {'state': state, 'began_with': _variables(entry.get('began_with'))}
        if state == COMPLETED:
            out['ended_with'] = _variables(entry.get('ended_with'))
        place = entry.get('place')
        if state == IN_PROGRESS and isinstance(place, dict) and isinstance(place.get('state'), str):
            out['place'] = {'state': place['state'], 'variables': _variables(place.get('variables'))}
        return out

    def save(self):
        self.file.data = {'last': self.last, 'episodes': self.episodes}
        self.file.write()

    # ---- reading ---------------------------------------------------------
    def state_of(self, episode):
        entry = self.episodes.get(episode.id)
        return entry['state'] if entry else NEW

    def locked(self, episode):
        """Locked until the episode before it is completed; the Prologue and Holiday Party
        never are."""
        if not episode.locked_at_first or not episode.locked_by:
            return False
        before = self.story.episodes.get(episode.locked_by)
        return before is None or self.state_of(before) != COMPLETED

    def start_variables(self, episode):
        """What a new start of the episode begins with: the variables the episode that opens
        it ended with, or nothing for the Prologue and Holiday Party."""
        if episode.locked_by:
            before = self.episodes.get(episode.locked_by)
            if before and before['state'] == COMPLETED:
                return dict(before.get('ended_with', {}))
        return {}

    def began_with(self, episode):
        entry = self.episodes.get(episode.id)
        return dict(entry['began_with']) if entry else self.start_variables(episode)

    def place(self, episode):
        """(state name, variables before it) to continue the episode from, or None."""
        entry = self.episodes.get(episode.id)
        if not entry or 'place' not in entry or entry['place']['state'] not in self.story.states:
            return None
        return entry['place']['state'], dict(entry['place']['variables'])

    def continue_episode(self):
        """The episode the main menu's Continue goes back to, or None."""
        episode = self.story.episodes.get(self.last) if self.last else None
        if episode is not None and self.place(episode) is not None:
            return episode
        return None

    # ---- for the agent profile (game/profile.py) ---------------------------
    def mission_chain(self):
        """Mission 1's episodes in story order, each opening the next: the Prologue to
        Signum Cygni. Holiday Party stands apart."""
        chain = []
        episode = next((e for e in self.story.playable_episodes()
                        if not e.locked_by and self.story.next_episode(e) is not None), None)
        while episode is not None and episode not in chain:
            chain.append(episode)
            episode = self.story.next_episode(episode)
        return chain

    def furthest_episode(self):
        """The furthest episode of the mission started or finished, or None."""
        reached = [e for e in self.mission_chain() if self.state_of(e) != NEW]
        return reached[-1] if reached else None

    def completed_count(self):
        return sum(1 for e in self.story.playable_episodes() if self.state_of(e) == COMPLETED)

    def mission_variables(self):
        """The story so far: where the furthest episode was left, or how it ended. Holiday
        Party is left out, since it resets its own variables and uses none of the others'."""
        episode = self.furthest_episode()
        if episode is None:
            return {}
        entry = self.episodes[episode.id]
        if entry['state'] == COMPLETED:
            return dict(entry.get('ended_with', {}))
        place = self.place(episode)
        return place[1] if place else dict(entry['began_with'])

    # ---- writing ---------------------------------------------------------
    def begin(self, episode, variables):
        """A fresh start of the episode, from its beginning."""
        self.episodes[episode.id] = {'state': IN_PROGRESS, 'began_with': dict(variables)}
        self.last = episode.id
        self.save()
        log.info('%s begun', episode.title)

    def save_place(self, episode, state_name, variables):
        """The player has reached ``state_name``, which was entered with ``variables``."""
        entry = self.episodes.setdefault(episode.id, {'state': IN_PROGRESS,
                                                      'began_with': dict(variables)})
        entry['state'] = IN_PROGRESS
        entry.pop('ended_with', None)
        entry['place'] = {'state': state_name, 'variables': dict(variables)}
        self.last = episode.id
        self.save()

    def complete(self, episode, variables):
        entry = self.episodes.setdefault(episode.id, {'began_with': {}})
        entry['state'] = COMPLETED
        entry['ended_with'] = dict(variables)
        entry.pop('place', None)
        if self.last == episode.id:
            self.last = None
        self.save()
        log.info('%s completed', episode.title)

    def restart(self, episode):
        """Restart or Replay: the episode starts again with what it began with, and every
        episode after it in the mission goes back to locked and not played, as the
        original's warning says. Holiday Party, opened by none, is never touched by
        another's restart."""
        began = self.began_with(episode)
        erased = []
        later = self.story.next_episode(episode)
        while later is not None:
            if self.episodes.pop(later.id, None) is not None:
                erased.append(later.title)
            if self.last == later.id:
                self.last = None
            later = self.story.next_episode(later)
        self.episodes[episode.id] = {'state': IN_PROGRESS, 'began_with': began}
        self.last = episode.id
        self.save()
        log.info('%s restarted%s', episode.title,
                 ', erasing %s' % ', '.join(erased) if erased else '')
        return began
