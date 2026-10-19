---
name: seek_settings_plan
description: "Seek step (the skip length) and seek speed (the repeat rate) as two Settings rows, each opening its levels as a volume does, remembered in config/settings.json, used at once by the story, the previews and held keys. Status: planned, one question open."
metadata:
  node_type: memory
  type: project
---

**Status: planned,** not built. Asked for on 2026-10-18 (the dev: "I think this would be the last feature I'd want, but it needs planning first"), after choosing the game's own repeat by ear with `tests/interact/seek_check.py` ([[audio_plan]]).

## Proposed

- **Two rows in Settings,** after the three volumes and before Speech recognition ([[menus_plan]]), named by the dev (2026-10-18: "I like seek step and seek speed", after "Seek interval" was weighed and set aside as reading like the time between repeats):
  - "Seek step, 5 seconds": how far each press of Left or Right goes.
  - "Seek speed, 100 milliseconds": how often a held key repeats.
- **Each opens its levels,** as a volume's row opens `VolumeLevels`: Back first and opening on it ([[feedback_back_first]]), then the levels. Enter sets one, goes back to Settings and says it, such as "Seek step 10 seconds"; Escape keeps the old one.
  - Seek step: 1, 2, 3, 5, 10, 15, 20, 30 and 60 seconds, the seek check's steps.
  - Seek speed: 50, 100, 150, 200, 250, 300, 350, 400, 450 and 500 milliseconds, the seek check's steps (the dev, 2026-10-18: "It should only be 50, 100, 150 ... and 500"), fastest first, as the volumes go from loudest. The ends say which way they go, "50 milliseconds, fastest" and "500 milliseconds, slowest", since a smaller number is faster.
- **Remembered in `config/settings.json`** ([[saves_plan]]) as `skip_seconds`, default 5, and `repeat_ms`, default 100, the dev's choice. A value not among the levels is put back to its default, as a volume's is.
- **Used at once,** from the main menu's Settings or the pause menu's:
  - the skip by Left and Right in the story and in previews, which read `SKIP_SECONDS` now;
  - the repeat by the main loop for every held key, which reads `REPEAT_EVERY` now.
- **The 0.4-second wait** before a held key starts repeating stays as it is, not a setting.
- **The seek check stays as it is** ([[audio_plan]]); it is the dev's tool for trying values, and the settings are the player's.
- **Tests** in `tests/case/screens.py` and `tests/case/settings.py`; the player readme's Settings section and the changelog.

## Open questions

1. Does the seek speed apply to every held key, the volume keys included, or only to Left and Right? Every held key is simpler, one setting for one loop; Left and Right alone keeps the volumes as they are now.
