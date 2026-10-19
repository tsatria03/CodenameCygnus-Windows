---
name: story_engine_plan
description: "Plan 4 of 8: playing the story graph: states, choices, automatic, conditional and timed transitions, variables and traits, and the keys a player uses during an episode, S and what counts as heard, the debug keys, scene headings on H, the van escape fix, and 16 local achievements. Status: finished."
metadata:
  node_type: memory
  type: project
---

**Status: finished,** all five sections confirmed by the dev by ear, the last on 2026-10-18 ("The achievements works."). The keys were agreed first, while [[foundation_plan]] was being written. What stays for later plans: the episode list, the end-of-episode menu and the agent profile's achievements ([[menus_plan]]); carrying the variables between episodes, Continue and the restart warning's second sentence ([[saves_plan]]); and V ([[speech_recognition_plan]]).

## Built in five sections

The dev asked on 2026-10-17 for it to be done in sections ("This next part should be done in sections"), and agreed to these ("Yes"). Each section is built and tested, the dev tries it, and the next starts only once the dev says it works.

1. **The story's rules, with no sound:** loading `states.json` and `missions.json`, the story variables (set, raised, lowered), the conditions, where each state goes next (the first automatic exit wins), the choices and the timed choices. Tests only, since there is nothing to hear. Status: done, confirmed by the dev on 2026-10-17 ("Section 1 is good"). `codenamecygnus/game/story.py` holds `Story` (the states, their ways out and the episodes), `State` (its voice, background and decision sound, the last background listed winning, and its scene heading), `Choice` (hidden ones offered only when asked for) and `Playthrough` (one run: `enter` applies a state's variables and notes its achievements, then `after_voice`, `choose` and `time_out`). A variable never set counts as 0, as a missing value did in the original. `tests/case/story.py` has 16 tests, all passing, among them 60 random playthroughs of each episode, every one reaching its end. Holiday Party sends a wrong choice back to the start of the party, so a random run there passes about 1,600 states at the median and up to 15,000 (300 runs measured, all finishing), which set the test's limit.
2. **Playing an episode:** the episode screen playing the states through the audio ([[audio_plan]]), reading the choices after the question, Up, Down, Enter and 1 to 9 to choose, C, Space, R, Left and Right, H, the 7-second timed choices, `--episode` to start one, and a plain "Episode complete" at its end. Status: done, confirmed by the dev on 2026-10-17 after trying it through `tests/interact/episode_check.py` and asking for three changes, the choices' Left, Right, Home and End, Restart episode and held keys ("There we go. It works."). Escape opens the pause menu, Resume, Restart episode, Settings and Return to menu; the end-of-episode menu comes with [[menus_plan]]. Restart episode asks "Restart episode?", No first and Escape as No, and Yes starts the episode again with the variables it began with; [[saves_plan]] adds the original's warning about saved progress once there is any (the dev, 2026-10-17, after trying it: "a restart button after resume"). `codenamecygnus/game/episode_screen.py` holds `EpisodeScreen` and `PauseMenu`:
   - Once the question's recording ends, the first choice is focused and said by its word alone, such as "Charismatic", as a menu says its row, waiting behind anything the player made the game say; C says them all together, "Charismatic or Hostile." (the dev, 2026-10-17: "When there are more than 1 choice on screen, it should auto focus to it and speak the first one"; at first all were read together). The first choice is the one you are on as they are read, so Enter at once chooses it, Down goes to the second and Up wraps to the last (the dev, 2026-10-17: "When a choice appears, pressing enter should activate the first focused option"; at first nothing was picked until an arrow was pressed, and Enter read the choices again). Choosing says the word, so a number key is confirmed.
   - R at a choice asks the question again, stopping the decision loop, and offers the choices after it; a timed choice's 7 seconds start again then.
   - The story pauses by itself while the pause menu or F1 covers it and while the window has lost the keyboard, and carries on when it comes back, unless it was paused through the pause menu. A paused timed choice keeps its seconds: the clock's call is cancelled and remade with what was left, so the F1 screen's hold of the timers never clashes with a pause.
   - `tests/interact/episode_check.py` is a tool to try it by ear: a list of all eight episodes, every one open, Enter starting one and leaving it coming back to the list, with its own save (the dev, 2026-10-17: "Can you please make an interactive episode chooser so I can test it without typing any commands?", then "I wanted the chooser in tests/interact. Not in the main game."). The stand-in main menu stays Settings and Quit.
   - `--episode 1.3.1` opens the episode with the stand-in main menu waiting silently underneath (`ScreenStack.put_under`), so Return to menu has somewhere to go. An episode that does not exist logs a warning and opens the menu.
   - V and the debug keys wait for section 4 and the speech recognition plan; V says "Speech recognition is not ready yet."
   - `tests/case/episode.py` drives it with a stand-in audio that notes what it was asked to play.
3. **Heard recordings and S:** `saves/heard.json` and S skipping across heard recordings to the next choice. Status: done, confirmed by the dev by ear on 2026-10-18 ("S also works perfectly."). Built 2026-10-17 (the dev: "Now all we need is S for skipping.").
   - `codenamecygnus/game/heard.py` keeps every recording heard to its end by its story key, such as `016f_contactmark`, writing the file when a new one is heard. The episode screen notes a voice when it ends, by playing through or by Right past its end, and only when it was found on disk.
   - S follows the rules below: "Not heard yet" on a new recording, "Already at the choices" while a choice waits, and otherwise on through `Playthrough.after_voice` across every heard recording, each state entered as play would. At a choice or the end it acts as if that voice had just finished: the decision loop, the choices and any clock. At a recording not heard yet it plays it from its start. The background is the one of the state it stops at.
   - S plays the original's skip sound, `PushButton D`, as [[menus_plan]] says.
   - **Making a choice plays the same sound,** added after the plan was finished (the dev, 2026-10-18: "What I wanted is a sound that plays when you select a choice in an episode", then "Use that same sound for choices as well"). Enter and the number keys choose without speaking ("I also do not want it to speak if you press enter on a choice"), since the choice was said as it was moved to; a spoken choice is still said back ([[speech_recognition_plan]]).
   - Restart keeps the same heard list, which belongs to the player.
   - `tests/interact/episode_check.py` keeps its own `heard.json` in its own save, so S there knows only what was heard through the tool.
   - `tests/case/episode.py` has 6 tests for it, among them skipping a Prologue played before and ending with the same variables as playing it.
4. **Debug mode:** F2, F3, F4 and `--state`. Status: done, confirmed by the dev by ear on 2026-10-18 ("It works."), with two changes made then: Escape in F3's prompt says "Canceled." ("pressing escape after f3 should say canceled"), and F2 plays the skip sound, `PushButton D`, as S does ("f2 should play the skip sound").
   - `codenamecygnus/game/debug.py` holds F3's `JumpScreen` and `MatchMenu` and F4's `state_report`; the episode screen's `do_debug_skip`, `do_debug_jump`, `do_debug_state` and `jump` use them. The keys work only in debug mode, through the key map's `debug` flag.
   - **F2** goes on as if the recording had ended, heard or not, without noting it heard; at a choice it says "Already at the choices."
   - **F3** opens "Jump to a state." Letters and digits are typed and echoed, Shift with a letter types a capital and Shift with Minus an underscore, Backspace takes the last off and says it, and Escape goes back to the story. Enter jumps at once when one name holds what was typed, or one matches exactly; lists the matches when there are up to 40, Enter on one jumping there; and asks for more of the name when there are more. Matching ignores letter case.
   - **Cut, copy and paste in F3's prompt** (the dev, 2026-10-18: "add the ability to cut/copy/paste in the input prompt so I don't have to hand type the states if you give me some to test"): Ctrl+V adds the clipboard's first line, trimmed, and a "State: " before it is dropped, so a line copied from `analysis/script/` pastes as the name; it says "Pasted" and the text. Ctrl+C copies what is typed and Ctrl+X cuts it, each saying so. `codenamecygnus/platform/clipboard.py` uses Windows' own clipboard through ctypes, since pygame's clipboard support differs between versions. The tests use a stand-in and never touch the real clipboard; the dev confirmed all three on the real one on 2026-10-18 ("the cut/copy/paste methods past").
   - **A jump to a state in another episode** starts that episode there, carrying the variables over, so its end and Return to menu work. `Story.episode_of` finds each state's episode from the episodes' starts; no state is in two episodes. The six previews and the two cut states belong to none, and a jump to one stays in the episode playing. "Jumped to 012introRejectPrompt, in Prologue." is said after.
   - **F4** says "State 001introOpen. Openness 0, Predictability 0, Diplomacy 0, Activeness 0. Flags: ...", every variable that is not a trait, by name, with its value.
   - **`--state NAME`** in debug mode starts the episode that state is in, at that state; out of debug mode, or for a state that does not exist, the log says it is ignored.
   - `Playthrough.enter` decides afresh at every state whether the episode has reached its end, so a jump away from the end state goes on playing.
   - `tests/interact/episode_check.py` turns debug mode on, so the three keys work there.
   - `tests/case/episode.py` has 10 tests for it, and `tests/case/story.py` one for `episode_of`.
5. **Achievements:** the 16, announced at a quiet moment and saved in `saves/achievements.json`. Status: done, confirmed by the dev by ear on 2026-10-18 ("The achievements works."). Built the same day (the dev: "yes").
   - `codenamecygnus/game/achievements.py` holds the 16 with their approved names and descriptions (listed below), keyed by the original's id without `net.reactivestudios.codenamecygnus.`, and `Achievements`, the earned ones kept for good in `saves/achievements.json` and written when one is first earned. The data has exactly these 16 ids, at 23 states, which a test checks.
   - The episode screen's `collect` notes what every state entered has earned, whether reached by play, S, F2 or a jump, and keeps it at once, so a crash never loses one. `announce` says "Achievement earned: Card Shark." at the next quiet moment: before the first choice is said, or after "Episode complete!" and the completion text, before the end menu ([[menus_plan]]) Each waits behind what was being said and is never said over the story.
   - Only the first time an achievement is ever earned is it announced; earning it again in a replay is silent.
   - Restart and a jump into another episode keep the same list.
   - `tests/interact/episode_check.py` keeps its own `achievements.json` in its own save.
   - `tests/case/episode.py` has 5 tests for it. The agent profile's list comes with [[menus_plan]].

Plan 4 of 8 ([[story_export_plan]] lists the order).

## Keys during an episode

Agreed on 2026-10-17 (the dev: "I like all of it"). They follow the original's game screen: its replay button, its slider for skipping back and forth through the current recording, its choice buttons and its voice button. Every key can be rebound on the F1 screen ([[foundation_plan]]).

**While a choice is offered:**
- **Up and Down** move through the choices, each spoken by its word alone, such as "Charismatic", never with its place (the dev, 2026-10-17: "The story choices should also ditch the menu positions as well"). They wrap round, as the menus do.
- **Enter** chooses the one you are on.
- **1 to 9** choose by number directly, which matters most for Holiday Party's 7-second choices.
- **C** says the choices again.
- **Left and Right** move through the choices as Up and Down do, and **Home and End** go to the first and last (the dev, 2026-10-17, after trying section 2: "left/right/home/end navigation in the choices list"). The question's recording has ended by then, so there is nothing for Left and Right to skip through.

**While the story plays:**
- **Space** paused and resumed at first; it was removed on 2026-10-18 (the dev: "Can you remove space to pause? I feel like escape already does the job"). Escape pauses, with the pause menu, and Resume or Escape there carries on. P does the same as Escape, in the story and in a preview (the dev, 2026-10-18: "For pausing, add p to that list along with escape"): it is the key map's `pause_menu` action, "Pause menu" on the F1 screen, so it can be rebound, while Escape stays fixed; it has a new name so the old `pause` binding, Space, cannot come back with it. The `pause` action is gone from the key map and the F1 screen, and a pause binding left in an old keys file is dropped. A preview's Space went too, the same day (the dev: "Remove it from the preview as well"); a preview's Escape now pauses it, with its own pause menu ([[menus_plan]]).
- **R** replays the current recording from the start, like the original's replay button.
- **Left and Right** skip back or forward 5 seconds, like the original's slider.
- **S** skips straight to the choices, but only for a part the player has heard before (the dev, 2026-10-17: "pressing S should skip straight to the choices if the user has played that part before. It's a shortcut for left/right"). It is a shortcut for skipping forward with Right until the choices come.

**At any time:**
- **H** says where you are: the scene heading, such as "Consulate, bomb room".
- **V** turns speech recognition on or off, like the original's voice button ([[project_speech_recognition]]).
- **Escape** opens the pause menu: Resume, Restart episode, Settings and Return to menu ([[menus_plan]]).
- **Holding a key repeats it** for Left and Right while the story plays and for the six volume keys, after 0.4 seconds and then every 0.15 (the dev, 2026-10-17: "make it so you can hold left/right/page up/down/shift home/end in the main story for seaking and volume changes"). It is the game's own repeat in `app.py`, asked of the top screen through `Screen.repeats`, so Enter, the choice keys and every menu fire once however long they are held. Letting go of the key, or of Shift held with it, stops it, and a held skip stops when a choice comes.
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
- **Confirmed by the dev by ear on 2026-10-18** through `tests/interact/episode_check.py`, jumping to each prompt with F3 ("It's good now. Everything plays normally").
- **The engine's rule stays the original's:** the first automatic exit wins. In the exported data the transitions keep the file's order, so "first" is always the same one.

## The order of the choices

Found by the dev on 2026-10-17: "some of the episodes present the choices in the wrong order. Example, in the art show, when you are with agent delfy ... the secretive choice appears before bold. This is a bug for a lot of the episodes".

- **The original had no order of its own.** A state's ways out were kept in an unordered set, and `-[CCDecisionChooser addButtons]` (0x100047058) laid out the buttons in whatever order `-[CCState manualTransitions]` (0x100012448) gave from it. Neither sorts. It is the same unordered set behind the van escape bug, so the file's order, which the export keeps, is arbitrary.
- **The port offers them in the order the question says them.** Every question ends by saying its choices, such as "SECRETIVE or ATHLETIC." or Holiday Party's "take it, or leave it.", so `spoken_order` in `game/story.py` puts each choice where its words are last said, in any letter case. Delphi's briefing in Art Show (`008distractionGadgetPrompt`) now offers BOLD before SECRETIVE.
- **Counted 2026-10-18:** of the 114 states with two or three choices, 20 were reordered, among them six in Signum Cygni and four in Lazarus Awakens. The 4 where a choice's words are never said, plain YES or NO questions and Holiday Party's "Delphi's, or your own?", keep the stored order, which already matches how they are asked.
- Confirmed by the dev by ear on 2026-10-18: "Much better. All good here."
- It is done when the story is loaded, not in the exported data, so `states.json` and `analysis/script/` keep the file's order. `tests/case/story.py` checks every state whose question says its choices.

## The script

Each state's `script` is the text of what its recording says, in three kinds of line: `SPEECH` with a character's name, `PARENTHETICAL` for sounds such as "(GUNSHOT)", and `HEADING` for a scene, such as "CONSULATE - BOMB ROOM" (63 in all).

- **The screen reader does not read the dialogue,** since every line is voiced.
- **Scene headings are spoken only when the player presses H** (the dev, 2026-10-17: "Only when you press H"). An automatic heading would talk over the scene's first words. H says the latest heading reached.
- **The window shows the script as it plays**, headings included ([[foundation_plan]]).
- **The `#a,b#` marks only pace the on-screen text.** `-[CCScrollingTextView presentScript:]` (0x1000280a8) splits each line at `#` and each mark at `,` into reveal steps it calls ticks, which `tick` (0x100028d1c) steps through as the recording plays. The second number is how long to wait before the next piece appears (`insertTicks:toArray:`, 0x100028c80, pads empty steps for the wait), and the first says whether to clear the text so far first (`tickClears`). Speech drops them, and the window may use them or show each line whole.

## Achievements

The original reported achievements to Apple's Game Center. 23 states earn one, 16 achievements in all, since some can be reached by several routes. Their names and descriptions lived on Game Center's servers, not in the app.

- **The port keeps them as its own local list** (the dev, 2026-10-17: "I want local achievements since the game center thing is an apple thing, and it's online").
- **When one is earned,** the game says "Achievement earned" and its name at the next quiet moment: when a choice comes up or at the end of the episode, never over the story ([[foundation_plan]]'s speech rules).
- **The agent profile lists them,** which are earned and how many of the 16 ([[menus_plan]]).
- **They are saved with the progress and kept for good** ([[saves_plan]]).
- **The port writes their names**, since the originals are lost. The 16, approved by the dev on 2026-10-17 ("I like all of the names"), each after the original's own ID (the part after `net.reactivestudios.codenamecygnus.`) and the states that earn it:
  1. **Card Shark:** raise the bet in the Prologue's card game, IMPULSIVE, so Krasnoff folds. `event.m1e1_cardsWin`, at `achievement_cardsWin`.
  2. **Martini:** order the Martini at the hotel bar in Art Show, the FOCUSED choice. `event.m1e2_drink_1`, at `achievement_drinkMartini`.
  3. **Neptune's Lover:** go off with Serena or Seth, Neptune's lover, when they invite you in Neptune's Lair. `event.m1e3_sex_1`, at `achievement_seduceNeptunesLover`.
  4. **Trust Matthews:** speak Director Matthews' password, BE, into the bomb in Consulate, rather than MAELSTROM. `event.m1e4_chooseTrust_0`, at `achievement_trustMatthews`.
  5. **Lazarus' Card:** cut the green wire in Lazarus' test in Lazarus Awakens, and he gives you his card. `inventory.m1e5_lazarusCard_1`, at `achievement_lazarusCard`.
  6. **Unhappy Childhood:** tell Neptune your childhood was not happy, in Neptune's Gift. `trait.happyChildhood_0`, at `achievement_unhappyChildhood`.
  7. **Ladies' Agent:** tell Director Matthews, in Art Show, that you work your charm on ladies. `romance.m1_maleInterest_0`, at `achievement_romanceWomenMission1`.
  8. **Gentlemen's Agent:** tell Director Matthews, in Art Show, that you work your charm on gentlemen. `romance.m1_maleInterest_1`, at `achievement_romanceMenMission1`.
  9. **Alexander's Loyalist:** finish Signum Cygni having sided with Alexander more than with Director Matthews. Decided at the end by `trait.cygnusLoyalty`, which the episode's choices raise and lower. `trait.cygnusLoyalty_1`, at `achievement_alexanderLoyalist`.
  10. **Matthews' Loyalist:** finish Signum Cygni having sided with Director Matthews more than with Alexander, the same score above 0. `trait.cygnusLoyalty_0`, at `achievement_matthewsLoyalist`.
  11. **Rhodes' Ally:** win Agent Rhodes over to your side in Signum Cygni. `npc_favor.succeedRhodes`, at five states, `achievement_succeedRhodesAAA`, `AAB`, `AB`, `BBA` and `BBB`.
  12. **Rhodes' Rival:** turn Agent Rhodes against you in Signum Cygni, so that you end up fighting him. `npc_favor.failRhodes`, at four states, `achievement_failRhodesAB`, `BAA`, `BAB` and `BB`.
  13. **Mission Complete:** finish Signum Cygni, the last episode of Mission 1. `completion.1.7.1`, at `achievement_completeSignumCygni`.
  14. **The Prize:** find the prize ending of Holiday Party. `prize`, at `achievement_thePrize`.
  15. **Sneeze:** find the sneeze ending of Holiday Party. `sneeze`, at `achievement_sneeze`.
  16. **Stalemate:** find the stalemate ending of Holiday Party. `stalemate`, at `achievement_stalemate`.
- **The descriptions were made specific on 2026-10-17** (the dev: "Please change it to make it more clearer. Do that for the other achievements as well"), each checked against `analysis/script/`.

## Open questions

None.
