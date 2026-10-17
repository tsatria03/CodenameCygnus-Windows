---
name: project_dev_tasks
description: "The developer tasks (repository, tools, tests, build and docs), open and finished, kept out of docks/todo list.txt, which is for players only."
metadata:
  node_type: memory
  type: project
---

The developer tasks, which `docks/todo list.txt` leaves out because it ships to players ([[feedback_todo_list_format]]). Same style: newest at the top, one or two short sentences each. An item moves to Finished only when the dev confirms it.

## Unfinished

- Add speech recognition for choices, with a setting to turn it on or off, when the port is built ([[project_speech_recognition]]). Needs a plan first.
- Adapt the build script and the release script for Windows only, without the GitHub Actions workflow and its CI steps ([[project_windows_only]]). Needs a plan first.

## Finished

- The voiced episode previews are out of the repository and its history, ignored in `game/data/audio/other/teasers/` (2026-10-17).
- The mission recordings are out of the repository and its history, ignored from the first commit on (2026-10-17).
