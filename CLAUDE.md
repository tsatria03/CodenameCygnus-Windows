# CLAUDE.md

This file guides Claude Code when it works in this repository. **It is a lean dispatcher.** It says what the project is and how it is laid out, then points to focused memory files (`[[name]]`) for the detail. When you start work in an area, read its linked memory first.

**Memory location:** all memory files (the `[[name]]` links and the `MEMORY.md` index) live in the repo's **`aidocks/`** folder, in two folders: **`aidocks/plans/`** holds every plan, planned or complete, as `aidocks/plans/<name>_plan.md` with no `project_` prefix, and a finished plan stays there, marked finished; **`aidocks/general/`** holds every other note, as `aidocks/general/<name>.md`. A `[[name]]` link resolves to whichever of the two holds it ([[feedback_completed_projects]]). Read memory from there and write new or updated memory there, never to the `~/.claude` memory store. `aidocks/general/MEMORY.md` is the index, so add a one-line pointer there for every new memory. Keep this file under 40,000 characters and move detail into memory ([[feedback_memory_in_aidocks]]).

## What this is

A Windows port of **Codename Cygnus** (`net.reactivestudios.codenamecygnus` 1.3.2, Reactive Studios), an iOS interactive radio drama no longer on the App Store. Each episode is a voiced spy story, and the player's choices shape their agent's personality and the story. The original took choices by voice; the port is for the keyboard and screen readers, and keeps spoken choices behind an on/off setting ([[project_speech_recognition]]).

- **A solo project.** tsatria03 makes it alone, with no contributors, until the dev says otherwise ([[project_solo]]).
- **Windows only.** No Linux or macOS, and no GitHub Actions release workflow ([[project_windows_only]]).
- **Python only**, in the `codenamecygnus/` package, with pygame and Prism ([[project_python_only]]).
- **Developer tasks**, open and finished, are in [[project_dev_tasks]].
- **The game is data-driven.** Each episode is a graph of states (voice, background and decision audio, a script) joined by manual choices, automatic transitions, conditions and timed choices. The story is built from the v53 graph in the app's database, not the bundled v1 JSON, and every player starts from scratch ([[project_story_data_source]]).
- **Status:** the story is exported and the foundation is built; the story itself does not play yet.

## Layout

- **`game/`**: the original app bundle, never written to. `game/data/text/` holds the three bundled descriptors (missions, resources, states v1), and beside them the game's own `missions.json`, `resources.json` and `states.json`, the final data exported by `tools/export_story.py` ([[story_export_plan]]); the game reads only those. `game/CodenameCygnus.sqlite` with its `-wal` holds the story v53. `game/data/audio/missions/m1/` holds `episodes/e1` to `e8` (the 756 voice recordings), `sources/` (the 52 backgrounds and decision sounds) and `teasers/` (the six previews, `m1e2.mp3` to `m1e7.mp3`). All of `missions/` is gitignored, since even some ambiences carry voices. `game/data/audio/others/menu/` holds the eight interface sounds and is the only audio in git. Every recording is MP3, converted by the dev from the original AAC `.m4a`; the story data still says `.m4a` ([[project_python_only]]). Don't move, rename, convert or delete sound files unless the dev asks.
- **`CodenameCygnus.py`**: the entry script, with the options, the logs and the crash file.
- **`codenamecygnus/`**: the port's Python package ([[foundation_plan]]): `paths.py`, `app.py` (the main loop), `platform/` (speech, timers, safe JSON files, settings, the key map, the audio), `ui/` (the screen stack, the spoken menu, the F1 screen, Settings) and `game/` (finding recordings by story name, and the stand-in main menu).
- **`tests/interact/`**: tools played by ear, not tests, run by the dev: `audio_check.py` plays a story state's sound layers ([[audio_plan]]).
- **`tests/case/`**: plain test scripts, each importing `_quiet.py` first, which keeps it silent and off the real save. `tests/suite.py` runs them all, into the gitignored `tests/results/`. Run only the files covering what changed, in the background; the full suite only when the dev asks ([[feedback_dont_run_or_build]]).
- **`vendor/nvda/`**: `nvdaControllerClient64.dll` (x64) and its license.
- **`docks/`**: the documents a player reads: `readme.txt`, `changelog.txt` and `todo list.txt` ([[feedback_changelog]], [[feedback_todo_list_format]]).
- **`analysis/`**: data exported from the original for reference. `analysis/script/` holds the whole story as plain text, one file per episode, written by `tools/script_text.py`; search a file for a state's name to follow a choice.
- **`tools/`**: scripts for reading the original, described in `tools/README.md`. `macho64.py` reads the arm64 slice of `game/Cygnus` (not encrypted) and `dis64.py` disassembles its methods with capstone, naming selectors. `cygnus_db.py` reads the story v53, episodes v18 and resources v11 from a temporary copy of the database, `export_story.py` writes the game's JSON after checking it, and `script_text.py` writes the readable script. Plans cite the original's code by those virtual addresses.
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
