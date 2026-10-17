---
name: build_release_plan
description: "Plan 8 of 8: compiler.py builds CodenameCygnus.exe with PyInstaller and releaser.py versions, zips and publishes a release from the dev's own machine; Windows only, no GitHub Actions workflow; the recordings ship separately as an encrypted m1.dat the game downloads. Status: planned, questions open."
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

## The mission pack, m1.dat

The dev's idea (2026-10-17): "I was thinking of creating a file called m1.dat inside the following directory. C:\Users\tonys\AppData\Roaming\CodenameCygnus\missions. That way, the game's zip file won't be massive." It works as the original's own downloads did, the app small and each episode's recordings fetched on first use.

- **A game release carries no recordings.** Mission 1's recordings, everything under the gitignored `game/data/audio/missions/m1/`, go into one pack, `m1.dat`, about 470 MB.
- **The pack lives on a release of its own,** tagged `mission-1` and named "Mission 1 recordings", uploaded once and never marked Latest (the dev, 2026-10-17: "Yes. I highly dout the recordings will ever change so."). Its address never changes, so every version of the game downloads from `https://github.com/tsatria03/CodenameCygnus-Windows/releases/download/mission-1/m1.dat`. Game releases carry only the small game zip.
- **The game downloads it into `%APPDATA%\CodenameCygnus\missions\m1.dat`** ([[saves_plan]]), with Python's own `urllib`:
  - When an episode is opened and the pack is missing, the game offers "Download Mission 1, about 470 megabytes", like the original's DOWNLOAD button ([[menus_plan]]).
  - The screen reader says the progress every 10 percent, and Escape cancels.
  - It downloads to `m1.dat.part` and renames it only once complete, so a cut connection never leaves a broken pack.
  - It checks the finished file against its SHA-256 fingerprint, built into the game, and fetches it again if damaged.
  - Game updates never touch it, since it is in the save folder, not the game folder.
- **The pack is encrypted with AES, through the `cryptography` package,** with a key built into the game. Each recording is encrypted on its own, so the game decrypts only the one it needs, in memory, and hands it to pygame, never unpacking anything to disk. This keeps out casual copying, not a determined person, since the key ships with the game. `cryptography` joins `requirements.txt` when this is built.
- **The pack holds an index** of every recording's name, place and size, so a recording is found by its story name as before ([[audio_plan]]).
- **A tool in `tools/` builds `m1.dat`** from `game/data/audio/missions/m1/` on the dev's machine and prints its SHA-256 for the game. The dev uploads it to the `mission-1` release.

- **A run from source reads the loose recordings** in `game/data/audio/missions/` when they are there, and the pack otherwise (the dev, 2026-10-17: "I like the loose folder for playing it from the source"). So testing needs no rebuilt pack after each change, and works before the first pack exists. A built game never has loose recordings, so players always use the pack.

- **Both kinds of build, chosen each time** (the dev, 2026-10-17: "You should be able to choose. I want to test both options"). `compiler.py` keeps the reference material's choices, Windows only, plus a test for the single exe; run with no options it shows them as a numbered menu, each choice exactly one command line:
  1. **Folder build:** `CodenameCygnus.exe`, a folder of Python and library files beside it, and the `game` folder.
  2. **Folder build and test** (`--test`): the folder build, then started silently for a few seconds to check it works.
  3. **Single exe** (`--embed`): Python, the libraries and the game's data all inside `CodenameCygnus.exe`.
  4. **Single exe and test** (`--embed --test`).
  5. **Clean build** (`--clean`): PyInstaller's cache emptied first, for when a build behaves oddly.
  6. **Console build** (`--console`): keeps a console window, to see why a build will not start.
  7. **One-file build** (`--onefile`): Python and the libraries inside the exe, the `game` folder still beside it. Kept though the game's data is small now (the dev: "No, keep it just encase I want it").
  8. **Build without the game's data** (`--no-game`).
  9. **Dry run** (`--dry-run`): what a build would do, building nothing.
  - Every kind carries `docks`, `VERSION` and the license beside the exe. None ever carries `m1.dat`.

## Open questions

- The releaser's menu.
- What the zip is called.
