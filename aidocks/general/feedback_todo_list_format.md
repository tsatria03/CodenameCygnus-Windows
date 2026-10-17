---
name: feedback_todo_list_format
description: "docks/todo list.txt: ##Unfinished. then ##Finished. headings, one plain sentence per line stating the bug itself (never \"Fix a bug where\"), new items at the top, each as short as the rest, LF endings, no markdown or numbers. Players only."
metadata:
  node_type: memory
  type: feedback
---

`docks/todo list.txt`, with a space in the name, is the dev's task list. **It holds only what a player notices**, because it ships beside the game. Developer tasks (the repository, tools, tests, build and docs) go in a `project_dev_tasks` note in `aidocks/general/` instead.

**Its format:**
- `##Unfinished.` on the first line, a blank line, then one item per line.
- A blank line, then `##Finished.`, a blank line, and its items below.
- **Every heading is followed by one blank line, and a new item goes after that blank line**, at the top of the items. Never put an item straight under the heading.
- Each item is a plain sentence or two. **A bug is stated as what happens**, with no "Fix a bug where" in front.
- An enhancement or task starts with what to do: "Add ...", "Make ...", "Remove ...".
- A finished item says what is now true, newest first. A reworded line goes back to the top.
- No numbering, no bullets, no markdown, no file:line references. Avoid contractions.
- **LF** line endings with no BOM. Keep every line well under 1024 characters.

**Why:** The dev's standing rules, adopted for this project on 2026-10-17. They read it by screen reader, so plain sentences read cleanly and markdown symbols would be spoken aloud.

**How to apply:**
- A player-facing finding that is reported and not fixed in the same change goes into `##Unfinished.` as soon as it is reported.
- A bug found and fixed in the same change goes straight into `##Finished.`.
- Move an item to `##Finished.` only when the dev confirms it is done.
- Keep each item as short as the others. The technical detail lives in a plan or memory note.
- After editing, check the line endings with a byte check.
