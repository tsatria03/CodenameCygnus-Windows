---
name: build_release_plan
description: "Plan 8 of 8: compiler.py builds CodenameCygnus.exe with PyInstaller and releaser.py versions, zips and publishes a release from the dev's own machine; Windows only, no GitHub Actions workflow; the recordings ship separately as an encrypted m1.dat the game downloads; folder build, single exe or one-file chosen each time. Status: finished."
metadata:
  node_type: memory
  type: project
---

**Status: finished,** both sections confirmed by the dev on 2026-10-18, the last with the full release ("The release works perfectly!"). Started the same day (the dev: "Now you can make the 2 python scripts.").

## Built in sections

1. **The two scripts,** `compiler.py` and `releaser.py` at the repository's root, with `tests/case/release.py` for what they work out without building. Status: done, confirmed by the dev on 2026-10-18: the mission pack upload, choice 9, and then a full release, building, zipping, committing, tagging and uploading ("The release works perfectly!").
   - **What a build carries:** the game's code; the NVDA client in `vendor\nvda`; Prism with its compiled half; PocketSphinx with only the model it uses, the English acoustic model and the dictionary, leaving out its two language models (28 MB) since the grammar replaces them; sounddevice with only PortAudio's 64-bit DLL; and of the game's data only what it reads: `game\data\text`'s three exported files (not the original's three descriptors) and the eight menu sounds in `game\data\audio\others\interface`. Nothing else of the original's bundle, and never the mission recordings or `m1.dat`.
   - **Beside the exe:** `docks\` (the readme, changelog and todo list, the changelog without an empty `unrelease:`), `VERSION` and the license as `license.txt`. **Inside it,** as `licenses\`: the NVDA client's, Prism's, pygame's LGPL, PocketSphinx's, sounddevice's and cffi's, each package's taken from its installed copy.
   - **`--test`** sets `CYGNUS_SILENT`, the dummy SDL drivers and a throwaway `CYGNUS_USER_DIR`, starts the build with `--exit-after 6`, and needs the log's "game data:" line, which `CodenameCygnus.py` now writes at every start, its "Codename Cygnus closed", no `crash.txt`, and exit code 0.
   - **The releaser's step 9** puts `dist\m1.dat` on the `mission-1` release, made with `--latest=false` if it is not there yet; until section 2 builds the pack, it says there is no pack.
   - Neither script names where it came from ([[feedback_no_other_games]]).
2. **The mission pack:** the tool that builds `m1.dat`, the game reading recordings from it, and the download. Status: built 2026-10-18 (the dev: "Please do section 2. Also, the source repo should be able to fall back to the dat file if I delete the local missions folder."). **The pack is complete,** confirmed by the dev by ear the same day: built with `tools/build_pack.py` (491,331,636 bytes, its `m1_pack.json` committed), it plays from both places, `dist\` from source and `%APPDATA%\CodenameCygnus\missions` ("The m1.dat works perfectly in 2 places, in the source dist folder, and in app data."), and the dev said to record it complete. A pack already in AppData is never downloaded again, and the embedded build reads `m1_pack.json` from inside the exe. **The download works too,** confirmed by the dev the same day ("There we go. All downloaded. It works."): the pack was rebuilt, its new `m1_pack.json` committed, and uploaded to the `mission-1` release with the releaser's choice 9, then downloaded by the game from there and checked. Section 2 is done.
   - **`codenamecygnus/game/pack.py`** holds the format, the reader and the writer. `m1.dat` is `CYGPACK1`, the index's length, the index, then every recording, each encrypted on its own with AES-256-GCM, a fresh 12-byte nonce in front, its story key as the associated data. The index, encrypted the same way, is JSON: each story key's offset and length. The key is 32 bytes in the code. Reading a recording opens the file, reads that one, and decrypts it in memory; nothing is unpacked to disk.
   - **`tools/build_pack.py`** packs every MP3 under `game/data/audio/missions/m1/` into `dist\m1.dat`, by the same story keys the loose files are found by, written to `m1.dat.part` and renamed once whole, then writes `game/data/text/m1_pack.json`: the file's size, its SHA-256 and the address it downloads from. That file is how the fingerprint is built into the game, and the compiler carries it; a build without it warns that it cannot download its recordings.
   - **Where the recordings come from** (`Recordings`): the loose files under `game/data/audio/missions/` when any are there, which only a source run has; otherwise the pack in `%APPDATA%\CodenameCygnus\missions\m1.dat`, and from source, failing that, the one the tool left in `dist\`. So a source run with the missions folder deleted uses the pack exactly as a build does (the dev's request above), downloading it if there is none. A pack of the wrong size is taken as missing. The menu sounds are always loose files.
   - **The download** (`codenamecygnus/game/download.py`): while no recordings are there, an episode's screen has Back, its description, then "Download Mission 1" in place of its buttons; a locked one keeps its Start. Continue in the main menu opens the download first. The download runs on a thread of its own with `urllib`, into `m1.dat.part`; the screen says "Downloading Mission 1. Escape cancels.", with no size, as the row has none, and every 10 percent with the push sound, `00000Push`, Enter says how far it is, and Escape cancels and deletes the part. Once whole it says "Checking the download.", compares the SHA-256, fetches again up to twice if it is damaged, then renames it, says "Mission 1 is downloaded.", and goes back to the episode's screen, now with its buttons. A failed download says why, and Enter tries again.
   - **`cryptography`** joins `requirements.txt` (50.0.2 was already installed), and its license goes into a build.
   - **Tests:** `tests/case/pack.py`, with a small pack of made-up recordings and a stand-in for the network; nothing is downloaded.

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
  - When an episode is opened and the pack is missing, the game offers "Download Mission 1" (at first with "about 470 megabytes" after it, which the dev removed on 2026-10-18: "Please remove the size lable"), like the original's DOWNLOAD button ([[menus_plan]]).
  - The screen reader says the progress every 10 percent, and Escape cancels.
  - It downloads to `m1.dat.part` and renames it only once complete, so a cut connection never leaves a broken pack.
  - It checks the finished file against its SHA-256 fingerprint, built into the game, and fetches it again if damaged.
  - Game updates never touch it, since it is in the save folder, not the game folder.
- **The pack is encrypted with AES, through the `cryptography` package,** with a key built into the game. Each recording is encrypted on its own, so the game decrypts only the one it needs, in memory, and hands it to pygame, never unpacking anything to disk. This keeps out casual copying, not a determined person, since the key ships with the game. `cryptography` is in `requirements.txt`.
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

- **The releaser's menu** (the dev, 2026-10-17: "Yes. It sure does."), the reference material's own without its workflow and second-system rows:
  1. **Full release:** every step below from 2 to 8, in order, each asking Y or N first.
  2. **Check that everything is ready:** everything committed and pushed, `gh` signed in, and 5 to 100 changes under `unrelease:`; with 1 to 4 it asks "Release anyway with N change(s)?" ([[feedback_changelog]]).
  3. **Set the version and file the changelog:** `VERSION` becomes today's date and that day's number, such as `26.10.17-1`, and the `unrelease:` lines go under it.
  4. **Build:** asks "1. the folder build, 2. the single exe, 0. skip" and runs the compiler. A failed build puts `VERSION` and the changelog back.
  5. **Zip the build** into `CodenameCygnus-Win-<version>.zip`, which extracts to a `CodenameCygnus-Windows` folder. It only zips a build made for that version.
  6. **Commit and push** `VERSION` and the changelog as "Release <version>".
  7. **Tag the release** `V<version>`, and push the tag.
  8. **Upload the release to GitHub** as "CodenameCygnus V<version>", with that version's changelog lines as its notes.
  9. **Upload the mission pack:** puts `m1.dat` on the `mission-1` release, never marked Latest. **The pack goes up as the loose file, never zipped** (the dev: "The mission pack is never zipped up. It's the loose dat file"), since the game downloads exactly that file and checks its fingerprint.
  - It never moves or replaces a tag, a release, or a file already on a release.

## Open questions

None.
