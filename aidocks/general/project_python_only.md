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

Don't propose moving parts to another language or engine. The original app's speech recognition is not ported; choices are made from the keyboard.

**Why:** The repo was set up this way by the dev: `requirements.txt` holds `pygame>=2.6.1` and `prismatoid~=0.18.2`, and the package folder is `codenamecygnus/`.

**Audio is played as MP3 through pygame** (the dev, 2026-10-17: "I'll convert them myself to mp3 so pygame can play them"). The original recordings are AAC in `.m4a` files, which neither pygame's mixer nor OpenAL can decode. The dev converts them to MP3 on their own machine; Claude never runs the conversion.

**How to apply:**
- Write any new code in Python, inside `codenamecygnus/`.
- The story data still names every recording with `.m4a`. The game looks each one up by its name with `.mp3` in place of `.m4a`, and never edits the original data to match.
- How the voice, background and decision layers are played (streamed or loaded whole) is still to be decided, in a plan, before any audio code. `pygame.mixer.music` streams only one file at a time.

