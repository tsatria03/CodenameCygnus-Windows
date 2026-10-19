---
name: seek_settings_plan
description: "Four Settings rows, each with its own levels as a volume has: Volume step (percent), Volume speed (milliseconds), Seek step (seconds), Seek speed (milliseconds); volume keys and seeking repeat independently; volumes become multiples of 5, their levels following the step; the volume keys work in previews. Status: planned, no questions open."
metadata:
  node_type: memory
  type: project
---

**Status: planned,** not built. Asked for on 2026-10-18 (the dev: "I think this would be the last feature I'd want, but it needs planning first"), after choosing the game's own repeat by ear with `tests/interact/seek_check.py` ([[audio_plan]]). Widened the same day to four settings (the dev: "Please make the variables independent. One for volume speed, and one for seek speed. Speaking of volume, I also want volume step as well. So it goes like this. Volume step, volume speed, seek step, seek speed. The volume step measures in percentages, like 1, 5, 10, etc."). The levels, the volume list and the volume keys in previews were settled the same day.

## Why independent

Until now the game has one repeat for every held key, `REPEAT_EVERY` in `app.py`: Left and Right while the story or a preview plays, and the six volume keys. The dev took it to control seeking only ("I didn't know that was a global speed"). So seeking and the volumes each get a speed of their own.

## Proposed

- **Four rows in Settings,** in the dev's order, after the three volumes and before Speech recognition ([[menus_plan]]), named by the dev ("I like seek step and seek speed", then the four above; "Seek interval" was set aside as reading like the time between repeats):
  - "Volume step, 10 percent": how much a volume key changes a volume.
  - "Volume speed, 100 milliseconds": how often a held volume key repeats.
  - "Seek step, 10 seconds": how far each press of Left or Right goes.
  - "Seek speed, 100 milliseconds": how often a held Left or Right repeats.
- **Each opens its levels,** as a volume's row opens `VolumeLevels`: Back first and opening on it ([[feedback_back_first]]), then the levels. Enter sets one, goes back to Settings and says it, such as "Seek step 10 seconds"; Escape keeps the old one.
  - Volume step: 5, 10, 20 and 25 percent (the dev, 2026-10-18: "for volume step, it should be 5, 10, 20, 25").
  - Volume speed and Seek speed: 50, 100, 150 ... 500 milliseconds in steps of 50 (the dev, 2026-10-18: "It should only be 50, 100, 150 ... and 500"), fastest first, as the volumes go from loudest. The ends say which way they go, "50 milliseconds, fastest" and "500 milliseconds, slowest", since a smaller number is faster.
  - Seek step: 5, 10, 15, 20, 30 and 60 seconds (the dev, 2026-10-18: "For seek step, it should be 5, 10, 15, 20, 30, 60"), the seek check's steps too.
- **Defaults:** volume step 10, volume speed 100 and seek speed 100, as the game does now, and seek step 10 seconds, up from today's 5 (the dev, 2026-10-18: "The default seek step should be 10 seconds, not 5"); `SKIP_SECONDS` in `audio.py` gives way to the setting. Saved in `config/settings.json` ([[saves_plan]]) as `volume_step`, `volume_speed`, `seek_step` and `seek_speed`; a value not among its levels is put back to its default.
- **Volumes become any multiple of 5, 0 to 100,** not only tens, since every step is a multiple of 5: a step of 5 can reach 35. A volume key moves by the step and stops at 0 and 100, so 95 up by 10 is 100. Saved volumes, all in tens now, stay as they are.
- **A volume's levels follow the step** (the dev, 2026-10-18: "The volume step should follow the volume settings in the settings screen"): its list in Settings goes from 100 percent down to 0 by the volume step, 21 levels at 5, 11 at 10, 6 at 20 and 5 at 25. Every step divides 100, so 100 and 0 are always in the list. A volume the list does not hold, such as 35 with a step of 10, is still said on its Settings row and kept until a level is chosen.
- **The volume keys work in previews too** (the dev, 2026-10-18: "You should also be able to change the volumes when previewing an episode as well. I mean the volume keys"): the six keys change the volumes while a preview plays, as in the story, and repeat at Volume speed when held. Until now they worked only in the story.
- **Held keys:** the main loop asks the top screen how often a held key repeats, not only whether it does, so the episode screen and a preview answer Seek speed for Left and Right and Volume speed for the volume keys. The 0.4-second wait before a held key starts repeating stays one fixed wait for both, not a setting.
- **Used at once,** from the main menu's Settings or the pause menu's.
- **The seek check keeps to the same limits** ([[audio_plan]]; the dev, 2026-10-18: "modify the seek checker to enforce these new min/max limmits"): A and D move through the Seek step's levels, 5 to 60 seconds, no longer 1 to 60, and Q and E through the speeds', 500 to 50 milliseconds, which they already did. Done before the settings are built; once they are, it starts on their defaults and says them as the game's.
- **Tests** in `tests/case/settings.py`, `screens.py`, `app.py`, `audio.py` and `episode.py` (the previews' tests are there too); the player readme's Settings and preview keys, and the changelog.

## Open questions

None. The one question, whether a volume's levels list follows the step, the dev answered on 2026-10-18: it does.
