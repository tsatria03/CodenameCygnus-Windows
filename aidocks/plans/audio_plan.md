---
name: audio_plan
description: "Plan 3 of 8: playing the story's three audio layers (voice, background, decision) through pygame's mixer, finding each MP3 by its story name, seeking, pausing and volume. Status: planned, questions open."
metadata:
  node_type: memory
  type: project
---

**Status: planned, questions open.** Nothing is built.

Plan 3 of 8 ([[story_export_plan]] lists the order). It stands on [[foundation_plan]] and serves [[story_engine_plan]].

## What the story data shows (v53, counted 2026-10-17)

Each state lists up to three layers, told apart by file name:
- **voice:** the dialogue, one recording per state. There are 756, 225 minutes in all; the median is 15 seconds and the longest 132 seconds.
- **background:** a `back_*` ambience, 16 to 80 seconds long, so it loops. 45 files.
- **decision:** a `decision_*` sound that comes with a choice. `decision_single` is 29 seconds; Holiday Party's six `decision_*_m1e8` sounds are 12 to 15 seconds.

How they combine:
- 454 states have voice and background; 223 have voice, background and decision; 178 have background only; 67 have voice only; 24 have nothing.
- The decision sound comes with the choices: 235 of the 241 states with a decision sound end in a choice, and only 4 choice states have none.
- **The background carries on from state to state.** In 1002 of the transitions, the next state lists the same background file. It must keep playing without restarting.
- A few states list two or three background files at once.

The 10 files in `other/misc/` no state names (`00000Push`, `1930Radio A` to `D`, `Buy`, `PushButton D`, `Sound A`, and two m1e6 backgrounds) are short interface sounds of under a second, plus the two unused backgrounds. Whether the menus use the interface sounds is for [[menus_plan]].

## Decided

- **pygame's mixer plays everything, as MP3** ([[project_python_only]]). Nothing else opens the audio device.
- **The voice streams through `pygame.mixer.music`,** the only pygame player that can start partway through a file. That is what Left and Right (5 seconds back or forward), R (replay) and S (skip to the choices) need ([[story_engine_plan]]).
- **The background and decision sounds are loaded whole as `pygame.mixer.Sound`**, each on its own channel. They are short, and they can loop without a gap.
- **A file is found by its story name:** the name with `.mp3` in place of `.m4a`, looked up by file name anywhere under `game/data/audio/`. A story `m1eN_teaser` is `other/teasers/m1eN.mp3` ([[project_python_only]]).
- **Space and Escape pause every layer together**, and resume them together.
- **The decision sound loops until the player chooses** (the dev, 2026-10-17, from playing the original: "It deffenatly looped. The user was able to tap/speak there choice."). It stops when a choice is made or a timed choice runs out.
- **The decision sound starts once the question's recording has finished, and the background keeps playing under it** (the dev, 2026-10-17: "It played after the recording asked you the question, then the backround ambience would play along with the decision loop sound. Same with holiday party."). So while a choice waits, two layers play: the background and the decision loop. Holiday Party's timed choices work the same way.

## Open questions

- What happens to the background when the next state lists none, or a different one: stop, fade or cut over.
- The volume keys: one overall volume, or separate ones for voice, background and decision.
