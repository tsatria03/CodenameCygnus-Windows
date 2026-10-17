---
name: feedback_changelog
description: "Whenever a change players will notice lands, add a plain sentence at the top of the unrelease: block in docks/changelog.txt, in the same commit; entries read newest first. LF, no BOM, one sentence per line, no markdown."
metadata:
  node_type: memory
  type: feedback
---

**Keep `docks/changelog.txt` up to date as game changes land.** Every commit that fixes a bug or adds an enhancement a player will notice also adds a line under `unrelease:` at the top of the file.

**Why:** The dev's standing rules, adopted for this project on 2026-10-17. The changelog ships beside the game, so players read it by screen reader.

**How to apply:**
- **Format:**
  - A heading is one word ending in a colon, on a line of its own: `unrelease:`, or a version like `26.10.17-1:`.
  - Every other line is an entry: one plain sentence or two, with no bullets, numbers or markdown.
  - A blank line separates one heading's block from the next.
- **LF, no BOM.** Match the endings the file has when you edit it, and check afterwards.
- **New lines go at the top of the `unrelease:` block**, so the block reads newest first. A reworded line goes back to the top too. If there is no `unrelease:` heading, add it at the very top.
- **Only what a player notices:** fixes, enhancements, removed features. Leave out notes, docs, tests, refactors and build internals, and anything only developers see.
- **Wording:** write for a player, say what is now true, and avoid contractions.
- **No credit lines.** Entries say what changed, not who changed it.
- **Released entries stay as they are.** Never edit an entry that already has a version heading.
- **Release size:** a release aims for 50 to 100 entries. It never holds more than 100, and fewer than 5 does not make a release unless the dev overrides it. A heading is never counted as an entry; count the lines from the file each time. Say so when the block nears 100.
