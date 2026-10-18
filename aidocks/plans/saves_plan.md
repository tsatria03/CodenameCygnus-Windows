---
name: saves_plan
description: "Plan 6 of 8: what the game remembers and where: progress per episode with the story variables carried between episodes, the place to continue from, heard recordings, achievements, settings and keys, all in %APPDATA%\\CodenameCygnus, with the original's restart warning and a save on every new state. Status: finished."
metadata:
  node_type: memory
  type: project
---

**Status: finished,** both sections confirmed by the dev by ear, the last on 2026-10-18 ("The episode texts look good, same for the agent profile."). Started that day ("Yes please."), with [[menus_plan]]'s section 4, the parts of the menus that need saved progress, built alongside it.

## Built in sections

1. **Progress, Continue and the episodes' states.** `saves/progress.json`; the story carried from episode to episode; the place to continue from, saved at every new state; Continue in the main menu; each episode's state and lock in the episode list; each episode's own buttons by its state; and Restart and Replay with the original's whole warning, erasing what came after. Status: done, confirmed by the dev by ear on 2026-10-18 ("the first section for the game saving plan works perfectly!"), with these changes made then:
   - A completed episode's screen has its completion text as a row straight after Back, such as "Well done, agent! Are you ready to save the hostages...", in place of its description (the dev: "Please put the episode's completed description after the back button for each episode", then "Please drop the description from the finished episode screen. I mean the main episode description"). An episode not finished keeps its description.
   - Continue says "Continuing Art Show." and Replay "Replaying Prologue."; Restart still says "Restarting" (the dev: "when you continue/replay an episode, it should say continuing/replaying x").
   - A locked episode opens its own screen, Back, description, Locked (above).
   - `codenamecygnus/game/progress.py` holds `Progress`: `state_of`, `locked`, `start_variables`, `began_with`, `place` and `continue_episode` to read, and `begin`, `save_place`, `complete` and `restart` to write, each writing the file at once. An entry the file gets wrong is left out, and an unknown episode or `last` is ignored.
   - `Playthrough.enter` keeps `entered_with`, the variables before the state, which is what the place saves.
   - The episode screen begins a fresh start in the file, saves the place at every state played and where S lands, completes the episode at its end, and restarts through `Progress.restart`. Continue and debug jumps start at a state, so they do not begin the episode again.
   - The main menu's first row is "Continue Art Show" while there is a place to go back to. The episode list adds ", in progress", ", completed" or ", locked" to each episode; a locked one opens its own screen too, with Back, its description and Locked. Each episode's own screen offers its buttons by its state, as above, and Restart episode and Replay episode both ask the original's question, "Restart episode? If you restart this episode, all saved progress beyond this episode will be erased.", then say "Restarting Prologue." The pause menu's Restart asks the same.
   - `--episode` starts with what the episode before it ended with, as Start does.
   - `tests/case/progress.py` has 10 tests and `tests/case/menus.py` 8 more; each test gets a fresh progress file.
2. **The agent profile** ([[menus_plan]]): the dominant trait, furthest episode, episodes completed, game progress, the four trait scales and the achievements. Status: done, confirmed by the dev by ear on 2026-10-18 ("The episode texts look good, same for the agent profile."). Built the same day (the dev: "update all docks where possible ... then continue with the implementation").
   - `codenamecygnus/game/profile.py` holds `ProfileScreen` and `AchievementList`, with `dominant_trait` and `scale_text`; the main menu's "Agent profile", between Episodes and Settings, opens it with the original's profile sound, `1930Radio B`.
   - The rows: Back; "Dominant trait: Charismatic." or "none yet"; "Furthest episode: Episode 3, Neptune's Lair." or "none yet"; "Episodes completed: 2 of 8."; "Game progress: 25 percent.", the episodes completed out of eight; the four scales, such as "Diplomacy: Charismatic, 3" or "Activeness: balanced"; and "Achievements: 3 of 16". Enter on a row says it again.
   - **Whose traits:** the story of Mission 1 so far, from the furthest of its episodes started: where it was left, or how it ended once finished (`Progress.mission_variables`). Holiday Party is left out of the traits and the furthest episode, since it resets its own variables and uses none of the mission's; it counts among the episodes completed.
   - **The achievements** are a list of their own, opened from the Achievements row: Back, then all 16, such as "Card Shark, earned. Raise the bet in the Prologue's card game, so that Krasnoff folds." or "Martini, not earned yet. Order the Martini at the hotel bar in Art Show."
   - `tests/case/agent_profile.py` has 8 tests (not `profile.py`, which would hide Python's own `profile` module from the tests).

## How section 1 works

- **One place to continue from per episode in progress,** each its own state and the variables as they were before that state was entered, so Continue entering it again applies its variables once, not twice. The main menu's Continue goes to the one played most recently. (The plan below says "the place to continue from" as one; keeping one per episode lets an episode's own Continue work even after another episode was played since.)
- **What an episode starts with:** the variables the episode that opens it ended with, so Art Show starts with the Prologue's; the Prologue and Holiday Party start from nothing.
- **Each episode's own screen, by its state,** following the original's two buttons (`-[CCEpisodeTableCell setupLeftButton]` and `setupRightButton`, read 2026-10-18), each list Back first ([[feedback_back_first]]) and the description after it:
  - not started: Start
  - in progress: Continue, then Restart episode
  - completed: Replay episode, then Preview next episode where there is one
  - locked: Locked, which says "You need to complete the previous episode before starting this one." when chosen, the original's own words (the dev, 2026-10-18: "For locked episodes, a similar menu should open with the back button, description, then the locked status after it"); at first Enter on a locked episode in the list said its description and the reason without opening a screen
- **Replay is Restart under another name.** The original's `replayEpisode` (0x10002d18c) and `restartEpisode` (0x10002d64c) play the same restart sound and ask the same question, "Restart Episode?" and "If you restart this episode, all saved progress beyond this episode will be erased.", with Cancel and Restart. So both ask that, answered No or Yes, No first, and do the same: the episode starts again with the variables it began with, and every later episode of Mission 1 goes back to locked and not played. The pause menu's Restart episode does the same.
- **The list says each episode's state:** "Episode 2, Art Show, in progress", "completed", "locked", or nothing more while new.

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
  - Before restarting, the game asks with the original's own words, "Restart Episode?" and "If you restart this episode, all saved progress beyond this episode will be erased.", answered Yes or No. The question already exists, from [[story_engine_plan]]'s section 2, as "Restart episode?" with No first; this plan adds the warning's second sentence, once there is saved progress for it to be true of.
  - Restarting an episode starts it again with the variables it began with.
  - Every episode after it goes back to locked and not played, since its story followed the old choices. Its saved variables and place to continue from are erased.
  - Heard recordings, achievements and settings are kept: they belong to the player, not to one playthrough.
  - Holiday Party is never affected by restarting another episode, since it uses none of their variables.

- **The place to continue from is saved periodically, by itself** (the dev, 2026-10-17: "I want it saving periodicly"): every time the story moves to a new state, which is about every 15 seconds in play (the median recording), and again on Return to menu and on closing the game. A crash or a power cut loses at most the recording the player was in. A fixed timer would save nothing more useful, since Continue always goes back to the start of a recording. The files are small and written safely, so saving this often costs nothing noticeable.

## Open questions

None. Ready to build once the dev says so.
