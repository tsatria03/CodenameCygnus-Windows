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
  3. **Agent profile:** the original's Profile screen, the agent's name, the dominant trait, furthest episode, episodes completed, game progress and the four trait scales, plus the achievements, each earned or not with its description ([[story_engine_plan]]).
  4. **Settings:** speech recognition on or off, the three volumes, the Debug mode row when running from source ([[foundation_plan]]), and the key bindings screen, F1 from anywhere.
  5. **Credits:** Reactive Studios' company credits, as on the original's Info screen, and a line for the port. Each episode's own credits play at the end of that episode, as in the original.
  6. **Quit** closes the game, as Escape on the main menu does.

- **The opening follows the original, kept short** (the dev, 2026-10-17: "I agree"):
  1. As the game starts, the screen reader says "Codename Cygnus" and one of the original's eight loading messages, picked at random, while the game loads: "Counting Stars...", "Reticulating Splines...", "Almost There...", "Folding Papers...", "Adjusting Mainframe...", "Baking Bagels...", "Measuring Squares..." or "Calculating Distance..." (all from `en.lproj/Localizable.strings`).
  2. The first time only, the headphones notice: "Headphones recommended. The acoustic experience of Codename Cygnus is best with the use of a high quality headset." Enter continues, and the game remembers it has been shown, as the original's `kHeadphonesKey` did ([[saves_plan]]).
  3. Then the main menu.

## Open questions

- The episode list's exact rows and wording.
- The agent name: whether players set one, and what it is for.
- How the trait scales and the dominant trait are spoken.
- The end-of-episode screen and the preview.
- The pause menu's rows.
- Whether the menus use the original's interface sounds in `other/misc/`.
