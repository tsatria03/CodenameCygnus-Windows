"""Build the mission pack, m1.dat, from the loose recordings.

    python tools/build_pack.py

Section 2 of aidocks/plans/build_release_plan.md. It packs every MP3 under
game/data/audio/missions/m1/, encrypted one by one (codenamecygnus/game/pack.py), into
dist\\m1.dat, through m1.dat.part, renamed once whole. Then it reads the pack back to check
every recording opens, and writes game/data/text/m1_pack.json, the pack's size, SHA-256 and
download address, which the game carries to check a download against; commit that file.

releaser.py's "Upload the mission pack" puts dist\\m1.dat on the mission-1 release. A run
from source with game/data/audio/missions deleted plays from dist\\m1.dat as well, so the
pack can be heard before it is uploaded.
"""
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from codenamecygnus.game import pack as packs  # noqa: E402

SOURCE = os.path.join(ROOT, 'game', 'data', 'audio', 'missions', 'm1')
DEST = os.path.join(ROOT, 'dist', packs.FILE_NAME)
INFO = os.path.join(ROOT, 'game', 'data', 'text', packs.INFO_NAME)


def say(text=''):
    print(text, flush=True)


def main():
    if not os.path.isdir(SOURCE):
        say('there are no loose recordings at %s, so there is nothing to pack.' % SOURCE)
        say('if the missions folder was renamed to test the pack, give it back its name, '
            'missions, first.')
        return 1
    say('packing the recordings under %s into %s ...' % (SOURCE, DEST))
    started = time.perf_counter()
    count = packs.write_pack(SOURCE, DEST, say)
    say('%d recordings packed, %.0f MB, in %.0f seconds.'
        % (count, os.path.getsize(DEST) / (1 << 20), time.perf_counter() - started))
    say('checking that every recording opens ...')
    pack = packs.Pack(DEST)
    for key, path in packs.mp3_files(SOURCE):
        with open(path, 'rb') as f:
            if pack.read(key) != f.read():
                say('%s does not come back as it went in, so the pack is not right.' % key)
                return 1
    info = packs.write_info(DEST, INFO)
    say('every recording opens.')
    say('SHA-256: %s' % info['sha256'])
    say('%s is written; commit it, so the game can check its download.' % INFO)
    return 0


def run():
    """Double-clicked, or run on its own at a keyboard, the window waits at the end, so what
    happened can be heard before it closes, an error included (tsatria03, 2026-10-18: "the
    py file imideatly quits when I double click it")."""
    try:
        code = main()
    except Exception:
        import traceback
        say('the pack could not be built:')
        say(traceback.format_exc().rstrip())
        code = 1
    if sys.stdin.isatty():
        say()
        try:
            input('Finished. Press Enter to close this window.')
        except EOFError:
            pass
    return code


if __name__ == '__main__':
    sys.exit(run())
