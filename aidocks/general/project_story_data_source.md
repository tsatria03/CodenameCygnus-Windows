---
name: project_story_data_source
description: "The authoritative Codename Cygnus story graph is v53 inside game/CodenameCygnus.sqlite, not the bundled v1 JSON. The port starts from scratch and never imports a save."
metadata:
  node_type: memory
  type: project
---

The authoritative story graph is states v53. It is stored as an NSKeyedArchiver plist in `ZCCGAMEDATA.ZSTATESJSON` of `game/CodenameCygnus.sqlite`, read together with its `-wal` file. The bundled `game/data/text/states_descriptor.json` is v1. It lacks Holiday Party (1.8.1), the `auto-timeout` transitions and the `render: false` hidden choices. The v53 graph was checked on 2026-10-17: all 8 Mission 1 episodes can be played from start to end, and every audio file it names is on disk.

The DB's save and progress rows (3 early Prologue saves, nothing completed) come from a secondary device. The dev fully played the game, Holiday Party included, on a different device.

**Why:** Low progress in the DB looks as if the game was barely played, or as if later episodes did not work. Neither is true.

**How to apply:**
- Build the port from v53, exported once to a plain JSON file. Use the DB for story data only, never for progress.
- The dev decided on 2026-10-17 that the port starts from scratch. There is no save or progress import from the iOS DB or any old device.
- A new game opens the Prologue and Holiday Party; each other episode opens when the one before it is finished. The dev confirmed Holiday Party open from the start on 2026-10-17 ("Yes. It should be open."), following the DB's mission data.

**The DB's mission and resource data are newer too** (checked 2026-10-17):
- Mission data is version 18, against the bundled `mission_descriptor.json`'s version 1, in the tables `ZCCMISSION`, `ZCCEPISODE`, `ZCCEPISODELOCK` and `ZCCCREDIT`. The first seven episodes match the bundled file exactly. Holiday Party (1.8.1) differs:
  - it is not locked
  - it has its start and end states, `m1e8_start` and `m1e8_end`
  - its completion text is "You completed the Holiday Party, but did you find all three endings? Find out which endings your friends found!"
  - its description drops "Coming this month..."
  - it has 18 credit lines instead of 8
- Resource data is version 11, against version 1, in `ZCCRESOURCECOLLECTION` and `ZCCRESOURCE`. It adds the collections `1.8` (75 files) and `1.8_other` (12).
- How all three are exported is in [[story_export_plan]].
