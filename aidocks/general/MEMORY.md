# Codename Cygnus memory index

The `[[name]]` links in `CLAUDE.md` and across these notes resolve to `aidocks/general/<name>.md`, beside this index, or, for a plan, planned or complete, to `aidocks/plans/<name>.md` (no `project_` prefix). Add a one-line pointer here for every new note. "Memory" or "memories" always means this folder, never the `~/.claude` store.

## Project: what the port is and how to work on it
- [Solo project](project_solo.md): tsatria03 makes the port alone, with no contributors or co-authors, until the dev says otherwise.
- [Windows only](project_windows_only.md): the port is strictly for Windows; the build and release scripts, when adapted, drop the GitHub workflow, its CI steps, and Linux and macOS.
- [Developer tasks](project_dev_tasks.md): the repository, tool, test, build and docs tasks, open and finished, kept out of the players' todo list.
- [Python only](project_python_only.md): the port is written entirely in Python, in `codenamecygnus/`, with pygame and Prism; the recordings are played as MP3 through pygame, converted from .m4a by the dev; no OpenAL.
- [Speech recognition](project_speech_recognition.md): the port keeps spoken choices behind an on/off setting, as the original's voice button did; the keyboard always works; recogniser and defaults still to plan.
- [Story data source](project_story_data_source.md): the v53 story graph in the sqlite DB is authoritative, not the bundled v1 JSON; the port starts from scratch with no save import.

## Plans (aidocks/plans/, planned or being built)
- [Story export plan](../plans/story_export_plan.md): plan 1 of 8. A standard-library tool decodes the DB's story v53, missions v18 and resources v11 once into missions.json, resources.json and states.json in game/data/text/, reading a copy of the DB and checking the result first; planned, ready to build.

- [Foundation plan](../plans/foundation_plan.md): plan 2 of 8. The name Codename Cygnus (CodenameCygnus.py, CodenameCygnus.exe, %APPDATA%\CodenameCygnus), the package layout, speech, timers, settings files, logs and the screen loop adapted from user/, a debug mode with a Settings row, window text, five command-line options and the interruption rules; planned, ready to build.
- [Audio plan](../plans/audio_plan.md): plan 3 of 8. Voice streamed through pygame.mixer.music (seekable), background and decision sounds as Sound objects; the background carries on between states and cuts hard on a change or when a state has none, as the original's code does; the decision loop starts after the question and loops until a choice; files found by story name; three volumes (Shift+Home/End master, Page Up/Down ambience, Shift+Page Up/Down decision); planned, ready to build.
- [Story engine plan](../plans/story_engine_plan.md): plan 4 of 8. Playing the story graph; the episode keys are agreed (arrows, Enter and 1 to 9 for choices, Space, R, Left/Right, S to skip across heard recordings, H for the scene heading, V, Escape), debug keys F2 to F4, the van escape fix and 16 local achievements; planned, ready to build.
- [Menus plan](../plans/menus_plan.md): plan 5 of 8. The original's screens read from the binary (opening, side menu, episode list, agent profile with four trait scales, end of episode, info); main menu of six rows, the opening, no agent name, traits spoken clearly, end-of-episode and pause menus, episode list with descriptions behind Enter, interface sounds; Store and Downloads left out; planned, ready to build.
- [Saves plan](../plans/saves_plan.md): plan 6 of 8. Story variables carry between episodes (Signum Cygni checks choices from every earlier one); progress, heard recordings, achievements, settings and keys in short files in %APPDATA%\CodenameCygnus; Restart locks later episodes again behind the original's warning; saved on every new state; planned, ready to build.
- [Speech recognition plan](../plans/speech_recognition_plan.md): plan 7 of 8. Spoken choices behind a setting, listening only while a choice waits and only for its words; PocketSphinx, sounddevice for the microphone, off by default, 15 seconds a time; nothing recorded; planned, ready to build.
- [Build and release plan](../plans/build_release_plan.md): plan 8 of 8. compiler.py builds CodenameCygnus.exe with PyInstaller, releaser.py versions, zips, tags and uploads from the dev's machine; Windows only, no workflow; the recordings ship separately as an AES-encrypted m1.dat on a fixed mission-1 release, which the game downloads into %APPDATA%\CodenameCygnus\missions; the compiler's nine-choice menu and the releaser's nine-row menu; planned, ready to build.

## Completed projects (aidocks/plans/, marked finished)
- None yet.

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

## User
- [Screen reader](user_screen_reader.md): the dev uses NVDA; lists and short lines, no wide tables, and never make noise from tools.
