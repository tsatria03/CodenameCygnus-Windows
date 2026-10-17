# Codename Cygnus memory index

The `[[name]]` links in `CLAUDE.md` and across these notes resolve to `aidocks/general/<name>.md`, beside this index, or, for a plan, planned or complete, to `aidocks/plans/<name>.md` (no `project_` prefix). Add a one-line pointer here for every new note. "Memory" or "memories" always means this folder, never the `~/.claude` store.

## Project: what the port is and how to work on it
- [Solo project](project_solo.md): tsatria03 makes the port alone, with no contributors or co-authors, until the dev says otherwise.
- [Windows only](project_windows_only.md): the port is strictly for Windows; the build and release scripts, when adapted, drop the GitHub workflow, its CI steps, and Linux and macOS.
- [Developer tasks](project_dev_tasks.md): the repository, tool, test, build and docs tasks, open and finished, kept out of the players' todo list.
- [Python only](project_python_only.md): the port is written entirely in Python, in `codenamecygnus/`, with pygame and Prism; the audio library and format are still to be planned.
- [Story data source](project_story_data_source.md): the v53 story graph in the sqlite DB is authoritative, not the bundled v1 JSON; the port starts from scratch with no save import.

## Completed projects (aidocks/plans/, marked finished)
- None yet.

## Feedback: how the dev wants you to work
- [Memory in aidocks](feedback_memory_in_aidocks.md): all memory goes in aidocks/, plans in plans/, everything else in general/, with this index; CLAUDE.md is a lean dispatcher under 40,000 characters.
- [Git commits and pushes](feedback_git_commits.md): one commit per fix, split into multiple commits when possible; commit only when asked; add, commit and fetch run without approval. "Commit" means commit only, "commit/push" means both. Force pushes and history rewrites need an explicit go-ahead. Use `git commit -F` with a message file, from PowerShell, and never hide git's errors.
- [GitHub usernames, not real names](feedback_use_github_usernames.md): name people by GitHub username (tsatria03) in commits and committed notes.
- [No other games](feedback_no_other_games.md): never name the dev's other game from user/ in this repo's files, even when adapting from it.
- [Don't run or build](feedback_dont_run_or_build.md): never build unless told; ask before running the game or anything that speaks or plays sound; tests must be silent and off the real save.
- [Record plans first](feedback_record_plans_first.md): an agreed plan gets its own aidocks/plans/ note before any code, committed on its own first; marked finished only once the dev says it works.
- [Completed projects](feedback_completed_projects.md): every plan stays in aidocks/plans/, planned or complete; a finished one moves only its index line.
- [Changelog](feedback_changelog.md): every player-facing change adds a plain sentence at the top of `unrelease:` in docks/changelog.txt, newest first; LF, no markdown; 5 to 100 entries a release.
- [Todo list format](feedback_todo_list_format.md): ##Unfinished. then ##Finished., one plain sentence per line, new items at the top, players only; LF, no markdown.
- [No release records](feedback_no_release_records.md): never record individual releases in aidocks or README.md.
- [Questions are checks](feedback_questions_are_checks.md): a question from the dev gets an answer in chat, not edits.
- [No question pickers](feedback_no_question_pickers.md): ask questions as plain text, never through the picker tool.
- [One question at a time](feedback_one_question_at_a_time.md): one question per reply, with a recommendation.

## User
- [Screen reader](user_screen_reader.md): the dev uses NVDA; lists and short lines, no wide tables, and never make noise from tools.
