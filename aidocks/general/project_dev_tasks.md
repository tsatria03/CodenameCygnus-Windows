---
name: project_dev_tasks
description: "The developer tasks (repository, tools, tests, build and docs), open and finished, kept out of docks/todo list.txt, which is for players only."
metadata:
  node_type: memory
  type: project
---

The developer tasks, which `docks/todo list.txt` leaves out because it ships to players ([[feedback_todo_list_format]]). Same style: newest at the top, one or two short sentences each. An item moves to Finished only when the dev confirms it.

## Unfinished

None.

## Finished

- `compiler.py` and `releaser.py` build and release the game for Windows only, with no GitHub Actions workflow, and Mission 1's recordings ship as the encrypted `m1.dat`, built by `tools/build_pack.py` and downloaded by the game, finishing [[build_release_plan]] (2026-10-18).
- Speech recognition for choices is built, behind its setting, with `tests/interact/SPEECH_check.py` to try it by ear, finishing [[speech_recognition_plan]] (2026-10-18).
- The agent profile, the last part of the menus, is built, finishing the menus and saves plans (2026-10-18).
- Progress is saved in `saves/progress.json` at every new state, with Continue, the episodes' states and locks, the story carried from episode to episode, and Restart and Replay erasing what came after (2026-10-18).
- The menus around the story are built: the opening, the main menu, the episode list and each episode's own screen, Settings with the three volumes, Credits, the end of an episode and the previews, with the original's interface sounds and Back first in every menu (2026-10-18).
- Debug mode's F3 prompt has cut, copy and paste through the Windows clipboard (2026-10-18).
- The story engine plays every episode: the choices in spoken order, the episode keys, S across heard recordings, debug mode's F2 to F4 and `--state`, and the 16 local achievements; `tests/interact/episode_check.py` plays any episode by ear (2026-10-18).
- The audio plays a story state's voice, background and decision loop, with pausing, skipping and the three volumes, and `tests/interact/audio_check.py` lets it be heard by ear (2026-10-17).
- The foundation is built: the entry script, speech, timers, settings and keys files, the F1 screen, logs and the silent tests (2026-10-17).
- The original's final story, missions and resources are exported as checked JSON in `game/data/text/` by `tools/export_story.py` (2026-10-17).
- The ambiences and decision sounds are out of the repository and its history, on GitHub too, kept under the gitignored `game/data/audio/missions/`; only the eight menu sounds remain (2026-10-17).
- The whole story is written as plain text in `analysis/script/`, one file per episode, by `tools/script_text.py` (2026-10-17).
- The voiced episode previews are out of the repository and its history, ignored in `game/data/audio/other/teasers/` (2026-10-17).
- The mission recordings are out of the repository and its history, ignored from the first commit on (2026-10-17).
