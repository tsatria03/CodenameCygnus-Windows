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
  - every recording the story names has its MP3 on disk, found the way the game will find it: by file name under `game/data/audio/`, `.mp3` in place of `.m4a`, and a story `m1eN_teaser` as `missions/m1/teasers/m1eN.mp3`
- **It reports in short plain lines** a screen reader reads cleanly: one line per check, then each problem on its own line naming the state or file.
- **Known quirks are reported as notes, not failures:** two states nothing leads to, `026gentlemenFlavor_m1e8` and `46BopenItResponse_m1e8`, cut from the original.
- **The export fixes the van escape bug** in Signum Cygni ([[story_engine_plan]] has the detail; the dev, 2026-10-17: "This bug needs to be fixed"). `3_AAB008transition_m1e7` is split in two, one copy for each way in, each with a single automatic exit:
  - the GRAB IT choice from `3_AAB007matthewsEscapePrompt_m1e7` leads to a copy that goes on to `4_AABA002alexAthleticRefuseMatthewsEND_m1e7`
  - the HANG ON choice from `3_AAB007alexEscapePrompt_m1e7` leads to a copy that goes on to `4_AABB003alexAthleticRefuseAlexEND_m1e7`
  - both copies keep the state's media and its variable (`npc_state.rhodes` set to 4)
  - the check then fails if any state still has more than one automatic exit
- **It runs on the dev's own machine.** The mission recordings and previews are gitignored, so the recording check needs them on disk.

## The readable script

Added 2026-10-17 (the dev: "Yes please. I'd love to see how the entire story was written"), and built ahead of the rest, since it is a tool and not part of the game. **This part is finished,** confirmed by the dev on 2026-10-17 ("I love it! It reads super clearly"): eight files, all 967 states placed, no pacing marks left, and the database unchanged after reading it. The rest of the plan, the JSON export and its checks, is still to build.
- **`tools/script_text.py` writes the whole story as plain text into `analysis/script/`,** one file per episode, such as `m1e2 Art Show.txt`, for reading the story and for checking the port against it.
- **It reads the v53 story and the v18 episodes through `tools/cygnus_db.py`,** which decodes the database from a temporary copy. The export tool will use the same module.
- **Each file starts with the episode's title and description, then gives every state once**, in the order play reaches them from the episode's start. Each state block is headed by its name, so any choice can be followed by searching for the name it leads to.
- **A block holds** the scene heading, each character's lines, the sound directions, what the state sets, and where it goes next: each choice and its target, the 7-second timeout, a condition and both its outcomes, or the next state.
- **The pacing marks are removed.** Hidden choices are marked as hidden.
- **It shows the original's data, the van escape bug included,** with a note at that state.
- **A preview goes at the end of the episode it follows**, as the original played it there. States no episode reaches go at the end of the last file, marked as never reached.

## Open questions

None. Ready to build once the dev says so.
