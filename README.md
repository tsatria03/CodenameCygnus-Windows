# CodenameCygnus-Windows

A Windows port, in Python, of **Codename Cygnus** (`net.reactivestudios.codenamecygnus`
1.3.2, Reactive Studios), an interactive radio drama for iPhone and iPad that is no longer
on the App Store. You are a secret agent of the Cygnus agency. Each episode is a fully
voiced spy story, and at every turn you choose what your agent does, such as CHARISMATIC
or HOSTILE, BOLD or SECRETIVE. Your choices shape your agent's personality and change how
the story goes.

The original was played by voice: you spoke your choice aloud, and the game listened. This
port is for the keyboard and for screen readers, so the whole game can be played without
sight. You can speak your choices too, behind a setting that turns speech recognition on
or off.

**Headphones are recommended.** The original says so itself, as it starts: "The acoustic
experience of Codename Cygnus is best with the use of a high quality headset."

## Status

**The port is being built, and every episode can be played from start to end.** Built so
far:

- speech through your screen reader, the keys (every one rebindable with F1), the settings
  and the three volumes;
- the original's audio: the voice, the background ambience and the decision loop, with
  the original's hard cut between scenes;
- the whole story, with its choices in the order the characters say them, Holiday Party's
  timed choices, and the van escape in Signum Cygni fixed;
- the menus around it: the opening, the main menu, the episode list, each episode's own
  screen, the end of an episode, previews and credits;
- saving: progress at every new part of the story, Continue, the episodes' locks, and the
  story carried from episode to episode;
- the agent profile, with the dominant trait and the four trait scales;
- 16 achievements of the game's own, kept on your computer;
- speaking your choices aloud, with speech recognition turned on, being tried by ear.

Still to come: the built game.

What was found in the original:

- The game is driven almost entirely by data, not code. Every episode is a graph of story
  states, each with its voice recording, background sound and on-screen script, joined by
  choices, automatic transitions and conditions.
- The newest version of the story, version 53, survives in the app's own database,
  `game/CodenameCygnus.sqlite`. The JSON files bundled with the app hold an older version 1.
- Version 53 is complete. Every one of the eight episodes of Mission 1 can be played from
  its start to its end, and every recording it names is on disk.

## The episodes

Mission 1 has eight episodes:

- **Prologue:** extract yourself from the Krasnoff Mission.
- **Art Show:** gain information on Neptune and the hostages.
- **Neptune's Lair:** infiltrate the Waterfront Towers to eavesdrop on Neptune.
- **Consulate:** stop TRIDENT to save the hostages.
- **Lazarus Awakens:** discover the origin of Lazarus.
- **Neptune's Gift:** learn more about Neptune's motivations.
- **Signum Cygni:** escape a perilous situation as a former threat resurfaces.
- **Holiday Party:** fondly recall last year's holiday party with Cygnus.

A new game starts with the Prologue and Holiday Party open, as in the original's final
data. Each of the other episodes opens when the one before it is finished. Holiday Party
is the only episode with timed choices: if you do not choose within seven seconds,
the story moves on without you.

Mission 2, "The Dutch Diamond", was announced but never released. Nothing of it exists in
the app.

## Requirements

The port needs 64-bit Python 3.12 or newer on Windows 10 or later, and four packages:

    pip install -r requirements.txt

- `pygame`: the window, the keyboard and the frame loop. It must be `pygame`, not
  `pygame-ce`, because the two cannot be installed side by side.
- `prismatoid`: Prism, which speaks through any screen reader other than NVDA, or through a
  Windows voice when none is running.
- `pocketsphinx`: speech recognition, limited at each choice to that choice's words. It
  is held at 5.0.4, the newest with a ready-made package for Windows; 5.1 needs a C
  compiler to install.
- `sounddevice`: the microphone, opened only while a choice is listened for.

`vendor/nvda/nvdaControllerClient64.dll` ships with the repository, so NVDA speaks through
its own client.

## Running it

From the repository's folder:

    python CodenameCygnus.py

It opens with a loading message, the first time with the original's headphones notice,
then the main menu, all spoken through your screen reader:

- **Continue**, while an episode is in progress, goes back to where you left off.
- **Episodes** lists the eight episodes and whether each is in progress, completed or
  locked. The Prologue and Holiday Party are open from the start, and each other episode
  opens when the one before it is finished. Enter on one opens its own screen: its
  description, then Start; Continue and Restart episode while in progress; or, once
  finished, what was said at its end, Replay episode and a preview of the next episode.
- **Agent profile** says your dominant trait, the furthest episode reached, the episodes
  completed, your four trait scales, each with which way it leans, and the achievements.
- **Settings** has the three volumes, a switch for speech recognition, the key bindings,
  and from source, Debug mode.
- **Credits** lists Reactive Studios' team.
- **Quit**, or Escape, closes the game.

Back is the first row of every menu. F1 opens the key bindings from anywhere.

During an episode:

- the arrows, Home and End move through the choices once they are read, and Enter or 1
  to 9 choose; C says them all again;
- R replays the recording, and Left and Right skip 5 seconds while the story plays;
- S skips on to the next choice across what you have heard before;
- H says the scene heading;
- V turns speech recognition on or off: with it on, "Listening." follows the first choice,
  and saying a choice chooses it, for 15 seconds, or a timed choice's whole seven;
- Shift with Home and End, Page Up and Page Down, and Shift with Page Up and Page Down set
  the master, background ambience and decision loop volumes;
- Escape or P pauses, with the pause menu: Resume, Restart episode, Settings and Return to
  menu.

Holding a skip or a volume key repeats it. At the end of an episode, a menu offers the next
episode, its preview and the episode's credits. Achievements are announced the first time
each is earned, at the next choice or at the end of the episode.

Everything the game keeps is in `%APPDATA%\CodenameCygnus`:

- `saves\progress.json`: each episode's progress, saved at every new state;
- `saves\heard.json`: every recording heard to its end, which S skips across;
- `saves\achievements.json`: the achievements earned;
- `config\settings.json` and `config\keys.json`: the settings and the key bindings;
- `logs\log.txt`, with the run before as `log.old.txt`, and `logs\crash.txt` when an error
  stops the game, which is spoken too.

The options:

- `--debug`: debug mode for this run. Running from source, the Settings screen's Debug mode
  row turns it on for good. During an episode, F2 then skips the recording without noting
  it as heard, F3 jumps to any state by typing or pasting part of its name, and F4 says the
  state, the trait scores and the story flags.
- `--episode ID`: start an episode straight away, from `1.1.1`, the Prologue, to `1.8.1`,
  Holiday Party, past the opening. Return to menu goes to the main menu.
- `--state NAME`: start at any story state, in debug mode, in the episode it belongs to.
  The names are the ones in `analysis\script`.
- `-v`: a more detailed log.
- `--exit-after SECONDS`: quit by itself.

## Tests

    python tests\suite.py

runs every test in `tests\case`, several at once, writing the results to `tests\results`.
Any one file runs on its own too, such as `python tests\case\keymap.py`. The tests never
speak, never play a sound, never open a window, and never touch your save.

`tests\interact` holds tools to hear the game by ear instead. `python
tests\interact\audio_check.py` plays a story state the way the game will, background,
voice and decision loop, from the Prologue's first scene or any state named after it; N
moves on to the next state. `python tests\interact\episode_check.py` lists the eight
episodes, every one open, and Enter plays one with the game's own keys; leaving it comes
back to the list. `python tests\interact\voice_check.py` listens for any question's
choices, or every choice word at once, and says what it heard, so speech recognition can
be judged before playing. Each keeps its own save, so none changes your volumes or keys.

## Layout

```
game/                    the original app bundle (see below)
vendor/nvda/             NVDA's controller client, with its license
CodenameCygnus.py        the entry script
codenamecygnus/          the port's Python package
docks/                   readme.txt, changelog.txt and todo list.txt, for players
aidocks/general/         the notes for AI-assisted work (see CLAUDE.md)
aidocks/plans/           every plan for a feature or fix, planned or finished
analysis/                notes and data read out of the original app
tools/                   the tools that read the original's data
tests/case/              the tests, one plain script each
tests/suite.py           runs them all
tests/interact/          tools to hear the game by ear, such as audio_check.py
requirements.txt         the four packages it needs
VERSION                  the version, as year, month, day and that day's number
```

### `game/`: the original's data

`game/` holds the original app bundle as the App Store shipped it, the `Cygnus` binary
included. The port never writes to it.

- `game/data/text/` holds the three descriptors the app shipped with:
  - `mission_descriptor.json`: the missions and episodes, their unlocking and their
    credits.
  - `resource_descriptor.json`: which recordings each episode needs.
  - `states_descriptor.json`: the story itself, in its older version 1.
- `game/CodenameCygnus.sqlite`, with its `-wal` and `-shm` files, is the app's database.
  It holds the newer version 53 of the story, version 18 of the missions and version 11 of
  the resources. The port never reads progress or saves from it: every player starts
  from scratch.
- `game/data/text/` also holds what the port reads: `missions.json`, `resources.json` and
  `states.json`, that final data exported as plain JSON by `tools/export_story.py`, which
  checks it first. The export fixes one bug in the original: in Signum Cygni's van escape,
  either ending could follow either choice.
- `game/data/audio/missions/m1/` holds Mission 1's recordings:
  - `episodes/e1/` to `e8/`: the 756 recordings of the episodes themselves, one folder per
    episode and part.
  - `sources/`: the 52 background ambiences and decision sounds.
  - `teasers/`: the six episode previews, `m1e2.mp3` to `m1e7.mp3`.
- `game/data/audio/others/menu/` holds the eight interface sounds the menus play.
- **Everything under `missions/` is left out of the repository**, being the original's
  voice acting, over 400 MB of it; even some of the ambiences carry voices. It belongs in
  those folders on your own machine. Only the interface sounds are in the repository.
- Every recording is MP3, converted from the original's AAC `.m4a` files so pygame can play
  them. The story data still names them `.m4a`; the port finds each one by the same name
  with `.mp3` in its place.
- `game/AcousticModelEnglish.bundle` is the speech recognition model the original used to
  hear spoken choices.

## Version numbers

A version is the date and that day's number: `26.10.14-1` is the first version of the 14th
of October 2026.

## Credits

**[tsatria03](https://github.com/tsatria03)** makes the port, on their own.

Codename Cygnus itself is Reactive Studios' game. Its writers, voice actors, composer and
team are credited in full, episode by episode, in `game/data/text/mission_descriptor.json`.

## Licence

The port's code is under the MIT License, in `LICENSE`. Everything under `game/` is
Reactive Studios' and is not covered by it.

The third-party pieces keep their own licenses. NVDA's controller client's sits beside its
DLL in `vendor/nvda/`, and can also be read online:

- the NVDA controller client, LGPL 2.1: <https://github.com/nvaccess/nvda/blob/master/extras/controllerClient/license.txt>
