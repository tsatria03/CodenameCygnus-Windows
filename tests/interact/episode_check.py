"""Choose an episode and play it by ear, before the real menus exist. Not a test.

    python tests/interact/episode_check.py

It opens on a list of Mission 1's eight episodes, every one open. Up and Down move, Enter
starts the one you are on, and Escape quits. During the episode the game's own keys work
(aidocks/plans/story_engine_plan.md), and Return to menu in the pause menu, or Enter at
the end of the episode, comes back to the list.

    Up and Down     the choices, once they are read
    Enter, 1 to 9   choose
    C               the choices again
    Space           pause and resume
    R               the recording again
    Left and Right  5 seconds back or forward
    H               the scene heading
    Escape          the pause menu
    F1              the key bindings

It keeps its own save, in %APPDATA%\\CodenameCygnus\\episode_check, so your volumes and
keys in the game are not changed; its log is logs\\log.txt there.
"""
import logging
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
os.environ.setdefault('CYGNUS_USER_DIR',
                      os.path.join(os.environ.get('APPDATA') or os.path.expanduser('~'),
                                   'CodenameCygnus', 'episode_check'))
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

import pygame  # noqa: E402

from codenamecygnus import paths  # noqa: E402
from codenamecygnus.app import App  # noqa: E402
from codenamecygnus.game.episode_screen import EpisodeScreen  # noqa: E402
from codenamecygnus.game.story import Story  # noqa: E402
from codenamecygnus.ui.menu import Menu, Row  # noqa: E402


class EpisodeChooser(Menu):
    name = 'episode check'
    title = 'Episode check. Choose an episode.'

    def __init__(self, app, story):
        super().__init__(app)
        self.story = story

    def rows(self):
        return [Row('Episode %d, %s' % (e.number, e.title), lambda e=e: self.play(e))
                for e in self.story.playable_episodes()]

    def play(self, episode):
        self.stack.push(EpisodeScreen(self.app, episode, story=self.story))

    def back(self):
        self.app.quit()


def main():
    handler = logging.FileHandler(os.path.join(paths.logs_dir(), 'log.txt'), 'w', encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-7s %(name)-8s %(message)s',
                                           '%H:%M:%S'))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)
    options = types.SimpleNamespace(debug=False, episode=None, state=None, verbose=False,
                                    exit_after=None)
    app = App(options)
    app.run(EpisodeChooser(app, Story.shared()), pygame)
    logging.shutdown()
    return 0


if __name__ == '__main__':
    sys.exit(main())
