---
name: audio_plan
description: "Plan 3 of 8: playing the story's three audio layers (voice, background, decision) through pygame's mixer, finding each MP3 by its story name, seeking, pausing, the decision loop, the original's hard background cuts and three volumes. Status: finished."
metadata:
  node_type: memory
  type: project
---

**Status: finished,** confirmed by the dev on 2026-10-17 after hearing it through `tests/interact/audio_check.py` ("The interactive test worked."). Built 2026-10-17 (the dev: "Yes."):
- `codenamecygnus/platform/audio.py`: the voice through `pygame.mixer.music` (started partway with `play(start=)`, for Left, Right, R and S), the background on channel 0, the decision loop on channel 1 and the menu sounds on channel 2, pausing all together, and the three volumes as squared gains. pygame says a paused voice is not playing, so pausing is tracked by the module itself, and a voice is believed finished only after a quarter of a second of play. pygame cannot give a streamed MP3's length, so `mp3_length` reads it from the file's headers (a Xing, Info or VBRI frame count, or the bitrate). Only the background playing is kept decoded in memory. With no sound device, the game carries on silent.
- `codenamecygnus/game/recordings.py`: a story file name found as its MP3 anywhere under `game/data/audio/`, in any letter case, the previews without `_teaser`. The pack `m1.dat` will feed the same `Recording` objects ([[build_release_plan]]).
- `codenamecygnus/app.py` opens the sound device as the game starts, updates the audio every frame and closes it at the end.
- `tests/case/audio.py` (13 tests) and `tests/case/recordings.py` (6), all passing on SDL's dummy sound driver, so nothing is heard.
- `tests/interact/audio_check.py`, a tool to hear it by ear before the story engine exists: it plays a story state's layers, N moving on to the next state, with the episode's keys and its own save.

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
- A few states list two or three background files at once. In the original each one replaced the last, so the last listed is the one heard.

**Choosing the skip length:** `tests/interact/seek_check.py` (the dev, 2026-10-18: "Pressing a/d will increase the seak speeds, and pressing left/right will seak based on the speed you set. I want to see what speed I like the best") plays the 20 longest recordings, with A and D setting the skip at 1, 2, 3, 5, 10, 15, 20, 30 or 60 seconds, and Q and E the repeat rate while Left or Right is held, every 500 down to 50 milliseconds in steps of 50 (the dev: "Please make q and e the repeat rate", then "It should only be 50, 100, 150, 200, 250, 300, 350, 400, 450, and 500"), changing `REPEAT_EVERY` for the tool alone; the 0.4-second wait before repeating stays the game's. The game's `SKIP_SECONDS` stays 5, until the dev picks another; the dev picked a repeat of 100 milliseconds with it (2026-10-18: "I want the new repeat rate to be 100ms"), so `REPEAT_EVERY` is 0.1, and the tool itself was left as it was ("Do not modify it").

The 10 files no state names are the eight interface sounds of under a second in `others/interface/` (`00000Push`, `1930Radio A` to `D`, `Buy`, `PushButton D`, `Sound A`), which [[menus_plan]] uses, and two unused m1e6 backgrounds in `missions/m1/sources/`.

## Decided

- **pygame's mixer plays everything, as MP3** ([[project_python_only]]). Nothing else opens the audio device.
- **The voice streams through `pygame.mixer.music`,** the only pygame player that can start partway through a file. That is what Left and Right (5 seconds back or forward), R (replay) and S (skip to the choices) need ([[story_engine_plan]]).
- **The background and decision sounds are loaded whole as `pygame.mixer.Sound`**, each on its own channel. They are short, and they can loop without a gap.
- **In a built game, the mission recordings come from the encrypted pack `m1.dat`** in the save folder, read one recording at a time into memory ([[build_release_plan]]). `pygame.mixer.music.load` and `pygame.mixer.Sound` both take a file-like object, so the voice still streams and seeks, and the background and decision sounds still loop.
- **A file is found by its story name:** the name with `.mp3` in place of `.m4a`, looked up by file name anywhere under `game/data/audio/`. A story `m1eN_teaser` is `missions/m1/teasers/m1eN.mp3` ([[project_python_only]]).
- **Space and Escape pause every layer together**, and resume them together.
- **The decision sound loops until the player chooses** (the dev, 2026-10-17, from playing the original: "It deffenatly looped. The user was able to tap/speak there choice."). It stops when a choice is made or a timed choice runs out.
- **The decision sound starts once the question's recording has finished, and the background keeps playing under it** (the dev, 2026-10-17: "It played after the recording asked you the question, then the backround ambience would play along with the decision loop sound. Same with holiday party."). So while a choice waits, two layers play: the background and the decision loop. Holiday Party's timed choices work the same way.

- **The background follows the original exactly, with a hard cut** (the dev, 2026-10-17: "I want the original's hard cut"). Read from the arm64 code of `game/Cygnus` with capstone on 2026-10-17, which is not encrypted (`cryptid` 0):
  - **The same background carries on untouched.** `-[CCSoundManager playBackgroundMedium:]` (0x10002501c) compares the new file's URL with the playing one's (`isEqualToString:`) and returns if they match.
  - **A different background cuts over.** It calls `stopBackgroundPlayer` (0x100024ba8), which only calls `stop` on the player, then starts the new file. There is no fade: the binary never sets a player's volume.
  - **Every background loops forever** (`setNumberOfLoops:` with -1).
  - **A state with no background stops it,** whether it has a voice or nothing at all. `-[CCSoundManager startPlaying]` (0x100024d64) calls `stopBackgroundPlayer` when none of the state's media was a background. None of the 24 states with no audio sits between two states with the same background, so this never interrupts a scene.
  - **The media types** are sorted in the block at 0x100024ed8 by `mediumType`: 2 is the voice, played at once; 1 is the decision sound, kept for later; 0 is the background.
  - The earlier choice of a one-second crossfade, made before the code was read, is dropped.

- **Three volumes, each from 0 to 100% in steps of 10** (the dev, 2026-10-17: "Home/end should be for master volume, and then page up/down for ambience volume", then "Shift page up/down. For master, do shift home/end"):
  - **Shift with Home and End:** the master volume, everything together, Shift+Home louder and Shift+End quieter. The voice follows it, so it stays the loudest thing the player controls.
  - **Page Up and Page Down:** the ambience, the `back_*` backgrounds.
  - **Shift with Page Up and Page Down:** the decision loop, the `decision_*` sounds.
  - Each press says the new level, such as "Background ambience volume 60 percent", and the game remembers all three ([[saves_plan]]). The ambience and decision volumes were first called "Ambience" and "Decision sound", renamed by the dev on 2026-10-18 ([[menus_plan]]).
  - Plain Home and End stay free, so in menus they jump to the first and last row.
  - Since 2026-10-18 a press moves a volume by the Volume step, 10 percent at first, and a volume is any multiple of 5 ([[seek_settings_plan]]).

## Open questions

None.
