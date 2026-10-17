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

## Open questions

- The main menu's rows.
- The opening: the loading messages, and the headphones screen.
- The agent name: whether players set one, and what it is for.
- How the trait scales and the dominant trait are spoken.
- The end-of-episode screen and the preview.
- The pause menu's rows.
- Whether the menus use the original's interface sounds in `other/misc/`.
