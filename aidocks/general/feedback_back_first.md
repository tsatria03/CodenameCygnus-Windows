---
name: feedback_back_first
description: "Every menu with a way back has a Back row, always the first row and the one it opens on, before anything else, Settings and the volume levels included."
metadata:
  node_type: memory
  type: feedback
---

Every menu that can be left by going back has a **Back** row, and it is **always the first row**. Anything else that should come first, such as Settings' Debug mode, comes straight after it.

**Why:** the dev, 2026-10-18, after asking for a Back row at the top of the episode list ("There should also bee a back button in the episode list, at the top of the screen") and for Debug mode to be the first option in Settings: "The back button should always appear first in any menu, including settings."

**How to apply:**
- It holds for screens that are not built on `ui/menu.py` too: the F1 key bindings screen has Back as its first row and opens on it, Enter there going back as Escape does (the dev, 2026-10-18: "The keybind menu should also open on the back button").
- A new menu gets `Row('Back', self.back)` as its first row; `Menu.back` plays the back sound and closes it, as Escape does.
- The menu opens on Back too, never on another row, even where landing on the current choice would save a key press: a volume's levels open on Back, not on the level it is at (the dev, 2026-10-18: "I want it to open on the back button").
- Menus whose first row is already their way back keep it: the main menu (Quit), the pause menu (Resume), a yes-or-no question (No) and the headphones notice (Continue). See [[menus_plan]].
