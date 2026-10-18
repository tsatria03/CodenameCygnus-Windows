"""The game's main loop: the window, the keys, the timers and the stack of screens.

``CodenameCygnus.py`` builds an ``App`` and runs it. Every frame, sixty a second, it:

1. reads the window's events: closing the window quits, losing the keyboard tells the top
   screen (the story pauses), and a key goes to the top screen;
2. runs the timers that are due (platform/runloop.py);
3. draws the top screen's text in the window, for a sighted helper.

F1 opens the key bindings screen from anywhere, and the timers are held while it is open,
so a timed choice keeps the seconds it had (aidocks/plans/foundation_plan.md).
"""
from __future__ import annotations

import logging
import os

from . import paths
from .platform.audio import Audio
from .platform.keymap import KeyMap, mods_from_pygame
from .platform.runloop import RunLoop
from .platform.settings import Settings
from .platform.speech import Speech
from .ui.keybind_screen import KeyBindScreen
from .ui.screens import ScreenStack

log = logging.getLogger('app')

TITLE = 'Codename Cygnus'
WINDOW_SIZE = (800, 500)
FPS = 60
#: The window's text, in lines from the top; the rest is cut.
MAX_LINES = 22


class App:
    def __init__(self, options, speech=None, settings=None, keymap=None, loop=None, audio=None):
        self.options = options
        self.speech = speech or Speech.shared()
        self.settings = settings or Settings.shared()
        self.keymap = keymap or KeyMap.shared()
        self.loop = loop or RunLoop.main()
        # The sound device opens in run(), once pygame is started (aidocks/plans/audio_plan.md).
        self.audio = audio or Audio(self.settings)
        self.stack = ScreenStack()
        self.running = True
        self.debug = False
        # Debug mode is for source runs only: --debug turns it on for one run, and the
        # Settings row turns it on or off for good.
        self.set_debug(bool(options.debug or self.settings.get('debug')), remember=False)

    # ---- debug mode -----------------------------------------------------
    def set_debug(self, on, remember=True):
        """Turn debug mode on or off. Never on in a built game."""
        on = bool(on) and not paths.FROZEN
        self.debug = on
        self.keymap.debug = on
        if remember and self.settings.get('debug') != on:
            self.settings.set('debug', on)
        log.info('debug mode %s', 'on' if on else 'off')

    # ---- running --------------------------------------------------------
    def quit(self):
        self.running = False

    def open_key_bindings(self):
        if isinstance(self.stack.top, KeyBindScreen):
            return
        self.loop.hold()
        self.stack.push(KeyBindScreen(self))

    def key_down(self, key, mods):
        top = self.stack.top
        if key == 'f1' and not mods and not isinstance(top, KeyBindScreen):
            self.open_key_bindings()
            return
        if top is not None:
            top.handle_key(key, mods)
            if top is not self.stack.top and isinstance(top, KeyBindScreen):
                self.loop.resume()          # the F1 screen just closed

    def run(self, first_screen, pygame):
        """The main loop. Returns when the game quits or the last screen closes."""
        os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
        pygame.display.init()
        pygame.font.init()
        screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption(TITLE)
        font = pygame.font.SysFont('consolas', 18) or pygame.font.Font(None, 22)
        clock = pygame.time.Clock()
        if not self.audio.ok:
            self.audio.open(pygame)
        if self.options.exit_after:
            self.loop.after(self.options.exit_after, self.quit)
            log.info('quitting by itself after %s seconds', self.options.exit_after)
        self.stack.push(first_screen)
        try:
            while self.running and not self.stack.empty:
                for event in pygame.event.get():
                    self.handle_event(event, pygame)
                if self.stack.top is not None:
                    self.stack.top.update()
                self.audio.update()
                self.loop.pump()
                self.draw(screen, font, pygame)
                clock.tick(FPS)
        finally:
            self.stack.clear()
            self.audio.close()
            pygame.display.quit()

    def handle_event(self, event, pygame):
        if event.type == pygame.QUIT:
            self.quit()
        elif event.type == getattr(pygame, 'WINDOWFOCUSLOST', None):
            if self.stack.top is not None:
                self.stack.top.focus_lost()
        elif event.type == getattr(pygame, 'WINDOWFOCUSGAINED', None):
            if self.stack.top is not None:
                self.stack.top.focus_gained()
        elif event.type == pygame.KEYDOWN:
            self.key_down(pygame.key.name(event.key), mods_from_pygame(event.mod, pygame))

    def draw(self, screen, font, pygame):
        screen.fill((0, 0, 0))
        lines = self.stack.top.lines() if self.stack.top is not None else []
        lines = list(lines)[:MAX_LINES - 2]
        if self.speech.last:
            lines += ['', self.speech.last]
        y = 10
        for line in lines:
            if line:
                screen.blit(font.render(str(line), True, (230, 230, 230)), (12, y))
            y += font.get_linesize()
        pygame.display.flip()
