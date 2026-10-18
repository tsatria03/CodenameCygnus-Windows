---
name: foundation_plan
description: "Plan 2 of 8: the codenamecygnus package, the CodenameCygnus.py entry script and screen loop, save-folder paths, logging and crash files, screen reader speech and the timer loop, with a debug mode, five command-line options and the speech interruption rules. Status: finished."
metadata:
  node_type: memory
  type: project
---

**Status: finished,** confirmed by the dev on 2026-10-17 after trying it by ear ("It works. ... Also the keys are now saved correctly."). Changes that came of it: menu rows are no longer read with their place, such as "1 of 2" (the dev: "The menu position readouts should be disabled"), and Left and Right move through a menu and the F1 screen as Up and Down do, both wrapping round (the dev: "please enable menu wrapping, and left/right arrow navigation"). Built 2026-10-17 (the dev: "Yes"). Until [[menus_plan]] is built, the game opens on a small stand-in main menu, Settings and Quit (`codenamecygnus/game/stand_in_menu.py`), so its speech, keys and window can be tried by ear; the menus plan replaces it. `--episode` and `--state` are read but wait for [[story_engine_plan]]; until then the log says they are ignored.

**What was built:**
- `CodenameCygnus.py`: the options, `logs/log.txt` and `log.old.txt`, and `logs/crash.txt` with the error spoken.
- `codenamecygnus/paths.py`: the game's data, the NVDA client, and the save folder, `%APPDATA%\CodenameCygnus` or `CYGNUS_USER_DIR`.
- `codenamecygnus/app.py`: the 60-frame main loop, keys to the top screen, F1 from anywhere with the timers held, focus loss passed to the top screen, and the window's text.
- `codenamecygnus/platform/`: `speech.py` (NVDA, then Prism, then a Windows voice; `CYGNUS_SILENT` for tests), `runloop.py` (`after`, `every`, `hold`, `resume`, `remaining`), `files.py` (the safe JSON file), `settings.py` (`config/settings.json`, every setting written from the first start, bad values put back) and `keymap.py` (the agreed keys, a binding being one key with exact modifiers, `config/keys.json`).
- `codenamecygnus/ui/`: `screens.py` (the screen stack), `menu.py` (the spoken menu), `keybind_screen.py` (F1) and `settings_screen.py` (the Debug mode row, source runs only).
- `tests/case/`: 59 tests in 8 files, all passing on 2026-10-17, each importing `_quiet.py` first; `tests/suite.py` runs them all, writing `tests/results/` (gitignored).
- **The key map is simpler than the reference material's:** this game has no held-key chords, only modifiers, so a key fires the moment it is pressed, with no wait to tell a chord apart.
- **Master volume:** Shift+Home raises it and Shift+End lowers it, Home sitting above End as Page Up sits above Page Down (the dev confirmed it, 2026-10-17: "Yes.").

Plan 2 of 8 ([[story_export_plan]] lists the order). Everything else stands on this: [[audio_plan]], [[story_engine_plan]], [[menus_plan]], [[saves_plan]] and [[speech_recognition_plan]] all use its paths, speech, timers and screen loop.

## Decided

- **The name is "Codename Cygnus" everywhere** (the dev, 2026-10-17: "I like that. That was the name I was going to suggest."):
  - the window title: Codename Cygnus
  - the entry script: `CodenameCygnus.py` at the repo root
  - the built game: `CodenameCygnus.exe`
  - the save folder: `%APPDATA%\CodenameCygnus`
- **The code lives in `codenamecygnus/`**, split as the reference material in `user/` splits it:
  - `codenamecygnus/platform/`: the parts that talk to Windows (speech, timers, paths, settings files)
  - `codenamecygnus/ui/`: keyboard input, menus and screens
  - `codenamecygnus/game/`: the story and what is particular to Codename Cygnus
- **Windows only, Python 3.12 or newer, 64-bit** ([[project_windows_only]], [[project_python_only]]).
- **Adapted from the reference material in `user/`**, renamed and cut down to Windows, never naming where it came from ([[feedback_no_other_games]]):
  - **Speech:** NVDA through its own client first, then any other screen reader through Prism, then a Windows voice. It has `speak(text, interrupt)` and `stop()`, rechecks which screen reader is running every few seconds, and loads Prism only when NVDA is not running.
  - **Timer loop:** delayed calls and repeating timers pumped once a frame, on wall-clock time, with `hold()` and `resume()` that shift every waiting timer by the pause. Automatic transitions, the 7-second timed choices and the subtitle pacing all run on it.
  - **Settings files:** short JSON files written safely (a temporary file first, then a `.bak` of the old one, then a swap), with a damaged file kept as `.damaged` and the backup loaded instead.
  - **Logs:** every run writes `logs/log.txt` in the save folder and keeps the run before as `log.old.txt`. An error that stops the game writes `logs/crash.txt` and is spoken aloud, so a blind player knows why the game closed.
  - **Screen loop:** a stack of screens. A screen can open another on top, close itself, or replace the menu. Switching away from the window pauses the story.
  - **F1 key bindings screen:** every action rebindable, spoken in full, with F1 and Escape fixed so there is always a way out.
- **A debug mode, for source runs only** (the dev, 2026-10-17: "Yes, a debug mode would be super good"). It is turned on with `--debug` and never exists in a built game. Its keys are for testing a branching story by ear: skip the current recording, jump to any state by name, and hear the current trait scores and story flags. The exact keys are settled in [[story_engine_plan]]. **It is also a Debug mode row in Settings** (the dev, 2026-10-17: "yes"), shown only when running from source, remembered between runs, and switching debug mode on or off at once without a restart.
- **The window shows plain text for a sighted helper** (the dev, 2026-10-17: "yes"): the current menu's rows, or during an episode the scene heading, the line being spoken and the choices, as the original showed its script on screen. It is secondary: the speech and the audio are the real interface, and nothing is only in the window.
- **Five command-line options** (the dev, 2026-10-17: "agreed"):
  - `--debug` turns on debug mode.
  - `--episode ID`, such as `--episode 1.3.1`, starts that episode straight away, past the menus.
  - `--state NAME` starts at any story state, in debug mode only, to check one branch.
  - `-v` writes a more detailed log.
  - `--exit-after SECONDS` quits by itself after that many seconds, so the build test can start a built game silently and check it runs.
- **What interrupts what** (the dev, 2026-10-17: "Yes, agreed with all of that"):
  - Each move in a menu or through the choices cuts off what was being said, so fast arrowing never builds a backlog.
  - Choices are read once, after the recording that asks the question has finished.
  - A key the player presses, such as H, C or a volume change, speaks at once, cutting off earlier speech but never the story audio, which keeps playing underneath.
  - Important messages, such as "Episode complete", an error or "No microphone found", are never cut off by background events, only by the player pressing a key.
  - Speech never pauses the story. Only Space and Escape do.
- **Tests stay silent and off the real save** ([[feedback_dont_run_or_build]]): environment variables point the save at a throwaway folder and turn speech off, and every test imports the module that sets them.

## Open questions

None. Ready to build once the dev says so.
