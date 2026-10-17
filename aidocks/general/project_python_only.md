---
name: project_python_only
description: "The port is written entirely in Python, in the codenamecygnus/ package, with pygame for the window and keyboard and Prism or the NVDA client for speech."
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

**How to apply:** Write any new code in Python, inside `codenamecygnus/`. The audio library and the format the `.m4a` recordings are played in are still to be decided, in a plan, before any audio code.
