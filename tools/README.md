# tools

Scripts for reading the original app. None of them is part of the game, and none ever writes to `game/`.

- `macho64.py`: reads the arm64 slice of `game/Cygnus`, the original's binary. It lists the segments and sections, the Objective-C classes and their methods, the selector references and the imported functions. Standard library only. Run it on its own to print the slice's layout and whether its code is encrypted; it is not (`cryptid` 0).
- `dis64.py`: disassembles methods from that slice, naming the selectors, imported functions, classes and strings each instruction refers to. It needs `capstone` (`pip install capstone`), which the game itself does not.

Examples, from the repo root:

    python tools/macho64.py
    python tools/dis64.py --list CCSoundManager
    python tools/dis64.py CCSoundManager playBackgroundMedium:
    python tools/dis64.py --at 0x100024ed8

Addresses are the binary's own virtual addresses, as the plans cite them. Set `CYGNUS_BINARY` to read a different copy of the binary.
