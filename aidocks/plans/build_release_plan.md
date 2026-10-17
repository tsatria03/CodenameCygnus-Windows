---
name: build_release_plan
description: "Plan 8 of 8: compiler.py builds CodenameCygnus.exe with PyInstaller and releaser.py versions, zips and publishes a release from the dev's own machine; Windows only, no GitHub Actions workflow. Status: planned, questions open."
metadata:
  node_type: memory
  type: project
---

**Status: planned, questions open.** Nothing is built.

Plan 8 of 8 ([[story_export_plan]] lists the order). It is the developer task "Adapt the build script and the release script for Windows only" in [[project_dev_tasks]].

## Decided

- **Windows only,** with no Linux or macOS parts, no GitHub Actions workflow, no "Prepare and tag" or "Test the workflow" steps and no CI entry points ([[project_windows_only]]).
- **Two scripts adapted from the reference material in `user/`,** never naming where they came from ([[feedback_no_other_games]]):
  - `compiler.py` builds the game with PyInstaller into `dist\CodenameCygnus-Windows`, around `CodenameCygnus.exe`. It only builds: it never zips and never changes the repository. Run with no options, it shows a numbered menu.
  - `releaser.py` makes a release on the dev's own machine: it checks the changelog, sets `VERSION` to today's date and that day's number (`26.10.17-1`), files the changelog's `unrelease:` lines under it, builds with the compiler, zips the build, commits "Release <version>", tags `V<version>`, and uploads the zip to GitHub through `gh`. It asks Y or N before each step.
- **A build carries** the game data it needs, `docks\` (the readme, changelog and todo list), `VERSION`, the license, and the third-party licenses: the NVDA client, Prism, pygame, PocketSphinx and sounddevice.
- **`compiler.py --test` starts a finished build silently** for a few seconds with `--exit-after`, on a throwaway save, and reads its log ([[foundation_plan]]).
- **The changelog's release rules** (5 to 100 entries, never more than 100) are in [[feedback_changelog]].
- **Claude never builds or releases**; the dev runs both ([[feedback_dont_run_or_build]]).

## Open questions

- Whether a release carries the recordings, which are not in the repository.
- A folder build, a single executable, or both.
- What the zip is called.
