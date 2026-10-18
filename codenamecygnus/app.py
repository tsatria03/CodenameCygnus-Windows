"""The game's main loop: the window, the keys, the timers and the stack of screens.

``CodenameCygnus.py`` builds an ``App`` and runs it. Every frame, sixty a second, it:

1. reads the window's events: closing the window quits, losing the keyboard tells the top
   screen (the story pauses), and a key goes to the top screen;
2. runs the timers that are due (platform/runloop.py);
3. draws the top screen's text in the window, for a sighted helper.

F1 opens the key bindings screen from anywhere, and the timers are held while it is open,
so a timed choice keeps the seconds it had (aidocks/plans/foundation_plan.md).

Holding a key down presses it again and again, but only where the top screen says that
key repeats (``Screen.repeats``), such as the 5-second skips and the volume keys during an
episode (the dev, 2026-10-17: "make it so you can hold left/right/page up/down/shift
home/end in the main story for seaking and volume changes"). Every other key fires once
however long it is held. The repeat is the game's own, not pygame's, which would repeat
every key.
"""
from __future__ import annotations

import logging
import os

from . import paths
from .platform.audio import Audio
from .platform import runloop
from .platform.keymap import MODIFIER_KEYS, KeyMap, mods_from_pygame
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
#: The interface sounds in game/data/audio/others/interface/, by when they play, as the
#: original played them from CCStyleManager (aidocks/plans/menus_plan.md).
SOUNDS = {
    'play': '1930Radio A',      # starting or continuing an episode (playPlaySound)
    'back': '1930Radio A',      # going back with Escape (playBackButton)
    'episodes': '1930Radio A',  # opening Episodes (playMissionsVCSound)
    'profile': '1930Radio B',   # opening the agent profile (playProfileVCSound)
    'restart': '1930Radio C',   # restarting an episode (playRestartSound)
    'credits': '1930Radio C',   # opening Credits, in place of Info (playInfoVCSound)
    'skip': 'PushButton D',     # skipping with S (playSkipButton)
    # Download Mission 1, in place of opening the Store (playStoreVCSound; the dev,
    # 2026-10-18: "This should play if you click on the download button").
    'download': '1930Radio D',
    'open': 'Sound A',          # opening any other screen (playViewControllerSound)
}
#: Seconds a key is held before it starts repeating, and between repeats.
REPEAT_DELAY = 0.4
REPEAT_EVERY = 0.15


class App:
    def __init__(self, options, speech=None, settings=None, keymap=None, loop=None, audio=None,
                 listener=None):
        self.options = options
        # Speech recognition's listener, made at the first choice listened for
        # (aidocks/plans/speech_recognition_plan.md), and whether the microphone's trouble
        # has been said this session.
        self._listener = listener
        self.microphone_warned = False
        self.speech = speech or Speech.shared()
        self.settings = settings or Settings.shared()
        self.keymap = keymap or KeyMap.shared()
        self.loop = loop or RunLoop.main()
        # The sound device opens in run(), once pygame is started (aidocks/plans/audio_plan.md).
        self.audio = audio or Audio(self.settings)
        self.stack = ScreenStack()
        self.running = True
        self.held = None            # [key, mods, when it next repeats] for a key that repeats
        self.pygame = None          # pygame, once run() has opened the window
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
        self.retitle()
        if remember and self.settings.get('debug') != on:
            self.settings.set('debug', on)
        log.info('debug mode %s', 'on' if on else 'off')

    def window_title(self):
        """ "Codename Cygnus", or "Codename Cygnus (debug)" in debug mode (the dev,
        2026-10-18: "When you enable debug from the source, make it so the window title
        changes")."""
        return '%s (debug)' % TITLE if self.debug else TITLE

    def retitle(self):
        """Give the window its title, at once, once there is a window."""
        if self.pygame is not None:
            self.pygame.display.set_caption(self.window_title())

    @property
    def listener(self):
        if self._listener is None:
            from .platform.listener import Listener
            self._listener = Listener()
        return self._listener

    # ---- interface sounds -----------------------------------------------
    def play_sound(self, kind):
        """One of the interface sounds, by when it plays, such as 'back' or 'open'."""
        from .game.recordings import Recordings
        self.audio.play_menu(Recordings.shared().menu_sound(SOUNDS[kind]))

    # ---- running --------------------------------------------------------
    def quit(self):
        self.running = False

    def open_key_bindings(self):
        if isinstance(self.stack.top, KeyBindScreen):
            return
        self.loop.hold()
        self.stack.push(KeyBindScreen(self))

    def key_down(self, key, mods, now=None):
        if key in MODIFIER_KEYS:
            return                          # Shift and the rest only go with another key
        self.held = None
        top = self.stack.top
        if key == 'f1' and not mods and not isinstance(top, KeyBindScreen):
            self.open_key_bindings()
            return
        if top is not None:
            top.handle_key(key, mods)
            if top is not self.stack.top and isinstance(top, KeyBindScreen):
                self.loop.resume()          # the F1 screen just closed
        top = self.stack.top
        if top is not None and top.repeats(key, mods):
            now = runloop.clock() if now is None else now
            self.held = [key, list(mods), now + REPEAT_DELAY]

    def key_up(self, key):
        """A key let go: it stops repeating, as it does when a modifier held with it is."""
        if self.held is not None and (key == self.held[0] or key in MODIFIER_KEYS):
            self.held = None

    def repeat_keys(self, now=None):
        """Called once a frame: press the held key again when it is due."""
        if self.held is None:
            return
        now = runloop.clock() if now is None else now
        key, mods, due = self.held
        if now < due:
            return
        top = self.stack.top
        if top is None or not top.repeats(key, mods):
            self.held = None                # the story moved on, say to a choice
            return
        self.held[2] = now + REPEAT_EVERY
        top.handle_key(key, mods)

    def run(self, first_screen, pygame, on_top=None):
        """The main loop. Returns when the game quits or the last screen closes.

        ``on_top``, such as an episode started with ``--episode``, opens instead of
        ``first_screen``, which waits underneath until it closes."""
        os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
        pygame.display.init()
        pygame.font.init()
        screen = pygame.display.set_mode(WINDOW_SIZE)
        self.pygame = pygame
        self.retitle()
        font = pygame.font.SysFont('consolas', 18) or pygame.font.Font(None, 22)
        clock = pygame.time.Clock()
        if not self.audio.ok:
            self.audio.open(pygame)
        if self.options.exit_after:
            self.loop.after(self.options.exit_after, self.quit)
            log.info('quitting by itself after %s seconds', self.options.exit_after)
        if on_top is not None:
            self.stack.put_under(first_screen)
            self.stack.push(on_top)
        else:
            self.stack.push(first_screen)
        try:
            while self.running and not self.stack.empty:
                for event in pygame.event.get():
                    self.handle_event(event, pygame)
                self.repeat_keys()
                if self.stack.top is not None:
                    self.stack.top.update()
                self.audio.update()
                self.loop.pump()
                self.draw(screen, font, pygame)
                clock.tick(FPS)
        finally:
            self.stack.clear()
            if self._listener is not None:
                self._listener.stop()
            self.audio.close()
            pygame.display.quit()

    def handle_event(self, event, pygame):
        if event.type == pygame.QUIT:
            self.quit()
        elif event.type == getattr(pygame, 'WINDOWFOCUSLOST', None):
            self.held = None                # its key-up will go to another window
            if self.stack.top is not None:
                self.stack.top.focus_lost()
        elif event.type == getattr(pygame, 'WINDOWFOCUSGAINED', None):
            if self.stack.top is not None:
                self.stack.top.focus_gained()
        elif event.type == pygame.KEYDOWN:
            self.key_down(pygame.key.name(event.key), mods_from_pygame(event.mod, pygame))
        elif event.type == pygame.KEYUP:
            self.key_up(pygame.key.name(event.key))

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
