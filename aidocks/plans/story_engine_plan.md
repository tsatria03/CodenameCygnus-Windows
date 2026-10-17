---
name: story_engine_plan
description: "Plan 4 of 8: playing the story graph: states, choices, automatic, conditional and timed transitions, variables and traits, and the keys a player uses during an episode. Status: planned, questions open; the keys are agreed."
metadata:
  node_type: memory
  type: project
---

**Status: planned, questions open.** Nothing is built. The keys were agreed first, while [[foundation_plan]] was being written.

Plan 4 of 8 ([[story_export_plan]] lists the order).

## Keys during an episode

Agreed on 2026-10-17 (the dev: "I like all of it"). They follow the original's game screen: its replay button, its slider for skipping back and forth through the current recording, its choice buttons and its voice button. Every key can be rebound on the F1 screen ([[foundation_plan]]).

**While a choice is offered:**
- **Up and Down** move through the choices, each spoken with its place, such as "Charismatic, 1 of 2".
- **Enter** chooses the one you are on.
- **1 to 9** choose by number directly, which matters most for Holiday Party's 7-second choices.
- **C** says the choices again.

**While the story plays:**
- **Space** pauses and resumes.
- **R** replays the current recording from the start, like the original's replay button.
- **Left and Right** skip back or forward 5 seconds, like the original's slider.
- **S** skips straight to the choices, but only for a part the player has heard before (the dev, 2026-10-17: "pressing S should skip straight to the choices if the user has played that part before. It's a shortcut for left/right"). It is a shortcut for skipping forward with Right until the choices come.

**At any time:**
- **H** says where you are: the scene heading, such as "Consulate, bomb room".
- **V** turns speech recognition on or off, like the original's voice button ([[project_speech_recognition]]).
- **Escape** opens the pause menu: Resume, Restart episode and Return to menu.
- **F1** opens the key bindings screen.
- **Shift with Home and End** set the master volume, **Page Up and Page Down** the ambience, and **Shift with Page Up and Page Down** the decision loop ([[audio_plan]]).

**In debug mode only** ([[foundation_plan]]): skip the current recording whether heard or not, jump to any state by name, and hear the trait scores and story flags. Their keys are still to be chosen.

## Open questions

- What counts as "heard before" for S, how long that is remembered, and what S says on a part not heard yet. Remembering it across runs belongs in [[saves_plan]].
- Whether S passes over several automatic states in a row to the next choice, or only the current recording.
- Which of the two automatic transitions `3_AAB008transition_m1e7` takes.
- How the script is used: whether the scene headings and the `#a,b#` pacing marks matter to a screen reader player.
- The debug keys.
