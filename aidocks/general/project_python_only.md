---
name: project_python_only
description: "The port is written entirely in Python, in the codenamecygnus/ package, with pygame for the window, keyboard and audio (the recordings converted to MP3 by the dev), and Prism or the NVDA client for speech."
metadata:
  node_type: memory
  type: project
---

The port is written entirely in Python:
- pygame (not pygame-ce) for the window, the keyboard and the frame loop
- `prismatoid` (Prism) for speech through any screen reader or a Windows voice
- NVDA's own controller client, `vendor/nvda/nvdaControllerClient64.dll`, through ctypes

Don't propose moving parts to another language or engine. Choices are made from the keyboard, and also by voice when speech recognition is on ([[project_speech_recognition]]).

**Why:** The repo was set up this way by the dev: `requirements.txt` holds `pygame>=2.6.1` and `prismatoid~=0.18.2`, and the package folder is `codenamecygnus/`.

**Audio is played as MP3 through pygame** (the dev, 2026-10-17: "I'll convert them myself to mp3 so pygame can play them"). The original recordings are AAC in `.m4a` files, which neither pygame's mixer nor OpenAL can decode. The dev converts them to MP3 on their own machine; Claude never runs the conversion.

**No OpenAL** (the dev, 2026-10-17: "this game will not use openall right?", confirmed). Everything the game plays goes through pygame's mixer, and the microphone through `sounddevice` ([[speech_recognition_plan]]). Do not bring in OpenAL Soft, `cyal` or any OpenAL binding, even where the reference material in `user/` uses one.

**How to apply:**
- Write any new code in Python, inside `codenamecygnus/`.
- The story data still names every recording with `.m4a`. The game looks each one up by its name with `.mp3` in place of `.m4a`, and never edits the original data to match.
- **The dev's own layout of `game/data/audio/`** (reorganized 2026-10-17):
  - `missions/m1/episodes/e1/` to `e8/`: the 756 voice recordings, in `p1` to `p5` folders that match the original's resource collections exactly.
  - `missions/m1/sources/`: the 52 backgrounds and decision sounds, 45 `back_*` and 7 `decision_*`.
  - `missions/m1/teasers/`: the six voiced episode previews, renamed `m1e2.mp3` to `m1e7.mp3`. The story's `m1eN_teaser.m4a` is `teasers/m1eN.mp3`, the name without `_teaser`, so the lookup needs that one mapping.
  - `others/interface/`: the eight interface sounds ([[menus_plan]]).
- **Everything under `missions/` is gitignored and stays on the dev's machine,** the ambiences included, since some of them carry voices when listened to closely (the dev, 2026-10-17: "I found out that I can here voice recordings in some of them upon closer listening"). Only `others/` is in git (the dev: "Do not exclude the others folder").
- The game finds a recording by its file name anywhere under `game/data/audio/`, so a file can move between folders without code changes. Each name appears once.
- Don't move, rename or convert recordings unless the dev asks.
- How the voice, background and decision layers play is in [[audio_plan]].

