---
name: project_windows_only
description: "The port is strictly for Windows: no Linux or macOS builds, no GitHub Actions release workflow. The build and release scripts, when adapted, keep only the local Windows parts."
metadata:
  node_type: memory
  type: project
---

**The port is strictly for Windows.** There are no Linux or macOS runs, builds or releases.

**Why:** The dev decided on 2026-10-17: "This game will strictly for windows, therefore we'll need to modify the compiler/releaser later on to remove the github workflow parts."

**How to apply:**
- Write platform code for Windows only: `%APPDATA%` for the save, the NVDA client and Prism for speech. No per-system tables, Linux libraries or macOS bundles.
- When the build script (`compiler.py`) and release script (`releaser.py`) are brought in, leave out:
  - the GitHub Actions workflow (`.github/workflows/release.yml`)
  - the "Prepare and tag" and "Test the workflow" steps
  - the CI entry points
  - every Linux and macOS part
- Releases are then built, zipped and uploaded from the dev's own machine.
- That adaptation needs its own plan in `aidocks/plans/` first ([[feedback_record_plans_first]]). It is tracked in [[project_dev_tasks]].
