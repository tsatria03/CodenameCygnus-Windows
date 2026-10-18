"""Codename Cygnus for Windows.

    python CodenameCygnus.py

Options (aidocks/plans/foundation_plan.md):

    --debug               debug mode for this run (source runs only)
    --episode ID          start an episode straight away, such as --episode 1.3.1
    --state NAME          start at any story state, in debug mode only
    -v                    a more detailed log
    --exit-after SECONDS  quit by itself after that many seconds

Every run writes logs/log.txt in the save folder, %APPDATA%\\CodenameCygnus, keeping the
run before as log.old.txt. An error that stops the game writes logs/crash.txt and is
spoken, so a player who cannot see the screen knows why the game closed.
"""
from __future__ import annotations

import argparse
import datetime
import logging
import os
import platform
import sys
import time
import traceback

os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

from codenamecygnus import paths  # noqa: E402

log = logging.getLogger('cygnus')

CRASH_MESSAGE = ('Codename Cygnus has stopped because of an error. The details are in '
                 'crash.txt, in the logs folder of the game\'s save folder.')


def parse_args(argv=None):
    parser = argparse.ArgumentParser(prog='CodenameCygnus', description='Codename Cygnus for Windows')
    parser.add_argument('--debug', action='store_true', help='debug mode for this run (source runs only)')
    parser.add_argument('--episode', metavar='ID', help='start an episode straight away, such as 1.3.1')
    parser.add_argument('--state', metavar='NAME', help='start at any story state, in debug mode only')
    parser.add_argument('-v', '--verbose', action='store_true', help='a more detailed log')
    parser.add_argument('--exit-after', metavar='SECONDS', type=float,
                        help='quit by itself after that many seconds')
    return parser.parse_args(argv)


def start_log(verbose):
    """logs/log.txt for this run, keeping the run before as log.old.txt."""
    folder = paths.logs_dir()
    current = os.path.join(folder, 'log.txt')
    old = os.path.join(folder, 'log.old.txt')
    try:
        if os.path.exists(current):
            os.replace(current, old)
    except OSError:
        pass
    handler = logging.FileHandler(current, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-7s %(name)-8s %(message)s',
                                           '%H:%M:%S'))
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if verbose else logging.INFO)
    return current


def write_crash(error_text):
    """logs/crash.txt, for the last error that stopped the game."""
    path = os.path.join(paths.logs_dir(), 'crash.txt')
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write('Codename Cygnus stopped because of an error.\n')
            f.write('When: %s\n' % datetime.datetime.now().isoformat(timespec='seconds'))
            f.write('Python: %s\n' % sys.version.replace('\n', ' '))
            f.write('System: %s\n' % platform.platform())
            f.write('Running from: %s\n\n' % ('a build' if paths.FROZEN else 'source'))
            f.write(error_text)
    except OSError:
        pass
    return path


def say_why(speech, text):
    """Speak why the game is closing, and give the screen reader time to say it."""
    try:
        speech.speak(text)
        time.sleep(4)
    except Exception:
        pass


def episode_from_options(app, options):
    """The episode ``--episode`` names, ready to play, or None."""
    if not options.episode:
        return None
    from codenamecygnus.game.episode_screen import EpisodeScreen
    from codenamecygnus.game.story import Story
    episode = Story.shared().episodes.get(options.episode)
    if episode is None or not episode.playable:
        log.warning('there is no episode %s to play, so the menu opens instead', options.episode)
        return None
    return EpisodeScreen(app, episode)


def main(argv=None):
    options = parse_args(argv)
    start_log(options.verbose)
    log.info('Codename Cygnus starting, from %s', 'a build' if paths.FROZEN else 'source')
    from codenamecygnus.platform.speech import Speech
    speech = Speech.shared()
    try:
        import pygame
        from codenamecygnus.app import App
        from codenamecygnus.game.stand_in_menu import StandInMainMenu
        if options.state and not options.debug:
            log.warning('--state works only in debug mode, so it is ignored')
        elif options.state:
            log.warning('--state waits for debug mode in the story engine, so it is ignored for now')
        app = App(options, speech=speech)
        app.run(StandInMainMenu(app), pygame, on_top=episode_from_options(app, options))
        log.info('Codename Cygnus closed')
        return 0
    except SystemExit as stop:
        if isinstance(stop.code, str):              # a message to give the player, such as missing data
            log.error('%s', stop.code)
            write_crash(stop.code + '\n')
            say_why(speech, stop.code)
            return 1
        raise
    except Exception:
        text = traceback.format_exc()
        log.error('the game stopped because of an error:\n%s', text)
        write_crash(text)
        say_why(speech, CRASH_MESSAGE)
        return 1
    finally:
        logging.shutdown()


if __name__ == '__main__':
    sys.exit(main())
