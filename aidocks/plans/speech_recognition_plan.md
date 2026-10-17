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
- **The recogniser is PocketSphinx** (the dev, 2026-10-17: "I don't want open dictation, so I think the first one will do"), the `pocketsphinx` package from pip, with the English model it ships. It is the same family as the original's OpenEars, works offline and adds no large download. Each time a choice waits, it is limited to that choice's words, never open dictation. If testing finds it too unreliable, only the recogniser would change (Vosk being the fallback), not the rest of the game. The package joins `requirements.txt` when this is built.

- **It listens for 15 seconds a time** (the dev, 2026-10-17: "I like the 15 seconds"), using the original's own words for starting and stopping:
  - When a choice comes up, the screen reader reads the choices, then says "Listening."
  - After 15 seconds with nothing recognised, it says "No longer listening." The choice stays open, the decision loop keeps playing, and the keys still choose.
  - C reads the choices again and listens for another 15 seconds.
  - Speech heard but matching no choice gets "Sorry, I did not catch that", and listening carries on for the rest of the 15 seconds.
  - Holiday Party's timed choices listen for their whole 7 seconds.

## Open questions

- How the microphone is opened.
- The setting's default.
- What is spoken when no microphone is found.
- Keeping the story audio out of the microphone, on speakers rather than headphones.
