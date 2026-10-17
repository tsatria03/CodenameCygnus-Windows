---
name: speech_recognition_plan
description: "Plan 7 of 8: speaking choices aloud, as in the original, behind an on/off setting: the recogniser, the microphone, what is spoken, and how long it listens. Status: planned, questions open."
metadata:
  node_type: memory
  type: project
---

**Status: planned, questions open.** Nothing is built.

Plan 7 of 8 ([[story_export_plan]] lists the order). What the original did, and the decision to keep it behind a setting, are in [[project_speech_recognition]].

## Decided

- **Choices can be spoken, behind a setting** that turns speech recognition on or off: a row in Settings, and V during an episode ([[story_engine_plan]], [[menus_plan]]). The keyboard always works, whether it is on or off.
- **It listens only while a choice waits,** after the question's recording has finished, as the decision loop plays ([[audio_plan]]).
- **It listens only for the current choices' words.** Each manual transition's `text` is a word or short phrase such as CHARISMATIC, TWO CARDS or HER DRINK, 98 distinct in all, and usually two or three at a time. Hidden choices (`render: false`) can be spoken too, as in the original.
- **A recognised word makes the same choice its key would,** said back by the screen reader first, such as "Charismatic."
- **Nothing is ever recorded or kept,** and nothing leaves the computer.

## Open questions

- The recogniser.
- How the microphone is opened.
- The setting's default.
- What is spoken when listening starts and stops, and when no microphone is found.
- How long it waits for the player to speak before it times out (the dev, 2026-10-17: "we need to discuss how long it should wait for the user to speak before timing out").
- Keeping the story audio out of the microphone, on speakers rather than headphones.
