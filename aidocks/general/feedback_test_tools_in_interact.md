---
name: feedback_test_tools_in_interact
description: "A tool for trying something by ear, such as an episode chooser, goes in tests/interact/ as its own script, never into the game's menus."
metadata:
  node_type: memory
  type: feedback
---

A tool the dev uses to try a feature by ear goes in `tests/interact/` as its own script, beside `audio_check.py` and `episode_check.py`, never into the game itself or its stand-in menus.

**Why:** asked for "an interactive episode chooser so I can test it without typing any commands", Claude added an Episodes row to the stand-in main menu, and the dev said (2026-10-17): "I wanted the chooser in tests/interact. Not in the main game." It was reverted and remade as `tests/interact/episode_check.py`.

**How to apply:** when the dev asks for a way to test or try something, make a `tests/interact/` script with its own save folder under `%APPDATA%\CodenameCygnus` (so the game's volumes and keys are untouched), and leave the game's screens as their plans say ([[feedback_dont_run_or_build]], [[menus_plan]]).
