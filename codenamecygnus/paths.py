"""Where things are: the game's own data, the vendored libraries and the save folder.

From source, everything is found from the repository's root. In a build made by
compiler.py, PyInstaller unpacks the code to ``sys._MEIPASS`` and the game's data
sits beside the executable, or inside it for a single exe (aidocks/plans/build_release_plan.md).

The game never writes to ``game/``. Everything it remembers goes in
``%APPDATA%\\CodenameCygnus`` (aidocks/plans/saves_plan.md), or wherever
``CYGNUS_USER_DIR`` points, which the tests set to a throwaway folder so they never
touch a player's save.
"""
from __future__ import annotations

import logging
import os
import sys

log = logging.getLogger('paths')

FROZEN = getattr(sys, 'frozen', False)
if FROZEN:
    ROOT = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.executable)))
    EXE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EXE_DIR = ROOT

VENDOR = os.path.join(ROOT, 'vendor')
NVDA_DLL = os.path.join(VENDOR, 'nvda', 'nvdaControllerClient64.dll')

#: The save folder's name under %APPDATA% (aidocks/plans/foundation_plan.md).
SAVE_FOLDER = 'CodenameCygnus'
#: Set by the tests to a throwaway folder, never by the game.
USER_DIR_ENV = 'CYGNUS_USER_DIR'


def game() -> str:
    """The folder holding the game's data: beside the executable in a folder build, inside
    it in a single exe, or the repository's own ``game/`` from source."""
    for folder in (os.path.join(EXE_DIR, 'game'), os.path.join(ROOT, 'game')):
        if os.path.isdir(folder):
            return folder
    raise SystemExit("Codename Cygnus's game data was not found. Looked in:\n  %s\n  %s"
                     % (os.path.join(EXE_DIR, 'game'), os.path.join(ROOT, 'game')))


def text() -> str:
    """``game/data/text``: missions.json, resources.json and states.json."""
    return os.path.join(game(), 'data', 'text')


def audio() -> str:
    """``game/data/audio``: the menu sounds, and from source the loose mission recordings."""
    return os.path.join(game(), 'data', 'audio')


def user_dir() -> str:
    """The save folder, made if it is not there yet."""
    folder = os.environ.get(USER_DIR_ENV)
    if not folder:
        base = os.environ.get('APPDATA') or os.path.expanduser('~')
        folder = os.path.join(base, SAVE_FOLDER)
    os.makedirs(folder, exist_ok=True)
    return folder


def user_path(*parts: str) -> str:
    """A path inside the save folder, such as ``user_path('config', 'settings.json')``."""
    return os.path.join(user_dir(), *parts)


def logs_dir() -> str:
    folder = user_path('logs')
    os.makedirs(folder, exist_ok=True)
    return folder
