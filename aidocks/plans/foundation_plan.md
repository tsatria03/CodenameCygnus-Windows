---
name: foundation_plan
description: "Plan 2 of 8: the codenamecygnus package, the CodenameCygnus.py entry script and screen loop, save-folder paths, logging and crash files, screen reader speech and the timer loop. Status: planned, questions open."
metadata:
  node_type: memory
  type: project
---

**Status: planned, questions open.** Nothing is built.

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
- **Tests stay silent and off the real save** ([[feedback_dont_run_or_build]]): environment variables point the save at a throwaway folder and turn speech off, and every test imports the module that sets them.

## Open questions

- Whether the window draws text for a sighted helper.
- The command-line options.
- The speech interruption rules: what cuts off what.
