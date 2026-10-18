"""The recordings the player has heard to their end, in ``saves/heard.json``.

Section 3 of aidocks/plans/story_engine_plan.md. S skips only across recordings heard
before, so a stray press never skips new story:

* A recording counts as heard once it has reached its end, whether played through or
  skipped to the end with Right. Starting it is not enough.
* It is remembered for good, across every replay and restart (aidocks/plans/saves_plan.md).
* It is kept by its story name without the extension, in lower case, as
  ``recordings.story_key`` gives it, such as ``016f_contactmark``.
* The file is written each time a new one is heard, which is at most once a recording.
"""
from __future__ import annotations

import logging

from .. import paths
from ..platform.files import JsonFile
from .recordings import story_key

log = logging.getLogger('heard')


class Heard:
    _shared = None

    @classmethod
    def shared(cls):
        if cls._shared is None:
            cls._shared = Heard()
        return cls._shared

    def __init__(self, path=None):
        self.file = JsonFile(path or paths.user_path('saves', 'heard.json'))
        saved = self.file.data.get('heard')
        self.names = {n for n in saved if isinstance(n, str)} if isinstance(saved, list) else set()
        if self.file.recovered:
            self.save()

    def __contains__(self, file_name):
        return story_key(file_name) in self.names

    def add(self, file_name):
        """Note a recording as heard to its end. True when it is new."""
        key = story_key(file_name)
        if key in self.names:
            return False
        self.names.add(key)
        self.save()
        return True

    def save(self):
        self.file.data = {'heard': sorted(self.names)}
        self.file.write()
