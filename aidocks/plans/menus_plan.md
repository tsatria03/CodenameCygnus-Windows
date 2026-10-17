---
name: menus_plan
description: "Plan 5 of 8: the screens around the story: the opening, the main menu, the episode list, the agent profile with its traits and achievements, settings, credits and the end of an episode. Status: planned, questions open."
metadata:
  node_type: memory
  type: project
---

**Status: planned, questions open.** Nothing is built.

Plan 5 of 8 ([[story_export_plan]] lists the order). Every screen is a spoken menu in the screen loop of [[foundation_plan]]: Up and Down move, Enter chooses, Home and End jump to the first and last row, Escape goes back, and each row is spoken with its place.

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

## Open questions

- The episode list's exact rows and wording.
- The pause menu's rows.
- Whether the menus use the original's interface sounds in `other/misc/`.
