# tools

Scripts for reading the original app. None of them is part of the game, and none ever writes to `game/`.

- `macho64.py`: reads the arm64 slice of `game/Cygnus`, the original's binary. It lists the segments and sections, the Objective-C classes and their methods, the selector references and the imported functions. Standard library only. Run it on its own to print the slice's layout and whether its code is encrypted; it is not (`cryptid` 0).
- `dis64.py`: disassembles methods from that slice, naming the selectors, imported functions, classes and strings each instruction refers to. It needs `capstone` (`pip install capstone`), which the game itself does not.

- `cygnus_db.py`: reads the original's final data out of `game/CodenameCygnus.sqlite`: the story (version 53) and the episodes (version 18). It always works on a temporary copy, since opening the database in place could change it. Standard library only. Run it on its own for a summary.
- `export_story.py`: exports the original's final data as the JSON the game reads, `missions.json`, `resources.json` and `states.json` in `game/data/text/`. It fixes the van escape bug in Signum Cygni, then checks that every episode reaches its end, every link leads to a real state, every condition can be read, no state has two automatic exits, and every recording has its MP3 under `game/data/audio/`. It writes nothing if a check fails. `--check` checks without writing. Standard library only. Run it on the dev's machine, where the mission recordings are.
- `script_text.py`: writes the whole story as plain text into `analysis/script/`, one file per episode, every state with its lines and where each choice leads. Standard library only.

Examples, from the repo root:

    python tools/macho64.py
    python tools/dis64.py --list CCSoundManager
    python tools/dis64.py CCSoundManager playBackgroundMedium:
    python tools/dis64.py --at 0x100024ed8
    python tools/cygnus_db.py
    python tools/export_story.py --check
    python tools/export_story.py
    python tools/script_text.py

Addresses are the binary's own virtual addresses, as the plans cite them. Set `CYGNUS_BINARY` to read a different copy of the binary.
