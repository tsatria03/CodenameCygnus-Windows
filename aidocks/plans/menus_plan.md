---
name: menus_plan
description: "Plan 5 of 8: the screens around the story: the opening, the main menu, the episode list, the agent profile with its traits and achievements, settings, credits, the end of an episode, the pause menu and the original's interface sounds. Status: being built in sections."
metadata:
  node_type: memory
  type: project
---

**Status: being built, in sections.** The dev said to go on on 2026-10-18 ("yes, then continue"). As with [[story_engine_plan]], each section is built and tested, the dev tries it by ear, and the next starts once the dev says it works.

## Built in sections

The parts that need saved progress wait for [[saves_plan]], which comes next: the Continue row, each episode's state (new, in progress, completed, locked), Restart in the episode list, and the agent profile's progress and traits. Until then every episode is open.

1. **The opening, the main menu, the episode list and Credits, with the interface sounds.** The opening's loading message and the headphones notice the first time; the main menu in place of the stand-in, for now Episodes, Settings, Credits and Quit; the episode list, each episode's own screen with its description and Start; Credits; and the original's sounds at the original's moments. Status: done, confirmed by the dev by ear on 2026-10-18 ("the menus work perfectly").
   - `codenamecygnus/game/menus.py` holds `Opening`, `HeadphonesNotice`, `MainMenu`, `EpisodeList`, `EpisodeMenu` and `CreditsScreen`; the stand-in main menu is gone.
   - **The opening** says "Codename Cygnus." and a loading message picked at random, waits 2.5 seconds so it is heard, or goes on at any key, then gives the headphones notice the first time (Continue, or Escape, sets `headphones_notice_shown`) or goes straight to the main menu. `--episode` and `--state` skip it, the main menu waiting silently under the episode.
   - **The main menu** says "Main menu." and offers Episodes, Settings, Credits and Quit; Escape quits.
   - **Episodes** says "Episodes. Mission 1." and lists Back, then "Episode 1, Prologue" to "Episode 8, Holiday Party". Back at the top was added on 2026-10-18 (the dev: "There should also bee a back button in the episode list, at the top of the screen"). Enter opens the episode's own screen, "Episode 2, Art Show.", with Back, the description as its own row, and Start (see section 3). Start puts the episode in that screen's place, so leaving the episode comes back to the list.
   - **Credits** says "Credits." and lists Back, then "Codename Cygnus is a game by Reactive Studios." as a row of its own (the dev, 2026-10-18: "Do the same with credits. Put the first part of that after the back button"; it was in the title before), then the company credits as rows, "CEO: Jonathon Myers", a credit with no title as a heading in plain case, and last "Windows port: tsatria03".
   - **The interface sounds** are played by purpose through `App.play_sound`, which `SOUNDS` in `app.py` maps to the files: Escape in any menu plays the back sound, `Menu.open` plays a screen's opening sound, Start plays `1930Radio A`, opening the pause menu `Sound A`, and Restart `1930Radio C`.
   - `tests/case/menus.py` has 11 tests.
2. **Settings:** the three volumes, speech recognition on or off, and the key bindings. Status: done, confirmed by the dev by ear on 2026-10-18 after the changes below ("There we go. All back buttons work").
   - **Back is the first row of every menu with a way back** (the dev, 2026-10-18: "The back button should always appear first in any menu, including settings"; [[feedback_back_first]]): Settings, the episode list, each episode's own screen (Back, then Start), Credits, a volume's levels, debug mode's list of matches, and the F1 key bindings screen (`ui/keybind_screen.py`), where Enter on Back goes back as Escape does and A, Delete and Backspace do nothing. Each opens on Back. The F1 screen opens by saying only "Key bindings." and then "Back"; how to use it is in `docks/readme.txt`'s Key bindings section, not said every time (the dev, 2026-10-18: "For the key bindings, remove the description, and put it in one of the document files ... the player facing one"). The main menu, the pause menu, the restart question and the headphones notice keep their own first rows, Quit, Resume, No and Continue.
   - `codenamecygnus/ui/settings_screen.py`: Back; "Debug mode, currently off", the first option, from source only; "Master volume, 100 percent", "Background ambience volume, 100 percent" and "Decision loop volume, 100 percent"; "Speech recognition, currently off"; and "Key bindings".
   - **Changed after the dev's first try, 2026-10-18:** Debug mode moved up from the bottom to be the first option, straight after Back ("The debug mode should be the first option in the screen"); and the ambience and decision volumes were renamed ("rename the following volume settings to this. Backround ambience volume, Decision loop volume") from "Ambience" and "Decision sound". The new names are the ones spoken everywhere: these rows, their levels, a volume key during an episode, and the F1 screen's actions, such as "Background ambience volume up".
   - **Enter on a volume** opens `VolumeLevels`, titled by the volume, "Background ambience volume.", listing Back and then 100 percent down to 0 percent in tens, so Down is quieter. It opens on Back (the dev, 2026-10-18: "I want it to open on the back button"), not on the level it is at as it first did; the Settings row has said the level already. The usual menu keys move through it (the dev, 2026-10-18: "With the volumes, you can click on it, and the normal menu keys will work, up/down/left/right/home/end"). Enter sets the level, comes back to Settings and says it, "Background ambience volume 10 percent"; Escape keeps the old level.
   - **Speech recognition** is switched and remembered now; [[speech_recognition_plan]] listens for it.
   - **Key bindings** opens the F1 screen, the timers held as F1 holds them.
   - The same screen opens from the main menu and the pause menu. `tests/case/screens.py` has 5 tests for it.
3. **The end of an episode and the previews:** "Episode complete!", then Next episode, Preview next episode, Credits and Return to menu, and Preview next in the episode list. Status: done, confirmed by the dev by ear on 2026-10-18 ("It works!"). Built the same day (the dev: "Yes, then start section 3.").
   - **Changed then:** each episode's own screen is titled by its name alone, "Episode 1, Prologue.", and its description is a row of its own between Back and Start, "Extract yourself from the Krasnoff Mission.", Enter on it saying it again (the dev: "Please put each episode's description before the start button, not crammed into the menu option"). It was in the title before, said with the name.
   - `codenamecygnus/game/episode_end.py` holds `EndMenu`, `PreviewScreen`, `CreditList` and `credit_lines`.
   - **At the end** the episode screen says "Episode complete!" and the completion text, then any achievements, then opens the end menu, whose first row, Back, is said behind them, never cutting them off. Coming back to it later says "Episode complete." and the row.
   - **The end menu** is Back; "Next episode, Art Show" where this episode opens one (`Story.next_episode`, the episode `locked_by` this one); "Preview next episode" where it has a preview; and Credits. Back stands in for the plan's "Return to menu", since Back is first in every menu and the two would be the same ([[feedback_back_first]]); it goes back to the menu the episode was started from. Signum Cygni and Holiday Party offer Back and Credits only.
   - **Next episode** starts that episode in this one's place with the variables this one ended with, so the traits and choices carry on, as [[saves_plan]] will keep between runs.
   - **A preview** says "Preview of Art Show." and plays the teaser's recording alone, the background stopped, coming back to the menu when it ends; Enter or Escape stops it, with the back sound, and Space pauses it. The teasers are 24 to 28 seconds.
   - **The episode's own screen** in the list also offers "Preview next episode", for every episode that has one; the original offered PREVIEW NEXT only once the episode was finished, which section 4 brings with the saves.
   - **The end credits** are the episode's own, "Credits. Prologue.", Back first, then a heading alone such as "Voice actors" and rows such as "Miss Honeybourne: Sarah Elmaleh".
   - Once complete, the episode is no longer paused when the end menu covers it, so the end state's background plays on under the menu.
   - **Found while checking the original for this section** (`-[CCEpisodeTableCell setupLeftButton]` and `setupRightButton`, 0x10002bc64 and 0x10002c020): an episode not started had only START; one in progress (state 0x10) RESTART on the left and CONTINUE on the right (`resumeEpisode`); one completed (0x20) REPLAY on the left (`replayEpisode`, a different routine from `restartEpisode`) and PREVIEW NEXT on the right. How Replay differs from Restart is for section 4.
   - `tests/case/episode.py` has 6 tests for it and `tests/case/menus.py` one.
4. **With saves:** Continue, the episodes' states and locks, Restart in the list, and the agent profile with its traits and achievements, built with or after [[saves_plan]]. Status: waiting.

Plan 5 of 8 ([[story_export_plan]] lists the order). Every screen is a spoken menu in the screen loop of [[foundation_plan]]: Up and Down move, Enter chooses, Home and End jump to the first and last row, Escape goes back, and each row is spoken by its text alone, never with its place such as "1 of 2" (the dev, 2026-10-17: "The menu position readouts should be disabled"). Moving wraps round past either end, and Left and Right move as Up and Down do (the dev, 2026-10-17: "please enable menu wrapping, and left/right arrow navigation"); during an episode Left and Right stay the 5-second skips ([[story_engine_plan]]).

## What the original had (read from `game/Cygnus`, 2026-10-17)

- **The opening:** a loading screen with joke messages ("Counting Stars...", "Reticulating Splines...", "Baking Bagels...", "Adjusting Mainframe..." and others), then, once only, a "Headphones Recommended" screen: "The acoustic experience of Codename Cygnus is best with the use of a high quality headset", with Continue. Whether it had been shown was saved (`kHeadphonesKey`).
- **The side menu,** in `-[CCSideMenuViewController reloadDatasource]` (0x100020618): Episodes, Store, Profile, Info.
- **The episode list:** each mission under "MISSION 1" with its description, and its episodes under "EPISODE" headings with their title, description and a button: START, CONTINUE, RESTART, PREVIEW NEXT, LOCKED or DOWNLOAD. A locked episode said "Episode Locked" and "You need to complete previous episode before starting this one."
- **The agent profile,** in `-[CCProfileDatasource createDatasource]` (0x100017d68), in this order:
  - Agent name, which could be changed ("Change agent name?")
  - Dominant trait
  - Furthest episode
  - Episodes completed
  - Game progress
  - the four trait scales: Openness, Predictability, Diplomacy and Activeness
- **The four traits** (`traitsFromProfile:accessible:`, 0x1000184d4), each a scale between two choice words, the low end first:
  - Openness: Secretive to Bold
  - Predictability: Impulsive to Focused
  - Diplomacy: Hostile to Charismatic
  - Activeness: Clever to Athletic
- **During an episode,** Escape's equivalent asked "Are you sure you want to stop this episode?" with Return To Menu, and a restart warned "If you restart this episode, all saved progress beyond this episode will be erased."
- **At the end of an episode:** "Episode Complete!", the episode's completion text, its credits, and PREVIEW NEXT.
- **Info:** support by email, technical information (build, device, system version) and the credits, Reactive Studios' company credits among them.
- **Store and Downloads** sold and downloaded episodes. The port has every episode on disk and free, so both go.

## Decided

- **Store and Downloads are left out**, along with everything online: Facebook sharing, the support email, Game Center and the analytics.
- **The main menu has six rows** (the dev, 2026-10-17: "I like it"), the original's side menu without its online parts:
  1. **Continue,** only while an episode is in progress, naming it, such as "Continue Art Show". Enter picks up where the player left off ([[saves_plan]]). It comes first, so one Enter after starting gets back into the story.
  2. **Episodes:** Mission 1's episodes in order, each read with its number, title and state, such as "Episode 2, Art Show, locked". An open episode offers Start, or Restart once finished, and "Preview next", the teaser of the following episode. A locked one says "You need to complete the previous episode before starting this one", as the original did. Escape goes back.
  3. **Agent profile:** the original's Profile screen without its agent name, so the dominant trait, furthest episode, episodes completed, game progress and the four trait scales, plus the achievements, each earned or not with its description ([[story_engine_plan]]).
  4. **Settings:** speech recognition on or off, the three volumes, the Debug mode row when running from source ([[foundation_plan]]), and the key bindings screen, F1 from anywhere.
  5. **Credits:** Reactive Studios' company credits, as on the original's Info screen, and a line for the port. Each episode's own credits play at the end of that episode, as in the original.
  6. **Quit** closes the game, as Escape on the main menu does.

- **The opening follows the original, kept short** (the dev, 2026-10-17: "I agree"):
  1. As the game starts, the screen reader says "Codename Cygnus" and one of the original's eight loading messages, picked at random, while the game loads: "Counting Stars...", "Reticulating Splines...", "Almost There...", "Folding Papers...", "Adjusting Mainframe...", "Baking Bagels...", "Measuring Squares..." or "Calculating Distance..." (all from `en.lproj/Localizable.strings`).
  2. The first time only, the headphones notice: "Headphones recommended. The acoustic experience of Codename Cygnus is best with the use of a high quality headset." Enter continues, and the game remembers it has been shown, as the original's `kHeadphonesKey` did ([[saves_plan]]).
  3. Then the main menu.

- **No agent name** (the dev, 2026-10-17: "What's the point of customizing the name? I recommend keeping it as agent"). The original's name belonged to the player's online account, checked by its server ("Please try again with different name"), and the story never uses it: the recordings always say "Agent". So the profile has no name row, and the player is simply "Agent".

- **Traits and the dominant trait, read from the original** (the `Extensions` category's `dominantTrait`, 0x1000337cc, and `dominantValue`, 0x100033c0c, and `traitsFromProfile:accessible:`):
  - Each trait is one number in the save's variables (`Openness`, `Predictability`, `Diplomacy`, `Activeness`). A choice word at one end raises it, its opposite lowers it.
  - The dominant trait is the one furthest from 0 either way. Above 0 it is named by the high end (Bold, Focused, Charismatic, Athletic), below 0 by the low end (Secretive, Impulsive, Hostile, Clever). With every trait at 0 it was "none".
  - On a tie it kept whichever it met first in an unordered dictionary, so ties came out arbitrarily.
  - The scales were sliders placed relative to the dominant trait's strength, and their VoiceOver text was only the trait and its number, such as "Openness: 2", which does not say which way it leans.
- **The port speaks them clearly** (the dev, 2026-10-17: "I like what you recommend. I want it announced clearly"):
  - "Dominant trait: Charismatic." Before any choice moves a trait, "Dominant trait: none yet."
  - A tie goes to the first in the original's own order, Openness, Predictability, Diplomacy, Activeness, so it is the same every time.
  - Each scale says which way it leans and how far, such as "Diplomacy: Charismatic, 3" or "Openness: Secretive, 2". At 0, "Activeness: balanced".

- **The end of an episode** (the dev, 2026-10-17: "agreed"):
  1. When the story reaches the episode's end state, the screen reader says "Episode complete!" and then the episode's completion text, as an important message that only a pressed key cuts off ([[foundation_plan]]).
  2. Then any achievements earned during it, such as "Achievement earned: Card Shark."
  3. Then a short menu:
     - **Next episode** starts the episode this one unlocked, when there is one.
     - **Preview next episode** plays its teaser, as the original's PREVIEW NEXT did.
     - **Credits:** this episode's credits, one row each, such as "Miss Honeybourne: Sarah Elmaleh".
     - **Return to menu.**
  - A row with nothing behind it is left out. Signum Cygni and Holiday Party have no next episode and no preview, and Mission 2 was never released.

- **The pause menu** (the dev, 2026-10-17: "agreed"). Escape during an episode pauses every layer of the story ([[audio_plan]]) and opens:
  1. **Resume** carries on exactly where the story paused; Escape does the same.
  2. **Restart episode** starts the episode again from its beginning, after asking to confirm, as the original did. What it does to the saved progress is for [[saves_plan]]. It comes straight after Resume (the dev, 2026-10-17: "a restart button after resume"), and is built with [[story_engine_plan]]'s section 2.
  3. **Settings** opens the same Settings screen as the main menu's, so a volume or speech recognition can be changed without leaving the episode.
  4. **Return to menu** saves the player's place and goes to the main menu, where Continue comes back to it. Since nothing is lost, it does not ask "Are you sure you want to stop this episode?" as the original did.

- **The menus play the original's interface sounds at the original's moments** (the dev, 2026-10-17: "I agree"). They are in `game/data/audio/others/menu/`. The original played them from `CCStyleManager`'s class methods (0x100008e48 to 0x100008f20), found by searching the code for their names:
  - `1930Radio A`: `playPlaySound`, `playBackButton` and `playMissionsVCSound`. In the port: starting or continuing an episode, going back with Escape, and opening Episodes.
  - `1930Radio B`: `playProfileVCSound`. In the port: opening the Agent profile.
  - `1930Radio C`: `playRestartSound` and `playInfoVCSound`. In the port: restarting an episode, and opening Credits, which stands in for the Info screen.
  - `PushButton D`: `playSkipButton`. In the port: skipping with S.
  - `Sound A`: `playViewControllerSound`. In the port: opening any other screen, such as Settings or the pause menu.
  - Not used: `1930Radio D` (`playStoreVCSound`) and `Buy` (`playBuySound`) belonged to the Store, and nothing in the code plays `00000Push`.
  - Moving between rows plays nothing, as in the original, so no sound overlaps the screen reader. The sounds follow the master volume ([[audio_plan]]).

- **The episode list** (the dev, 2026-10-17: "I think it should be like the original where you have to click on the episode to find the description of it"):
  - The screen opens on "Episodes. Mission 1." The original's mission description ("Five premium episodes, 15-25 minutes each...") is left out, since it predates Holiday Party and was written for selling episodes. Mission 2, never released, is left out.
  - Each row is the episode's number, title and state only: "Episode 2, Art Show, in progress." The states are new, in progress, completed and locked.
  - Enter on an episode opens its own screen, which says its description first and then offers its buttons: Start, or Continue while in progress; Restart once it has been started before; and Preview next episode once it is finished and there is a next one.
  - Enter on a locked episode says its description and then "Locked. You need to complete the previous episode before starting this one."
  - While Mission 1's recordings are not downloaded yet, an open episode's screen offers "Download Mission 1, about 470 megabytes" in place of Start ([[build_release_plan]]).

## Open questions

None. Ready to build once the dev says so.
