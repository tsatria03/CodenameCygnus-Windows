---
name: speech_recognition_plan
description: "Plan 7 of 8: speaking choices aloud, as in the original, behind an on/off setting: PocketSphinx limited to the current choice's words, the microphone through sounddevice, off by default, 15 seconds of listening, and what is spoken. Status: finished."
metadata:
  node_type: memory
  type: project
---

**Status: finished,** confirmed by the dev by ear on 2026-10-18, in the speech check ("All voice tests past.") and in the game ("It also works for the actual game as well, not just in the outside tests."). Started the same day (the dev: "Yes please. Then make an interactive voice test for it."); the speech check was made to stop listening at the first choice heard, as the game does.

## How it is built

- **`codenamecygnus/platform/listener.py`** holds it all, apart from the episode screen:
  - `Recogniser`: a PocketSphinx decoder with the English model and no language model, and its endpointer, which finds where speech starts and stops in the microphone's 30 ms blocks. At every choice it is given a JSGF grammar of the choice's phrases, hidden ones too, so it can only ever hear those.
  - **Speech that is no choice:** a grammar always picks one of its phrases, even for a cough, so the grammar also holds other words for it to pick instead: every other choice word in the story and a few short ones such as "the", "um" and "okay", leaving out any word of the current choices. Hearing one of those is "Sorry, I did not catch that".
  - Words are lowercased and lose their apostrophes. The dictionary knows every choice word but "Delphi's", which is added as "delphis", Delphi with a Z.
  - `Listener`: opens the default microphone through sounddevice only while listening, 16 kHz, 16-bit, one channel, and closes it as soon as listening stops. The blocks wait in a queue and are decoded once a frame on the main thread, so nothing in the game is touched from another thread. Nothing is written anywhere.
  - Before opening, it reads Windows' microphone privacy setting from the registry (`CapabilityAccessManager\ConsentStore\microphone`, the machine's, the user's and the desktop apps' `NonPackaged`); any of them set to Deny is "blocked". No input device, or one that will not open, is "no microphone".
  - The recogniser is loaded at the first listen, about a third of a second.
- **The episode screen** listens after offering a choice: the first choice, then "Listening.", for 15 seconds, or for the rest of a timed choice's clock. The 15 seconds are a run-loop timer, so F1 holds them as it holds a timed choice. Pausing stops listening and keeps the seconds left; resuming listens for the rest without saying "Listening." again. A choice, R, the end or leaving stops it.
  - C says the choices, then listens for 15 seconds more. V says "Speech recognition on." or "off.", and turned on at a waiting choice it starts listening. **While it is listening, V does nothing but say "Listening."**, as the original disabled its voice button while it listened: `-[CCGameViewController voiceRecognitionChangedStateToActive:]` (0x100042174) calls the control view's `setVoiceEnabled:` (0x100016ab8) with the opposite of listening (the dev, 2026-10-18: "The V key should not disable listening if the speech rec was on ... Match it to the original"). Once listening ends, after 15 seconds, V turns it off again. The original never disabled the choice buttons for speech, only after a choice was made (`selectedTransition:withButton:`, 0x100047a40).
  - **While it is listening, a choice can only be spoken,** the port's own rule, not the original's (the dev, 2026-10-18: "When it's listening, you should not be allowed to tap your choices or pick from them. I feel like that's sort of cheating", then "Yes please" to the details): Enter and 1 to 9 say "Speak your choice." and choose nothing. The arrows, Home and End still read the choices, C reads them all and listens again, and Escape and P pause. Once listening ends, after its 15 seconds, the keys choose again. Holiday Party's timed choices listen for their whole clock, so with speech recognition on they can only be spoken, and a word not caught lets the clock run out. Turning it on in Settings from the pause menu listens once the story resumes.
  - The microphone's trouble is said once a session, and listening stops at that choice; C tries again.
- **`tests/interact/SPEECH_check.py`**, the dev's voice test (the dev, 2026-10-18: "make an interactive voice test for it"), described in its own docstring: choose a question from the story, or every choice word at once, and it listens and says what it heard, stopping at the first choice heard as the game does (the dev, 2026-10-18: "as soon as it heres the correct word, it should stop listening"), with what the recogniser picked when it was no choice, so its reliability can be judged by ear before playing.
- **Tests:** `tests/case/listening.py` checks the episode screen with a stand-in listener, and the recogniser's grammar for every choice in the story, with no microphone.

Plan 7 of 8 ([[story_export_plan]] lists the order). What the original did, and the decision to keep it behind a setting, are in [[project_speech_recognition]].

## Decided

- **Choices can be spoken, behind a setting** that turns speech recognition on or off: a row in Settings, and V during an episode ([[story_engine_plan]], [[menus_plan]]). The keyboard always works, whether it is on or off.
- **It listens only while a choice waits,** after the question's recording has finished, as the decision loop plays ([[audio_plan]]).
- **It listens only for the current choices' words.** Each manual transition's `text` is a word or short phrase such as CHARISMATIC, TWO CARDS or HER DRINK, 98 distinct in all, and usually two or three at a time. Hidden choices (`render: false`) can be spoken too, as in the original.
- **A recognised word makes the same choice its key would,** said back by the screen reader first, such as "Charismatic.", with the choice sound, `PushButton D`. A choice made by key is not said back; a spoken one is, so the player knows which word was heard.
- **Nothing is ever recorded or kept,** and nothing leaves the computer.
- **The recogniser is PocketSphinx** (the dev, 2026-10-17: "I don't want open dictation, so I think the first one will do"), the `pocketsphinx` package from pip, with the English model it ships. It is the same family as the original's OpenEars, works offline and adds no large download. Each time a choice waits, it is limited to that choice's words, never open dictation. If testing finds it too unreliable, only the recogniser would change (Vosk being the fallback), not the rest of the game. It is in `requirements.txt` as `pocketsphinx~=5.0.4` (installed 2026-10-18): 5.1.1, the newest, ships only as source and needs a C compiler on Windows, while 5.0.4 has a ready-made wheel for Python 3.12 on 64-bit Windows, with the English model inside it.

- **It listens for 15 seconds a time** (the dev, 2026-10-17: "I like the 15 seconds"), using the original's own words for starting and stopping:
  - When a choice comes up, the screen reader says the first choice, the one you are on ([[story_engine_plan]]), then "Listening."
  - After 15 seconds with nothing recognised, it says "No longer listening." The choice stays open, the decision loop keeps playing, and the keys still choose.
  - C reads the choices again and listens for another 15 seconds.
  - Speech heard but matching no choice gets "Sorry, I did not catch that", and listening carries on for the rest of the 15 seconds.
  - Holiday Party's timed choices listen for their whole 7 seconds.

- **It starts off** (the dev, 2026-10-17: "I want it off by default"). The keyboard and screen reader are the port's main way to play; opening a microphone on a PC can bring up Windows' privacy prompt the first time, and on speakers the story itself could be heard as speech. A player turns it on with V or in Settings, and the game remembers it ([[saves_plan]]).

- **The microphone is opened through the `sounddevice` package,** the default input device, read in small blocks fed straight to PocketSphinx. It is the usual way to feed PocketSphinx a microphone in Python, it is reliable on Windows, and it never touches pygame's sound output. No OpenAL ([[project_python_only]]). It is in `requirements.txt` as `sounddevice>=0.5.6` (installed 2026-10-18).
- **No microphone** (the dev, 2026-10-17: "Yes"):
  - With speech recognition on and no microphone that opens, the screen reader says once a session: "No microphone found. Choose with the keys."
  - If Windows' privacy settings block the microphone, it says "The microphone is blocked in Windows privacy settings." instead.
  - The setting stays on, so a microphone plugged in later is used at the next choice.
- **Keeping the story out of the microphone:** listening only starts once the question's recording has finished, so only the background and the decision loop play while it listens, and those carry little speech. The headphones notice at the first start already recommends headphones ([[menus_plan]]). Anything more is for testing by ear.

## Open questions

None.
