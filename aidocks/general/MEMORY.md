# Codename Cygnus memory index

The `[[name]]` links in `CLAUDE.md` and across these notes resolve to `aidocks/general/<name>.md`, beside this index, or, for a plan, planned or complete, to `aidocks/plans/<name>.md` (no `project_` prefix). Add a one-line pointer here for every new note. "Memory" or "memories" always means this folder, never the `~/.claude` store.

## Project: what the port is and how to work on it
- [Solo project](project_solo.md): tsatria03 makes the port alone, with no contributors or co-authors, until the dev says otherwise.
- [Windows only](project_windows_only.md): the port is strictly for Windows; the build and release scripts, when adapted, drop the GitHub workflow, its CI steps, and Linux and macOS.
- [Developer tasks](project_dev_tasks.md): the repository, tool, test, build and docs tasks, open and finished, kept out of the players' todo list.
- [Python only](project_python_only.md): the port is written entirely in Python, in `codenamecygnus/`, with pygame and Prism; the recordings are played as MP3 through pygame, converted from .m4a by the dev; no OpenAL.
- [Speech recognition](project_speech_recognition.md): the port keeps spoken choices behind an on/off setting, as the original's voice button did; the keyboard always works; the details are in the speech recognition plan.
- [Story data source](project_story_data_source.md): the v53 story graph in the sqlite DB is authoritative, not the bundled v1 JSON; the port starts from scratch with no save import.

## Plans (aidocks/plans/, planned or being built)
- [Menus plan](../plans/menus_plan.md): plan 5 of 8. The original's screens read from the binary (opening, side menu, episode list, agent profile with four trait scales, end of episode, info); main menu of six rows, the opening, no agent name, traits spoken clearly, end-of-episode and pause menus, episode list with descriptions behind Enter, interface sounds; Store and Downloads left out; being built in four sections, the parts needing saved progress last: 1 (opening, main menu, episode list, Credits, sounds) and 2 (Settings) done; Back is first in every menu; 3 (end of episode, previews) done; 4 (the parts needing saves) waits for the saves plan.
- [Saves plan](../plans/saves_plan.md): plan 6 of 8. Story variables carry between episodes (Signum Cygni checks choices from every earlier one); progress, heard recordings, achievements, settings and keys in short files in %APPDATA%\CodenameCygnus; Restart locks later episodes again behind the original's warning; saved on every new state; planned, ready to build.
- [Speech recognition plan](../plans/speech_recognition_plan.md): plan 7 of 8. Spoken choices behind a setting, listening only while a choice waits and only for its words; PocketSphinx, sounddevice for the microphone, off by default, 15 seconds a time; nothing recorded; planned, ready to build.
- [Build and release plan](../plans/build_release_plan.md): plan 8 of 8. compiler.py builds CodenameCygnus.exe with PyInstaller, releaser.py versions, zips, tags and uploads from the dev's machine; Windows only, no workflow; the recordings ship separately as an AES-encrypted m1.dat on a fixed mission-1 release, which the game downloads into %APPDATA%\CodenameCygnus\missions; the compiler's nine-choice menu and the releaser's nine-row menu; planned, ready to build.

## Completed projects (aidocks/plans/, marked finished)
- [Story engine plan](../plans/story_engine_plan.md): FINISHED 2026-10-18, built in five sections, each confirmed by the dev by ear through tests/interact/episode_check.py. game/story.py (the rules; choices in the order the question says them), game/episode_screen.py (playing an episode: choices focused on the first, the keys, held-key repeat, timed choices, the pause menu with Restart), game/heard.py and S, game/debug.py (F2, F3 jump, F4, --state), game/achievements.py (16, local, announced at a quiet moment).
- [Audio plan](../plans/audio_plan.md): FINISHED 2026-10-17, confirmed by the dev by ear through tests/interact/audio_check.py. platform/audio.py: the voice streamed through pygame.mixer.music (replay, 5-second skips), the background on its own channel carrying on or cutting hard as the original did, the decision loop, menu sounds, pausing all together, three squared-gain volumes (Shift+Home/End, Page Up/Down, Shift+Page Up/Down); MP3 lengths read from headers. game/recordings.py finds recordings by story name.
- [Foundation plan](../plans/foundation_plan.md): FINISHED 2026-10-17, confirmed by the dev by ear. CodenameCygnus.py and the codenamecygnus package: paths, the main loop, speech (NVDA, Prism, a Windows voice), the timer loop, safe JSON files, settings, the key map (one key with exact modifiers; Shift+Home louder), the spoken menu (rows without their place), F1 from anywhere, the Settings screen's Debug mode row, logs and crash.txt; a stand-in main menu until the menus plan; 59 silent tests and tests/suite.py.
- [Story export plan](../plans/story_export_plan.md): FINISHED 2026-10-17, confirmed by the dev. tools/export_story.py decodes the DB's story v53, missions v18 and resources v11 from a copy of the DB, fixes the van escape bug, checks every episode, link, condition and recording, and writes missions.json, resources.json and states.json in game/data/text/; --check writes nothing. The readable script in analysis/script/ was finished the same day.

## Feedback: how the dev wants you to work
- [Memory in aidocks](feedback_memory_in_aidocks.md): all memory goes in aidocks/, plans in plans/, everything else in general/, with this index; CLAUDE.md is a lean dispatcher under 40,000 characters.
- [Git commits and pushes](feedback_git_commits.md): one commit per fix, split into multiple commits when possible; commit without asking; bring up pushing only at 10 or more unpushed commits, with the count; add, commit and fetch run without approval. "Commit" means commit only, "commit/push" means both. Force pushes and history rewrites need an explicit go-ahead. Use `git commit -F` with a message file, from PowerShell, and never hide git's errors.
- [GitHub usernames, not real names](feedback_use_github_usernames.md): name people by GitHub username (tsatria03) in commits and committed notes.
- [No other games](feedback_no_other_games.md): never name the dev's other game from user/ in this repo's files, even when adapting from it.
- [Don't run or build](feedback_dont_run_or_build.md): never build unless told; ask before running the game or anything that speaks or plays sound; tests must be silent and off the real save.
- [Record plans first](feedback_record_plans_first.md): an agreed plan gets its own aidocks/plans/ note before any code, committed on its own first; marked finished only once the dev says it works.
- [Completed projects](feedback_completed_projects.md): every plan stays in aidocks/plans/, planned or complete; a finished one moves only its index line.
- [Changelog](feedback_changelog.md): every player-facing change adds a plain sentence at the top of `unrelease:` in docks/changelog.txt, newest first; no markdown; 5 to 100 entries a release.
- [Todo list format](feedback_todo_list_format.md): ##Unfinished. then ##Finished., one plain sentence per line, new items at the top, players only; no markdown. Line endings do not matter.
- [No release records](feedback_no_release_records.md): never record individual releases in aidocks or README.md.
- [Questions are checks](feedback_questions_are_checks.md): a question from the dev gets an answer in chat, not edits.
- [No question pickers](feedback_no_question_pickers.md): ask questions as plain text, never through the picker tool.
- [One question at a time](feedback_one_question_at_a_time.md): one question per reply, with a recommendation.
- [Back first](feedback_back_first.md): every menu with a way back has a Back row as its very first row and opens on it, Settings and the volume levels included; the main menu, pause menu, yes-or-no questions and the headphones notice keep their own first rows.
- [Test tools in tests/interact](feedback_test_tools_in_interact.md): a tool for trying something by ear, such as the episode chooser, is its own script in tests/interact/ with its own save, never part of the game's menus.

## User
- [Screen reader](user_screen_reader.md): the dev uses NVDA; lists and short lines, no wide tables, and never make noise from tools.
