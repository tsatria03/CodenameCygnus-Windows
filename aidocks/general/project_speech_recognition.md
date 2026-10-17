---
name: project_speech_recognition
description: "The port keeps the original's spoken choices, behind a setting that turns speech recognition on or off; the keyboard always works. What the original did, and what is still to be decided in a plan."
metadata:
  node_type: memory
  type: project
---

**The port will let players speak their choices, as the original did, with a setting to turn speech recognition on or off.** The keyboard always works, whether it is on or off.

**Why:** The dev asked on 2026-10-17: "Are there settings to enable/disable speech recognition? If not, we need to add it when we build the actual port later."

**What the original did (read from the `Cygnus` binary's strings, 2026-10-17):**
- It listened with OpenEars (Pocketsphinx) and the English acoustic model in `game/AcousticModelEnglish.bundle`, building a small language model from the words of the current state's choices (`prepareForRecognitionOfState:`, `wordsInText`, `validateHypothesis:`).
- A voice button on the game screen turned recognition on and off (`voiceButtonClicked:`, `setSpeechRecognitionEnabled:`). Its labels were "Speech Recognition On" and "Speech Recognition Off". No saved settings key for it was found, so it may not have been remembered between runs; that is unconfirmed.
- Choices could also be tapped, as decision buttons (`decisionButtonWithTitle:`, `selectedTransition:withButton:`).
- Spoken messages included "Listening.", "No longer listening." and "Listen to the story unfold, then respond with your voice."
- It warned against two-way Bluetooth headsets, whose microphone profile degrades audio quality.

**Microphone reference:** the gitignored `user/` folder holds the dev's reference code for a microphone setting. It opens the default input through OpenAL Soft capture (the `cyal` package) and measures only the input level, never playing anything back. A Microphone row in Settings turns it on or off, defaulting to on. With no microphone, it speaks a notice once and the key still works. That is level detection, not word recognition, so the open, fallback and setting parts carry over, and the recogniser is new.

**How to apply:**
- Build it from a plan in `aidocks/plans/` first ([[feedback_record_plans_first]]). The plan settles:
  - the recogniser
  - how the microphone is opened
  - the setting's default, and where it is saved
  - what is spoken when listening starts and stops, and when no microphone is found
- The vocabulary is small and known in advance: each state's choice words, 98 distinct ones in v53, such as CHARISMATIC, HOSTILE and YES. A recogniser limited to those words suits it. Hidden choices (`render: false`) can still be spoken.
- Game audio must not be heard as speech. The original assumed headphones; desktop speakers can leak the story into the microphone.
- Never name the reference project in this repo's files ([[feedback_no_other_games]]).
- Tracked in [[project_dev_tasks]].
