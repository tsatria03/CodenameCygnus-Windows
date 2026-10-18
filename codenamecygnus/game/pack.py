"""The mission pack, m1.dat: Mission 1's recordings in one encrypted file.

Section 2 of aidocks/plans/build_release_plan.md. A game release carries no recordings; the
game downloads the pack into ``%APPDATA%\\CodenameCygnus\\missions\\m1.dat`` (game/download.py)
and reads each recording from it as it is needed, decrypted in memory, never unpacked to
disk. ``tools/build_pack.py`` writes it.

The file, in order:

    b'CYGPACK1'         what it is
    4 bytes             the encrypted index's length, big-endian
    the index           encrypted JSON: {"files": {story key: [offset, length]}}, each offset
                        counted from the end of the index
    the recordings      each encrypted on its own

Each part is AES-256-GCM: a fresh 12-byte nonce, then the ciphertext with its tag; the
story key, or "index", is the associated data, so a part cannot be passed off as another.
The key is in the game itself, so this keeps out casual copying, not a determined person.

``game/data/text/m1_pack.json`` says the pack's size, SHA-256 and where it downloads from;
the tool writes it, and the build carries it.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import struct

from .. import paths

log = logging.getLogger('pack')

MAGIC = b'CYGPACK1'
KEY = bytes.fromhex('00745e94d6598e7dc1b544a3c896f598b646a57c1a52708470cfb0fd30f30366')
NONCE = 12
#: GCM's tag, on the end of every part.
TAG = 16
FILE_NAME = 'm1.dat'
INFO_NAME = 'm1_pack.json'
#: Where every version of the game downloads the pack from: its own release, whose address
#: never changes.
URL = 'https://github.com/tsatria03/CodenameCygnus-Windows/releases/download/mission-1/m1.dat'


class PackError(Exception):
    """The pack is not one, or is damaged."""


def _cipher():
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    return AESGCM(KEY)


def seal(data: bytes, name: str, cipher=None) -> bytes:
    cipher = cipher or _cipher()
    nonce = os.urandom(NONCE)
    return nonce + cipher.encrypt(nonce, data, name.encode('utf-8'))


def unseal(part: bytes, name: str, cipher=None) -> bytes:
    from cryptography.exceptions import InvalidTag
    cipher = cipher or _cipher()
    try:
        return cipher.decrypt(part[:NONCE], part[NONCE:], name.encode('utf-8'))
    except (InvalidTag, ValueError) as error:
        raise PackError('%s is damaged' % name) from error


def recording_key(file_name: str) -> str:
    """A recording's key, as game/recordings.py finds loose files by: the name, lower case,
    without .mp3."""
    return os.path.splitext(os.path.basename(file_name))[0].lower()


def mp3_files(folder: str) -> list:
    """Every MP3 under ``folder``, in a steady order, as (key, path); the first of a key wins."""
    found, seen = [], set()
    for root, dirs, files in os.walk(folder):
        dirs.sort()
        for f in sorted(files):
            if f.lower().endswith('.mp3'):
                key = recording_key(f)
                if key in seen:
                    log.warning('%s is there more than once; the first is packed', key)
                    continue
                seen.add(key)
                found.append((key, os.path.join(root, f)))
    return found


def write_pack(folder: str, dest: str, say=lambda text: None) -> int:
    """Pack every MP3 under ``folder`` into ``dest``, through ``dest``.part, renamed only
    once whole. Returns how many recordings it holds."""
    files = mp3_files(folder)
    if not files:
        raise PackError('there are no recordings under %s' % folder)
    cipher = _cipher()
    index, offset = {}, 0
    for key, path in files:
        length = NONCE + os.path.getsize(path) + TAG
        index[key] = [offset, length]
        offset += length
    sealed_index = seal(json.dumps({'files': index}, sort_keys=True).encode('utf-8'), 'index', cipher)
    partial = dest + '.part'
    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
    marks = {len(files) * step // 10 for step in range(1, 10)}
    with open(partial, 'wb') as out:
        out.write(MAGIC + struct.pack('>I', len(sealed_index)) + sealed_index)
        for count, (key, path) in enumerate(files, 1):
            with open(path, 'rb') as f:
                part = seal(f.read(), key, cipher)
            if len(part) != index[key][1]:
                raise PackError('%s changed while it was being packed' % path)
            out.write(part)
            if count in marks:
                say('  %d of %d recordings packed ...' % (count, len(files)))
    os.replace(partial, dest)
    return len(files)


def fingerprint(path: str, chunk=1 << 20) -> str:
    """The file's SHA-256, as hex."""
    digest = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            block = f.read(chunk)
            if not block:
                return digest.hexdigest()
            digest.update(block)


class Pack:
    """An m1.dat to read recordings from."""

    def __init__(self, path: str):
        self.path = path
        self.cipher = _cipher()
        with open(path, 'rb') as f:
            head = f.read(len(MAGIC) + 4)
            if len(head) < len(MAGIC) + 4 or head[:len(MAGIC)] != MAGIC:
                raise PackError('%s is not a mission pack' % path)
            size = struct.unpack('>I', head[len(MAGIC):])[0]
            sealed = f.read(size)
        if len(sealed) != size:
            raise PackError('%s is cut short' % path)
        try:
            self.index = json.loads(unseal(sealed, 'index', self.cipher))['files']
        except (ValueError, KeyError) as error:
            raise PackError('the index of %s cannot be read' % path) from error
        self.start = len(MAGIC) + 4 + size
        log.info('mission pack %s: %d recordings', path, len(self.index))

    def keys(self):
        return list(self.index)

    def __contains__(self, key):
        return key in self.index

    def read(self, key: str) -> bytes:
        """One recording, decrypted."""
        offset, length = self.index[key]
        with open(self.path, 'rb') as f:
            f.seek(self.start + offset)
            part = f.read(length)
        if len(part) != length:
            raise PackError('%s is cut short at %s' % (self.path, key))
        return unseal(part, key, self.cipher)


# ---- where it is, and what it should be ----------------------------------

def installed_path() -> str:
    """Where the game keeps the pack it downloaded."""
    return paths.user_path('missions', FILE_NAME)


def built_path() -> str:
    """Where tools/build_pack.py leaves it, which a source run uses when there is no other."""
    return os.path.join(paths.ROOT, 'dist', FILE_NAME)


def info_path() -> str:
    return os.path.join(paths.text(), INFO_NAME)


def read_info(path=None):
    """What m1_pack.json says: {'size', 'sha256', 'url'}, or None when it is not there."""
    try:
        with open(path or info_path(), encoding='utf-8') as f:
            info = json.load(f)
        if isinstance(info.get('size'), int) and isinstance(info.get('sha256'), str):
            info.setdefault('url', URL)
            return info
        log.warning('%s is not what it should be', path or info_path())
    except (OSError, ValueError):
        pass
    return None


def write_info(pack_file: str, path=None) -> dict:
    """m1_pack.json for this pack: its size, fingerprint and address."""
    info = {'size': os.path.getsize(pack_file), 'sha256': fingerprint(pack_file), 'url': URL}
    with open(path or info_path(), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(info, f, indent=2)
        f.write('\n')
    return info


def find_pack(info='unread'):
    """The pack to read: the downloaded one, or from source the one the tool built; None
    when there is none, or it is the wrong size or will not open."""
    info = read_info() if info == 'unread' else info
    candidates = [installed_path()] + ([] if paths.FROZEN else [built_path()])
    for path in candidates:
        if not os.path.isfile(path):
            continue
        if info is not None and os.path.getsize(path) != info['size']:
            log.warning('%s is %d bytes, not %d, so it is not used', path,
                        os.path.getsize(path), info['size'])
            continue
        try:
            return Pack(path)
        except (OSError, PackError) as error:
            log.warning('the mission pack %s cannot be used: %s', path, error)
    return None
