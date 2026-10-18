# CodenameCygnus-Windows

A Windows port, in Python, of **Codename Cygnus** (`net.reactivestudios.codenamecygnus`
1.3.2, Reactive Studios), an interactive radio drama for iPhone and iPad that is no longer
on the App Store. You are a secret agent of the Cygnus agency. Each episode is a fully
voiced spy story, and at every turn you choose what your agent does, such as CHARISMATIC
or HOSTILE, BOLD or SECRETIVE. Your choices shape your agent's personality and change how
the story goes.

The original was played by voice: you spoke your choice aloud, and the game listened. This
port is being built for the keyboard and for screen readers, so the whole game can be
played without sight. Speaking your choices will stay possible too, behind a setting that
turns speech recognition on or off.

**Headphones are recommended.** The original says so itself, as it starts: "The acoustic
experience of Codename Cygnus is best with the use of a high quality headset."

## Status

**The port is being built.** The original app has been studied and its story data
recovered and checked. Speech, the keys, the settings and the sound are built, and an
episode can be played from start to end with `--episode`. The menus, saving, achievements
and speech recognition are still to come.

What has been found so far:

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

The port will need 64-bit Python 3.12 or newer on Windows 10 or later, and two packages:

    pip install -r requirements.txt

- `pygame`: the window, the keyboard and the frame loop. It must be `pygame`, not
  `pygame-ce`, because the two cannot be installed side by side.
- `prismatoid`: Prism, which speaks through any screen reader other than NVDA, or through a
  Windows voice when none is running.

`vendor/nvda/nvdaControllerClient64.dll` ships with the repository, so NVDA speaks through
its own client.

## Running it

From the repository's folder:

    python CodenameCygnus.py

For now it opens on a stand-in main menu, Settings and Quit, which speaks through your
screen reader. Until the real menus come, an episode is started from the command line,
such as `python CodenameCygnus.py --episode 1.1.1` for the Prologue, or chosen from a
list with `tests\interact\episode_check.py` (see Tests). F1 opens the key bindings from
anywhere.

During an episode, the arrows, Home and End move through the choices once they are read,
Enter or 1 to 9 choose, C says them again, Space pauses, R replays the recording, Left and
Right skip 5 seconds while the story plays, H says the scene heading, and Escape opens the
pause menu, where the episode can be restarted. Holding a skip or a volume key repeats it.

- `--debug`: debug mode for this run. Running from source, the Settings screen's Debug mode
  row turns it on for good.
- `--episode ID`: start an episode straight away, from `1.1.1`, the Prologue, to `1.8.1`,
  Holiday Party. Return to menu goes to the main menu.
- `--state NAME`: start at any story state, in debug mode. It waits for debug mode in the
  story engine.
- `-v`: a more detailed log.
- `--exit-after SECONDS`: quit by itself.

Every run writes `logs\log.txt` in `%APPDATA%\CodenameCygnus`, keeping the run before as
`log.old.txt`. An error that stops the game writes `logs\crash.txt` and is spoken.

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
back to the list. Each keeps its own save, so neither changes your volumes or keys.

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
requirements.txt         the two packages it needs
VERSION                  the version, as year, month, day and that day's number
```

### `game/`: the original's data

`game/` holds the original app bundle as the App Store shipped it, the `Cygnus` binary
included. The port will never write to it.

- `game/data/text/` holds the three descriptors the app shipped with:
  - `mission_descriptor.json`: the missions and episodes, their unlocking and their
    credits.
  - `resource_descriptor.json`: which recordings each episode needs.
  - `states_descriptor.json`: the story itself, in its older version 1.
- `game/CodenameCygnus.sqlite`, with its `-wal` and `-shm` files, is the app's database.
  It holds the newer version 53 of the story, version 18 of the missions and version 11 of
  the resources. The port will never read progress or saves from it: every player starts
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
  them. The story data still names them `.m4a`; the port will find each one by the same name
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
