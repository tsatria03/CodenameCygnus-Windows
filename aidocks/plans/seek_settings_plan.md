---
name: seek_settings_plan
description: "Four Settings rows, each with its own levels as a volume has: Volume step (percent), Volume speed (milliseconds), Seek step (seconds), Seek speed (milliseconds); volume keys and seeking repeat independently; volumes become any whole percent. Status: planned, one question open."
metadata:
  node_type: memory
  type: project
---

**Status: planned,** not built. Asked for on 2026-10-18 (the dev: "I think this would be the last feature I'd want, but it needs planning first"), after choosing the game's own repeat by ear with `tests/interact/seek_check.py` ([[audio_plan]]). Widened the same day to four settings (the dev: "Please make the variables independent. One for volume speed, and one for seek speed. Speaking of volume, I also want volume step as well. So it goes like this. Volume step, volume speed, seek step, seek speed. The volume step measures in percentages, like 1, 5, 10, etc.").

## Why independent

Until now the game has one repeat for every held key, `REPEAT_EVERY` in `app.py`: Left and Right while the story or a preview plays, and the six volume keys. The dev took it to control seeking only ("I didn't know that was a global speed"). So seeking and the volumes each get a speed of their own.

## Proposed

- **Four rows in Settings,** in the dev's order, after the three volumes and before Speech recognition ([[menus_plan]]), named by the dev ("I like seek step and seek speed", then the four above; "Seek interval" was set aside as reading like the time between repeats):
  - "Volume step, 10 percent": how much a volume key changes a volume.
  - "Volume speed, 100 milliseconds": how often a held volume key repeats.
  - "Seek step, 5 seconds": how far each press of Left or Right goes.
  - "Seek speed, 100 milliseconds": how often a held Left or Right repeats.
- **Each opens its levels,** as a volume's row opens `VolumeLevels`: Back first and opening on it ([[feedback_back_first]]), then the levels. Enter sets one, goes back to Settings and says it, such as "Seek step 10 seconds"; Escape keeps the old one.
  - Volume step: 1, 2, 5, 10, 20 and 25 percent.
  - Volume speed and Seek speed: 50, 100, 150 ... 500 milliseconds in steps of 50 (the dev, 2026-10-18: "It should only be 50, 100, 150 ... and 500"), fastest first, as the volumes go from loudest. The ends say which way they go, "50 milliseconds, fastest" and "500 milliseconds, slowest", since a smaller number is faster.
  - Seek step: 1, 2, 3, 5, 10, 15, 20, 30 and 60 seconds, the seek check's steps.
- **Defaults are what the game does now:** volume step 10, volume speed 100, seek step 5, seek speed 100. Saved in `config/settings.json` ([[saves_plan]]) as `volume_step`, `volume_speed`, `seek_step` and `seek_speed`; a value not among its levels is put back to its default.
- **Volumes become any whole percent, 0 to 100,** not only tens, so a step of 1 or 5 can reach 35 or 72. A volume key moves by the step and stops at 0 and 100, so 95 up by 10 is 100. Saved volumes, all in tens now, stay as they are.
- **Held keys:** the main loop asks the top screen how often a held key repeats, not only whether it does, so the episode screen and a preview answer Seek speed for Left and Right and Volume speed for the volume keys. The 0.4-second wait before a held key starts repeating stays one fixed wait for both, not a setting.
- **Used at once,** from the main menu's Settings or the pause menu's.
- **The seek check stays as it is** ([[audio_plan]]): the dev's tool for trying values, while these are the player's.
- **Tests** in `tests/case/settings.py`, `screens.py`, `app.py`, `audio.py` and `episode.py`; the player readme's Settings section and the changelog.

## Open questions

1. A volume's levels list, opened from its Settings row, is 100 percent down to 0 in tens now. With a volume step of 5 or 1, should the list follow the step (21 levels at 5, 101 at 1), or stay in tens, with the volume keys reaching the values in between?
