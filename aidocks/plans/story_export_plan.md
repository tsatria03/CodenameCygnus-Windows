---
name: story_export_plan
description: "Plan 1 of 8: a tool that decodes the newest story (v53), mission (v18) and resource (v11) data from the original's database once, and writes plain JSON for the game to read, after checking it. Status: planned, ready to build."
metadata:
  node_type: memory
  type: project
---

**Status: planned, ready to build.** Every question is answered; nothing is built.

This is the first of eight plans, written before any porting starts (the dev, 2026-10-17: "Let's write some plans first, and I'll answer any questions you may have before we start the actual porting process"). The order:
1. story export (this plan)
2. foundation
3. audio
4. story engine
5. menus and screens
6. saves
7. speech recognition
8. Windows build and release

## Goal

The game reads the original's final data, not the older files bundled with the app ([[project_story_data_source]]). The database is an iOS Core Data store, and the story is an `NSKeyedArchiver` plist inside it. So a tool decodes it once and writes plain JSON. The game itself never opens the database.

## Sources, all in `game/CodenameCygnus.sqlite` with its `-wal` file

- **Story, v53:** `ZCCGAMEDATA.ZSTATESJSON`, an `NSKeyedArchiver` binary plist. Decoded on 2026-10-17 with `plistlib`, resolving `UID` references: 967 states and 1089 transitions.
- **Missions, v18:** `ZCCMISSION`, `ZCCEPISODE`, `ZCCEPISODELOCK` and `ZCCCREDIT`. The company credits are the `ZCCCREDIT` rows with no episode.
- **Resources, v11:** `ZCCRESOURCECOLLECTION` and `ZCCRESOURCE`.

## Decided

- **Holiday Party is open from the start** (the dev, 2026-10-17: "Yes. It should be open."), as the v18 data says.
- **The tool lives in `tools/` and needs only the standard library:** `sqlite3`, `plistlib` and `json`.
- **It reads a copy of the database, never the original.** SQLite can fold the `-wal` file into the main file when a connection closes, which would change `game/`. So the tool copies the three files to a temporary folder first and opens the copy.
- **It cleans up the types the archive left as strings:** numbers such as a timeout's `"7"` and a variable's `"-1"` become numbers, and `render` becomes `true` or `false`.
- **The JSON keeps the bundled files' own key names and shape**, so a reader of the old files can read the new ones.
- **The game reads no progress or saves from the database** ([[project_story_data_source]]).
- **The output is three new files in `game/data/text/`:** `missions.json`, `resources.json` and `states.json` (the dev, 2026-10-17: "I agree"). They sit beside the bundled v1 files, which stay untouched as a record of what the app shipped. The game reads only the new ones, and the build ships them.

- **No second copy in `analysis/`.** The export is already plain, readable JSON in `game/data/text/`, so a copy would only duplicate it.
- **The tool checks its own result and writes nothing if a check fails** (the dev, 2026-10-17: "yes, please make it check"). It checks that:
  - every episode can be played from its start state to its end state
  - every choice, transition and condition points to a state that exists
  - every recording the story names has its MP3 on disk, found the way the game will find it: by file name under `game/data/audio/`, `.mp3` in place of `.m4a`, and a story `m1eN_teaser` as `other/teasers/m1eN.mp3`
- **It reports in short plain lines** a screen reader reads cleanly: one line per check, then each problem on its own line naming the state or file.
- **Known quirks are reported as notes, not failures:**
  - two states nothing leads to, `026gentlemenFlavor_m1e8` and `46BopenItResponse_m1e8`, cut from the original
  - one state with two automatic transitions, `3_AAB008transition_m1e7`; which one the game takes is for [[story_engine_plan]]
- **It runs on the dev's own machine.** The mission recordings and previews are gitignored, so the recording check needs them on disk.

## Open questions

None. Ready to build once the dev says so.
