"""Finding a recording by the name the story gives it.

The story names every recording as the original did, such as ``016F_contactMark.m4a``.
The dev converted them all to MP3 and sorted them into folders (aidocks/general/project_python_only.md),
so a name is looked up as:

* the name with ``.mp3`` in place of ``.m4a``, in any letter case;
* anywhere under ``game/data/audio/``, whatever folder it is in, since each name appears once;
* a preview, ``m1eN_teaser``, as ``missions/m1/teasers/m1eN.mp3``, the name without
  ``_teaser``.

Mission 1's recordings come from the loose files under ``game/data/audio/missions/`` when
any are there, which only a source run has; otherwise from the encrypted pack, m1.dat
(game/pack.py), the same in a build and in a source run whose missions folder was deleted
(aidocks/plans/build_release_plan.md). The menu sounds are always loose files. A
``Recording`` is what either gives the audio: a path, or bytes and a name.
"""
from __future__ import annotations

import logging
import os

from .. import paths

log = logging.getLogger('recordings')

#: The folder under game/data/audio that holds the mission recordings, loose.
MISSIONS = 'missions'


def story_key(file_name):
    """The name a story file name is looked up by: lower case, no extension, no _teaser."""
    name = os.path.splitext(os.path.basename(file_name))[0].lower()
    if name.endswith('_teaser'):
        name = name[:-len('_teaser')]
    return name


class Recording:
    """One recording to play: a file on disk, or bytes read from a pack."""

    def __init__(self, name, path=None, data=None):
        self.name = name
        self.path = path
        self.data = data

    def __repr__(self):
        return 'Recording(%r)' % self.name


class Recordings:
    """Every MP3 under one folder, by its story key, and the pack's when the folder has no
    mission recordings of its own."""

    _shared = None

    @classmethod
    def shared(cls):
        if cls._shared is None:
            cls._shared = Recordings()
        return cls._shared

    def __init__(self, folder=None, pack='find'):
        self.folder = folder or paths.audio()
        self.index = {}
        self.twice = {}
        self.loose_missions = 0
        missions = os.path.join(self.folder, MISSIONS) + os.sep
        for root, dirs, files in os.walk(self.folder):
            dirs.sort()
            for f in sorted(files):
                if not f.lower().endswith('.mp3'):
                    continue
                key = f[:-4].lower()
                path = os.path.join(root, f)
                if key in self.index:
                    self.twice.setdefault(key, [self.index[key]]).append(path)
                else:
                    self.index[key] = path
                    if path.startswith(missions):
                        self.loose_missions += 1
        for key, where in self.twice.items():
            log.warning('the recording %s is on disk more than once; using %s', key, where[0])
        log.info('%d recordings found under %s', len(self.index), self.folder)
        self.pack = None
        if not self.loose_missions:
            if pack == 'find':
                from .pack import find_pack
                pack = find_pack()
            self.use_pack(pack)

    @property
    def has_missions(self):
        """Whether Mission 1's recordings are here, loose or in the pack."""
        return bool(self.loose_missions or self.pack is not None)

    def use_pack(self, pack):
        """Read the mission recordings from ``pack`` from now on, such as one just downloaded."""
        self.pack = pack
        if pack is not None:
            log.info('mission recordings from the pack %s', pack.path)
        elif not self.loose_missions:
            log.info('no mission recordings: neither loose files nor a pack')

    def find(self, file_name):
        """The ``Recording`` for a story file name, or None when there is no such file."""
        key = story_key(file_name)
        path = self.index.get(key)
        if path is not None:
            return Recording(key, path=path)
        if self.pack is not None and key in self.pack:
            try:
                return Recording(key, data=self.pack.read(key))
            except Exception:
                log.exception('could not read %s from the pack', key)
                return None
        log.warning('no recording for %s', file_name)
        return None

    def menu_sound(self, name):
        """One of the interface sounds in ``others/menu``, such as ``1930Radio A``."""
        return self.find(name + '.mp3')
