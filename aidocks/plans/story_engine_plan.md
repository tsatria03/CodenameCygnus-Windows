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

**In debug mode only** ([[foundation_plan]]), on function keys so they never clash with the story keys (the dev, 2026-10-17: "I agree with the function keys"):
- **F2** skips the current recording, heard or not, and never marks it as heard.
- **F3** jumps to any state: type part of its name and press Enter, and pick from a short spoken list when several match. The names are the ones in `analysis/script/`, so a state found there can be jumped to at once.
- **F4** says the current state's name, the four trait scores and every story flag that is set.

## What "heard before" means for S

Agreed on 2026-10-17 (the dev: "I completely agree with that"):
- **A recording counts as heard once it has reached its end** in any playthrough, whether by playing or by skipping forward with Right. Starting it is not enough. The player who skips to the end with Right has already chosen not to need it.
- **It is remembered for good,** in the save, across every replay and restart of an episode ([[saves_plan]]). Replaying to try other choices is how the game is played, and every episode's opening is the same each time, so forgetting would make S useless exactly when it helps most.
- **On a recording not heard yet, S says "Not heard yet" and does nothing**, so a stray press never skips new story, which a listener cannot glance back at.
- **Debug mode's own skip never counts a recording as heard**, so testing a branch does not mark story the dev never listened to.
- **S skips across every heard recording in a row to the next choice** (the dev, 2026-10-17: "I like the skip across option"), following the automatic transitions as play would. If it reaches a recording not heard yet, it stops there and plays it from the start. Every state passed on the way still does what it does, setting traits and story flags and taking its conditions, so skipping never changes how the story turns out.

## Several automatic exits, and the van escape bug

- **How the original chose:** `-[CCStateMachine performAutoTransition]` (0x100049c00) walks every transition from the current state and takes the first automatic one it finds, skipping the rest. It walks an `NSHashTable` (`CCStateMachine`'s `transitions` property), whose order depends on where objects sit in memory, so with two automatic exits the one taken was effectively arbitrary.
- **Only one state has two:** `3_AAB008transition_m1e7`, in Signum Cygni's van escape. Two choices lead into it:
  - from `3_AAB007matthewsEscapePrompt_m1e7`, where Agent Rhodes shouts "Grab her gun, Agent! Now. GRAB IT!"
  - from `3_AAB007alexEscapePrompt_m1e7`, where Rhodes says the only way back to Alex is to make it look like you are dead, answered with HANG ON
- Its two exits are the two endings: `4_AABA002alexAthleticRefuseMatthewsEND_m1e7`, a struggle for the gun and an escape out the back, and `4_AABB003alexAthleticRefuseAlexEND_m1e7`, where Rhodes says goodbye and jumps. So in the original, a player could say HANG ON and hear the struggle for the gun.
- **The port fixes it** (the dev, 2026-10-17: "This bug needs to be fixed"): GRAB IT leads to the Matthews ending and HANG ON to the Alex ending, as the scenes and the writers' state names say. The fix is made in the data by [[story_export_plan]], so the engine needs no special case.
- **The engine's rule stays the original's:** the first automatic exit wins. In the exported data the transitions keep the file's order, so "first" is always the same one.

## The script

Each state's `script` is the text of what its recording says, in three kinds of line: `SPEECH` with a character's name, `PARENTHETICAL` for sounds such as "(GUNSHOT)", and `HEADING` for a scene, such as "CONSULATE - BOMB ROOM" (63 in all).

- **The screen reader does not read the dialogue,** since every line is voiced.
- **Scene headings are spoken only when the player presses H** (the dev, 2026-10-17: "Only when you press H"). An automatic heading would talk over the scene's first words. H says the latest heading reached.
- **The window shows the script as it plays**, headings included ([[foundation_plan]]).
- **The `#a,b#` marks only pace the on-screen text.** `-[CCScrollingTextView presentScript:]` (0x1000280a8) splits each line at `#` and each mark at `,` into reveal steps it calls ticks, which `tick` (0x100028d1c) steps through as the recording plays. The second number is how long to wait before the next piece appears (`insertTicks:toArray:`, 0x100028c80, pads empty steps for the wait), and the first says whether to clear the text so far first (`tickClears`). Speech drops them, and the window may use them or show each line whole.

## Open questions

- What happens at the 23 states that earn an achievement, now that there is no Game Center.
