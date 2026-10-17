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
- Only the Prologue is unlocked at first. Art Show and Holiday Party both unlock once the Prologue is finished.
