---
name: saves_plan
description: "Plan 6 of 8: what the game remembers and where: progress per episode with the story variables carried between episodes, the place to continue from, heard recordings, achievements, settings and keys, all in %APPDATA%\\CodenameCygnus, with the original's restart warning and a save on every new state. Status: planned, ready to build."
metadata:
  node_type: memory
  type: project
---

**Status: planned, ready to build.** Every question is answered; nothing is built.

Plan 6 of 8 ([[story_export_plan]] lists the order). Every player starts from scratch; nothing is read from the original's database ([[project_story_data_source]]).

## What the story needs (v53, checked 2026-10-17)

**Story variables carry from episode to episode.** Signum Cygni, the last episode, checks choices made in every earlier one:
- the Prologue's `npc_state.tomassi` and `npc_state.schafer`
- Art Show's `event.m1e2_distraction`, `event.m1e2_serum` and `event.m1e2_syringeUse`
- Neptune's Lair's `event.m1e3_entry` and `event.m1e3_defeatGuards`
- Consulate's `event.m1e4_chooseTrust`, also checked in Lazarus Awakens
- Lazarus Awakens' `event.m1e5_savedLili` and `inventory.m1e5_lazarusCard`
- Art Show's `romance.m1_maleInterest` is checked in every episode up to Lazarus Awakens.

The four traits also run through the whole mission. Holiday Party uses none of the other episodes' variables: it resets its own at its start.

**The original kept one save per episode** (the `ZCCSAVE` table: an episode, its last state, and every variable as an archived dictionary, `ZVARIABLESJSON`). Restarting warned: "If you restart this episode, all saved progress beyond this episode will be erased."

## Decided

- **One folder, `%APPDATA%\CodenameCygnus`** ([[foundation_plan]]), in short JSON files written safely (a temporary file, a `.bak` of the old one, then a swap):
  - `saves/progress.json`: each episode's state (new, in progress, completed), the variables it began with and ended with, and the place to continue from: the episode, its current state and the variables there.
  - `saves/heard.json`: every recording heard to its end, kept for good ([[story_engine_plan]]).
  - `saves/achievements.json`: the achievements earned, kept for good.
  - `config/settings.json`: speech recognition, the three volumes, debug mode, and whether the headphones notice has been shown.
  - `config/keys.json`: the key bindings.
  - `logs/`: `log.txt`, `log.old.txt` and `crash.txt`.
  - `missions/m1.dat`: Mission 1's recordings, downloaded by the game ([[build_release_plan]]). Starting over never deletes it.
- **An episode starts with the variables the one before it ended with,** so every choice reaches the episodes that check it. The Prologue and Holiday Party start from nothing.
- **Continue goes back to the start of the recording the player left in,** with the variables as they were when that state began ([[menus_plan]]).

- **Restart works as the original's warning says** (the dev, 2026-10-17: "I like the original's warnings"):
  - Before restarting, the game asks with the original's own words, "Restart Episode?" and "If you restart this episode, all saved progress beyond this episode will be erased.", answered Yes or No.
  - Restarting an episode starts it again with the variables it began with.
  - Every episode after it goes back to locked and not played, since its story followed the old choices. Its saved variables and place to continue from are erased.
  - Heard recordings, achievements and settings are kept: they belong to the player, not to one playthrough.
  - Holiday Party is never affected by restarting another episode, since it uses none of their variables.

- **The place to continue from is saved periodically, by itself** (the dev, 2026-10-17: "I want it saving periodicly"): every time the story moves to a new state, which is about every 15 seconds in play (the median recording), and again on Return to menu and on closing the game. A crash or a power cut loses at most the recording the player was in. A fixed timer would save nothing more useful, since Continue always goes back to the start of a recording. The files are small and written safely, so saving this often costs nothing noticeable.

## Open questions

None. Ready to build once the dev says so.
