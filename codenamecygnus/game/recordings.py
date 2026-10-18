"""Finding a recording by the name the story gives it.

The story names every recording as the original did, such as ``016F_contactMark.m4a``.
The dev converted them all to MP3 and sorted them into folders (aidocks/general/project_python_only.md),
so a name is looked up as:

* the name with ``.mp3`` in place of ``.m4a``, in any letter case;
* anywhere under ``game/data/audio/``, whatever folder it is in, since each name appears once;
* a preview, ``m1eN_teaser``, as ``missions/m1/teasers/m1eN.mp3``, the name without
  ``_teaser``.

From source the loose files are read; a built game will read the encrypted pack,
``m1.dat``, instead (aidocks/plans/build_release_plan.md). A ``Recording`` is what either
gives the audio: a path, or bytes and a name.
"""
from __future__ import annotations

import logging
import os

from .. import paths

log = logging.getLogger('recordings')


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
    """Every MP3 under one folder, by its story key."""

    _shared = None

    @classmethod
    def shared(cls):
        if cls._shared is None:
            cls._shared = Recordings()
        return cls._shared

    def __init__(self, folder=None):
        self.folder = folder or paths.audio()
        self.index = {}
        self.twice = {}
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
        for key, where in self.twice.items():
            log.warning('the recording %s is on disk more than once; using %s', key, where[0])
        log.info('%d recordings found under %s', len(self.index), self.folder)

    def find(self, file_name):
        """The ``Recording`` for a story file name, or None when there is no such file."""
        key = story_key(file_name)
        path = self.index.get(key)
        if path is None:
            log.warning('no recording for %s', file_name)
            return None
        return Recording(key, path=path)

    def menu_sound(self, name):
        """One of the interface sounds in ``others/menu``, such as ``1930Radio A``."""
        return self.find(name + '.mp3')
