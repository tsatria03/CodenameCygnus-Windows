"""Read the original's final data out of game/CodenameCygnus.sqlite.

The app kept the newest story (version 53) in its Core Data store, as an
NSKeyedArchiver plist in ZCCGAMEDATA.ZSTATESJSON, and the newest episodes
(version 18) in the ZCCMISSION, ZCCEPISODE, ZCCEPISODELOCK and ZCCCREDIT
tables. The JSON files bundled with the app are the older version 1.

The database is never opened in place: SQLite can fold the -wal file into
the main file when a connection closes, which would change game/. Every
read works on a copy in a temporary folder. Standard library only.
"""
import os
import plistlib
import shutil
import sqlite3
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "game", "CodenameCygnus.sqlite")


def _connect(folder):
    """Copy the database and its -wal and -shm files into folder, and open the copy."""
    for suffix in ("", "-wal", "-shm"):
        if os.path.exists(DB + suffix):
            shutil.copy2(DB + suffix, os.path.join(folder, "copy.sqlite" + suffix))
    return sqlite3.connect(os.path.join(folder, "copy.sqlite"))


def _unarchive(blob):
    """Decode an NSKeyedArchiver plist of dictionaries, arrays, strings and numbers."""
    archive = plistlib.loads(blob)
    objects = archive["$objects"]

    def resolve(value):
        if isinstance(value, plistlib.UID):
            value = objects[value.data]
        if isinstance(value, dict):
            if "NS.keys" in value:
                return {resolve(k): resolve(v) for k, v in zip(value["NS.keys"], value["NS.objects"])}
            if "NS.objects" in value:
                return [resolve(v) for v in value["NS.objects"]]
            if "NS.string" in value:
                return value["NS.string"]
            return {k: resolve(v) for k, v in value.items() if k != "$class"}
        if value == "$null":
            return None
        return value

    return resolve(archive["$top"]["root"])


def _number(value):
    """A number the archive kept as text, such as "7" or "-1", as a number."""
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return value
    return value


def _boolean(value):
    if isinstance(value, str):
        return value.lower() == "true"
    return bool(value)


def _clean_states(story):
    """Put back the types the archive turned into text."""
    for state in story["states"]:
        for medium in state.get("media", []):
            medium["id"] = _number(medium.get("id"))
        for line in state.get("script", []):
            line["id"] = _number(line.get("id"))
        for variable in state.get("variables", []):
            if "value" in variable:
                variable["value"] = _number(variable["value"])
    for transition in story["transitions"]:
        if "duration" in transition:
            transition["duration"] = _number(transition["duration"])
        if "render" in transition:
            transition["render"] = _boolean(transition["render"])
    return story


def read_all():
    """Return (story, episodes, version numbers) from a temporary copy of the database.

    story is {"general", "states", "transitions"}, as in the bundled
    states_descriptor.json. episodes is a list of dictionaries in the
    bundled mission_descriptor.json's own key names, sorted by episode_id.
    """
    folder = tempfile.mkdtemp(prefix="cygnus_db_")
    try:
        db = _connect(folder)
        try:
            versions = dict(zip(("missions", "resources", "states"), db.execute(
                "select ZMISSIONDATAVERSION, ZRESOURCEDATAVERSION, ZSTATESDATAVERSION from ZCCGAMEDATA").fetchone()))
            blob = db.execute("select ZSTATESJSON from ZCCGAMEDATA").fetchone()[0]
            story = _clean_states(_unarchive(blob))
            episodes = []
            rows = db.execute(
                "select e.Z_PK, m.ZMISSIONID, e.ZEPISODEID, e.ZEPISODETITLE, e.ZEPISODEDESCRIPTION,"
                " e.ZCOMPLETIONTEXT, e.ZINITIALSTATENAME, e.ZENDSTATENAME, e.ZPREVIEWSTATENAME,"
                " e.ZPREVIEWEPISODEID, l.ZISLOCKED, l.ZLOCKEDBYID"
                " from ZCCEPISODE e left join ZCCMISSION m on e.ZMISSION = m.Z_PK"
                " left join ZCCEPISODELOCK l on l.ZEPISODE = e.Z_PK order by e.ZEPISODEID")
            for (pk, mission, eid, title, description, completion, start, end,
                 preview, preview_id, locked, locked_by) in rows.fetchall():
                credits = [{"title": text or "", "credit": person or ""} for person, text in db.execute(
                    "select ZCREDITPERSON, ZCREDITTEXT from ZCCCREDIT where ZEPISODE = ? order by ZORDER", (pk,))]
                lock = {"is_locked": bool(locked)}
                if locked and locked_by:
                    lock["locked_by_id"] = locked_by
                episodes.append({
                    "mission_id": mission,
                    "episode_id": eid,
                    "title": title or "",
                    "episode_lock": lock,
                    "description": (description or "").strip(),
                    "completion_text": (completion or "").strip(),
                    "credits": credits,
                    "initial_state_name": start or "",
                    "end_state_name": end or "",
                    "preview_state_name": preview or "",
                    "preview_episode_id": preview_id or "",
                })
            return story, episodes, versions
        finally:
            db.close()
    finally:
        shutil.rmtree(folder, ignore_errors=True)


if __name__ == "__main__":
    story, episodes, versions = read_all()
    print("versions:", versions)
    print("states:", len(story["states"]), "transitions:", len(story["transitions"]))
    for e in episodes:
        print(e["episode_id"], e["title"], "locked" if e["episode_lock"]["is_locked"] else "open",
              e["initial_state_name"] or "-", "to", e["end_state_name"] or "-")
