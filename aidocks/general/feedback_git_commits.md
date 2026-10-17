---
name: feedback_git_commits
description: "One commit per fix. Commit without asking, but ask before every push. 'Commit' means commit only; 'commit/push' means both. Force pushes and history rewrites need an explicit go-ahead. Use git commit -F with a message file written by the Write tool, run git from PowerShell, and never hide git's errors."
metadata:
  node_type: memory
  type: feedback
---

**"Commit" means commit only; "commit/push" means commit and push.** Commits pile up locally by default, because the dev tests batches before pushing. A push waits for the dev to say "push" or "commit/push".

**Commit without asking; ask before pushing** (the dev, 2026-10-17: "For commits, you don't have to ask me if I want it done. You can always commit, but still ask if I want it pushed"). When a change is done, commit it straight away. Never push until the dev says "push" or "commit/push".

**Bring up pushing only from 10 unpushed commits** (the dev, 2026-10-17: "if it reaches grater than or equal to 10, you can count them", then "only push if it reaches grater than 10, like the commit count rule"). Below 10, commit quietly: no count and no question about pushing. At 10 or more, say how many are waiting and ask whether to push.

**Hold while the dev says so.** When the dev holds pushes, do not ask about pushing even past 10 commits; when the hold ends, report the count and ask. The dev can still ask for a push during a hold. The first hold lasted from 2026-10-17 until all eight plans were written the same day.

**Make multiple commits when possible** (the dev, 2026-10-17: "Make multiple commits when possible"). When the dev asks to commit a batch of work, split it into one commit per logical change rather than one large commit.

**`git add`, `git commit` and `git fetch` run without approval** (the dev, 2026-10-17: "make git commits without approval if you use the command. Same with git add/fetch"). They are allowed in `.claude/settings.local.json`.

**Fetching is fine without asking; bringing commits in is not.** Never pull, merge, rebase, cherry-pick or reset onto incoming commits without the dev's go-ahead.

**Rewriting published history needs an explicit go-ahead every time.** That covers force pushes, amending or rebasing pushed commits, and changing authors. When it is approved, push with `--force-with-lease`, and keep a backup until the dev is happy. The first was on 2026-10-17, when the dev asked for the mission recordings to be removed from history.

**Why:** These are the dev's standing rules, adopted for this project on 2026-10-17. The dev approves what goes into a commit, and history rewrites can lose work.

**How to apply:**
- Write the message to a file in the scratchpad with the Write tool, then run `git commit -F <file>` from PowerShell. Windows PowerShell 5.1 breaks double quotes inside `-m` arguments.
- Keep git commands plain: chain them with `;`, but pipe nothing after them. Never send git's error output to `$null`; a failed commit must be visible.
- **One commit per fix or change.** Each commit carries its own todo, changelog, docs and memory lines.
- **Mark the work finished before committing it**, so the finished line goes in the same commit as the work.
- Stage files by name when the commit should hold exactly what the dev approved. Check `git status` first.
- Format: a short summary line, a blank line, then a plain-text description wrapped at about 72 characters, ending with the Claude attribution line.
- The author is always tsatria03. This is a solo project, so there are no `Co-authored-by:` lines for people ([[project_solo]], [[feedback_use_github_usernames]]).
- Never commit the mission recordings or other large binaries; they stay in git history forever.
- After pushing, confirm with `git ls-remote origin refs/heads/main` and report the new commit.
- Committing isn't building or running; [[feedback_dont_run_or_build]] still applies.
