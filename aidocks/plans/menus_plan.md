---
name: menus_plan
description: "Plan 5 of 8: the screens around the story: the opening, the main menu, the episode list, the agent profile with its traits and achievements, settings, credits, the end of an episode, the pause menu and the original's interface sounds. Status: planned, ready to build."
metadata:
  node_type: memory
  type: project
---

**Status: planned, ready to build.** Every question is answered; nothing is built.

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
  2. **Settings** opens the same Settings screen as the main menu's, so a volume or speech recognition can be changed without leaving the episode.
  3. **Restart episode** starts the episode again from its beginning, after asking to confirm, as the original did. What it does to the saved progress is for [[saves_plan]].
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
