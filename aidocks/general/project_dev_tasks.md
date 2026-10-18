---
name: project_dev_tasks
description: "The developer tasks (repository, tools, tests, build and docs), open and finished, kept out of docks/todo list.txt, which is for players only."
metadata:
  node_type: memory
  type: project
---

The developer tasks, which `docks/todo list.txt` leaves out because it ships to players ([[feedback_todo_list_format]]). Same style: newest at the top, one or two short sentences each. An item moves to Finished only when the dev confirms it.

## Unfinished

- Add speech recognition for choices, with a setting to turn it on or off, when the port is built ([[project_speech_recognition]]). Planned in [[speech_recognition_plan]].
- Adapt the build script and the release script for Windows only, without the GitHub Actions workflow and its CI steps ([[project_windows_only]]). Planned in [[build_release_plan]].

## Finished

- The audio plays a story state's voice, background and decision loop, with pausing, skipping and the three volumes, and `tests/interact/audio_check.py` lets it be heard by ear (2026-10-17).
- The foundation is built: the entry script, speech, timers, settings and keys files, the F1 screen, logs and the silent tests (2026-10-17).
- The original's final story, missions and resources are exported as checked JSON in `game/data/text/` by `tools/export_story.py` (2026-10-17).
- The ambiences and decision sounds are out of the repository and its history, on GitHub too, kept under the gitignored `game/data/audio/missions/`; only the eight menu sounds remain (2026-10-17).
- The whole story is written as plain text in `analysis/script/`, one file per episode, by `tools/script_text.py` (2026-10-17).
- The voiced episode previews are out of the repository and its history, ignored in `game/data/audio/other/teasers/` (2026-10-17).
- The mission recordings are out of the repository and its history, ignored from the first commit on (2026-10-17).
