# CLAUDE.md

This file guides Claude Code when it works in this repository. **It is a lean dispatcher.** It says what the project is and how it is laid out, then points to focused memory files (`[[name]]`) for the detail. When you start work in an area, read its linked memory first.

**Memory location:** all memory files (the `[[name]]` links and the `MEMORY.md` index) live in the repo's **`aidocks/`** folder, in two folders: **`aidocks/plans/`** holds every plan, planned or complete, as `aidocks/plans/<name>_plan.md` with no `project_` prefix, and a finished plan stays there, marked finished; **`aidocks/general/`** holds every other note, as `aidocks/general/<name>.md`. A `[[name]]` link resolves to whichever of the two holds it ([[feedback_completed_projects]]). Read memory from there and write new or updated memory there, never to the `~/.claude` memory store. `aidocks/general/MEMORY.md` is the index, so add a one-line pointer there for every new memory. Keep this file under 40,000 characters and move detail into memory ([[feedback_memory_in_aidocks]]).

## What this is

A Windows port of **Codename Cygnus** (`net.reactivestudios.codenamecygnus` 1.3.2, Reactive Studios), an iOS interactive radio drama no longer on the App Store. Each episode is a voiced spy story, and the player's choices shape their agent's personality and the story. The original took choices by voice; the port is for the keyboard and screen readers.

- **A solo project.** tsatria03 makes it alone, with no contributors, until the dev says otherwise ([[project_solo]]).
- **Windows only.** No Linux or macOS, and no GitHub Actions release workflow ([[project_windows_only]]).
- **Python only**, in the `codenamecygnus/` package, with pygame and Prism ([[project_python_only]]).
- **Developer tasks**, open and finished, are in [[project_dev_tasks]].
- **The game is data-driven.** Each episode is a graph of states (voice, background and decision audio, a script) joined by manual choices, automatic transitions, conditions and timed choices. The story is built from the v53 graph in the app's database, not the bundled v1 JSON, and every player starts from scratch ([[project_story_data_source]]).
- **Status:** studied and laid out; no game code yet.

## Layout

- **`game/`**: the original app bundle, never written to. `game/data/text/` holds the three bundled descriptors (missions, resources, states v1). `game/CodenameCygnus.sqlite` with its `-wal` holds the story v53. `game/data/audio/other/` holds 66 shared recordings, and `game/data/audio/missions/` the 756 episode recordings, which are gitignored and were removed from history on 2026-10-17. Every recording is MP3, converted by the dev from the original AAC `.m4a`; the story data still says `.m4a` ([[project_python_only]]). Don't move, rename, convert or delete sound files unless the dev asks.
- **`codenamecygnus/`**: the port's Python package, still empty.
- **`vendor/nvda/`**: `nvdaControllerClient64.dll` (x64) and its license.
- **`docks/`**: the documents a player reads: `readme.txt`, `changelog.txt` and `todo list.txt` ([[feedback_changelog]], [[feedback_todo_list_format]]).
- **`analysis/`**, **`tools/`**: notes, data and tools for reading the original. Empty so far.
- **`tests/case/`** and **`tests/interact/`**: the tests, and the tools played by ear. Empty so far.
- **`user/`** is gitignored private reference material. Read it, but never edit it. Never name the dev's other games kept in it, in any of this repo's files ([[feedback_no_other_games]]).
- **`New File*.txt`** at the root is the dev's private scratchpad. It is gitignored; never read, edit, flag or delete it.

## Working here

- **The dev runs and builds, not Claude.** Ask before running the game or anything that plays sound or speaks ([[feedback_dont_run_or_build]]).
- **Plans first:** an agreed plan goes into its own note in `aidocks/plans/` before any code, and is marked finished only once the dev says it works ([[feedback_record_plans_first]], [[feedback_completed_projects]]).
- **Committing and pushing:** commit finished work without asking; ask about pushing only once 10 or more commits are unpushed; "commit/push" means both; history rewrites need a go-ahead ([[feedback_git_commits]]). Name people by GitHub username only ([[feedback_use_github_usernames]]).
- **Questions:** a question from the dev is a check, answered in chat ([[feedback_questions_are_checks]]). Ask one question per reply, in plain text ([[feedback_one_question_at_a_time]], [[feedback_no_question_pickers]]).
- **Releases** are never recorded in notes or the README ([[feedback_no_release_records]]).
- **Who you're working with:** [[user_screen_reader]]. The dev uses NVDA, so prefer lists and short lines, never wide tables, and never make noise from tools.

`CLAUDE.md` and `aidocks/` are committed, not gitignored.
