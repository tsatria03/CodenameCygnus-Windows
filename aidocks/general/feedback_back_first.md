---
name: feedback_back_first
description: "Every menu with a way back has a Back row, and it is always the first row, before anything else, Settings included."
metadata:
  node_type: memory
  type: feedback
---

Every menu that can be left by going back has a **Back** row, and it is **always the first row**. Anything else that should come first, such as Settings' Debug mode, comes straight after it.

**Why:** the dev, 2026-10-18, after asking for a Back row at the top of the episode list ("There should also bee a back button in the episode list, at the top of the screen") and for Debug mode to be the first option in Settings: "The back button should always appear first in any menu, including settings."

**How to apply:**
- A new menu gets `Row('Back', self.back)` as its first row; `Menu.back` plays the back sound and closes it, as Escape does.
- A menu that opens on another row, such as a volume's levels on the level it is at, still lists Back first and starts its index past it.
- Menus whose first row is already their way back keep it: the main menu (Quit), the pause menu (Resume), a yes-or-no question (No) and the headphones notice (Continue). See [[menus_plan]].
