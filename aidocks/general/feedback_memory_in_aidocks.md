---
name: feedback_memory_in_aidocks
description: "All memory for this project lives in the repo's aidocks/ folder: plans in aidocks/plans/, every other note in aidocks/general/, indexed by aidocks/general/MEMORY.md. Never write project memory to the ~/.claude store."
metadata:
  node_type: memory
  type: feedback
---

Write every memory for this project into `aidocks/` at the repo root:
- a plan goes in `aidocks/plans/<name>_plan.md`, with no `project_` prefix
- every other note goes in `aidocks/general/<name>.md`
- `aidocks/general/MEMORY.md` is the index; add a one-line pointer there for every new note

**Why:** The dev asked for this on 2026-10-17 ("use the aidocks folder for all future memmories for this project"), so memory travels with the repo.

**How to apply:**
- Name notes `feedback_<slug>.md`, `project_<slug>.md` or `user_<slug>.md`, with `name:` matching the file name.
- Use frontmatter with `name`, a quoted `description`, and `metadata: {node_type: memory, type: ...}`.
- For feedback and project notes, follow the fact with **Why:** and **How to apply:** lines.
- A `[[name]]` link resolves to whichever of the two folders holds that note.
- `CLAUDE.md` at the repo root is a lean dispatcher, under 40,000 characters. It orients, then points at notes with `[[name]]` links. When a section of it grows past a few lines of real detail, move that into a note and leave a pointer.
- The `~/.claude` memory store keeps only a pointer to this folder, nothing else.
- `CLAUDE.md` and `aidocks/` are committed, not gitignored.
