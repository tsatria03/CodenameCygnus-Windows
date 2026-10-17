"""Export the original's final data as the plain JSON the game reads.

Reads the story (version 53), the missions (version 18) and the resources
(version 11) from a temporary copy of game/CodenameCygnus.sqlite, through
tools/cygnus_db.py, fixes the van escape bug, checks the result, and only
when every check passes writes, into game/data/text/:

    missions.json    the missions, episodes, locks and credits
    resources.json   which recordings each episode's parts hold
    states.json      the story: states and transitions

The bundled mission_descriptor.json, resource_descriptor.json and
states_descriptor.json (all version 1) stay untouched beside them. The plan
is aidocks/plans/story_export_plan.md.

    python tools/export_story.py            check, then write
    python tools/export_story.py --check    check only, write nothing
"""
import collections
import copy
import json
import os
import re
import sys

import cygnus_db

ROOT = cygnus_db.ROOT
TEXT = os.path.join(ROOT, "game", "data", "text")
AUDIO = os.path.join(ROOT, "game", "data", "audio")

#: States nothing leads to, cut from the original. Reported as a note, not a failure.
KNOWN_UNREACHED = {"026gentlemenFlavor_m1e8", "46BopenItResponse_m1e8"}

#: The van escape bug in Signum Cygni: GRAB IT and HANG ON both lead to this state, which has
#: two automatic exits, and the original took whichever its unordered table gave first.
VAN_STATE = "3_AAB008transition_m1e7"
#: (the prompt the choice is made at, the choice, the new copy's name, the ending it leads to)
VAN_SPLIT = (
    ("3_AAB007matthewsEscapePrompt_m1e7", "GRAB IT", "3_AAB008transitionGrabIt_m1e7",
     "4_AABA002alexAthleticRefuseMatthewsEND_m1e7"),
    ("3_AAB007alexEscapePrompt_m1e7", "HANG ON", "3_AAB008transitionHangOn_m1e7",
     "4_AABB003alexAthleticRefuseAlexEND_m1e7"),
)

#: A condition is a variable, a comparison and a whole number, such as event.m1e2_serum==1.
EXPRESSION = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*(==|>=|<=|>|<)-?\d+$")

#: Key order for a state, as in the bundled states_descriptor.json.
STATE_KEYS = ("name", "media", "script", "variables", "achievements")


def say(text=""):
    print(text, flush=True)


def destinations(transition):
    if "destination" in transition:
        return [transition["destination"]]
    out = []
    for c in transition.get("conditions", []):
        out += [c["destination_if"], c["destination_else"]]
    return out


def fix_van_escape(story):
    """Split VAN_STATE into one copy for each way in, each with a single automatic exit."""
    states = {s["name"]: s for s in story["states"]}
    original = states.get(VAN_STATE)
    if original is None:
        return "the van escape state %s is missing, so it was not fixed" % VAN_STATE
    transitions = []
    for t in story["transitions"]:
        if t["origin"] == VAN_STATE:
            continue                                    # its two automatic exits are replaced below
        for prompt, choice, copy_name, _ending in VAN_SPLIT:
            if t["origin"] == prompt and t.get("destination") == VAN_STATE and t.get("text") == choice:
                t = dict(t, destination=copy_name)
        transitions.append(t)
    new_states = [s for s in story["states"] if s["name"] != VAN_STATE]
    for _prompt, _choice, copy_name, ending in VAN_SPLIT:
        state = copy.deepcopy(original)
        state["name"] = copy_name
        new_states.append(state)
        transitions.append({"type": "auto", "origin": copy_name, "destination": ending})
    story["states"] = new_states
    story["transitions"] = transitions
    return None


def recording_index():
    """Every recording on disk under game/data/audio, by its name without .mp3, in lower case."""
    found = collections.defaultdict(list)
    for folder, _dirs, files in os.walk(AUDIO):
        for f in files:
            if f.lower().endswith(".mp3"):
                found[f[:-4].lower()].append(os.path.join(folder, f))
    return found


def recording_for(file_name, index):
    """The file the game will play for a story file name, as the audio plan finds it."""
    name = os.path.splitext(file_name)[0].lower()
    if name.endswith("_teaser"):
        name = name[:-len("_teaser")]
    paths = index.get(name, [])
    return paths[0] if len(paths) == 1 else None


def check(data):
    """Return (problems, notes). Any problem stops the export."""
    story, episodes = data["story"], data["episodes"]
    problems, notes = [], []
    states = {}
    for s in story["states"]:
        if s["name"] in states:
            problems.append("The state %s appears twice." % s["name"])
        states[s["name"]] = s
    out = collections.defaultdict(list)
    for t in story["transitions"]:
        out[t["origin"]].append(t)
        if t["origin"] not in states:
            problems.append("A transition leaves %s, which is not a state." % t["origin"])
        for d in destinations(t):
            if d not in states:
                problems.append("A transition from %s leads to %s, which is not a state." % (t["origin"], d))
        for c in t.get("conditions", []):
            if not EXPRESSION.match(c["expression"]):
                problems.append("The condition %s, leaving %s, cannot be read." % (c["expression"], t["origin"]))
        if t["type"] == "manual" and not t.get("text"):
            problems.append("A choice leaving %s has no word to say." % t["origin"])
        if t["type"] == "auto-timeout" and not isinstance(t.get("duration"), int):
            problems.append("The timed choice leaving %s has no whole number of seconds." % t["origin"])

    for name, ts in out.items():
        autos = [t for t in ts if t["type"] == "auto"]
        if len(autos) > 1:
            problems.append("The state %s has %d automatic exits." % (name, len(autos)))
        if autos and any(t["type"] == "manual" for t in ts):
            problems.append("The state %s has both a choice and an automatic exit." % name)

    reached = set()
    for e in episodes:
        start, end = e["initial_state_name"], e["end_state_name"]
        if not start:
            continue                                    # Mission 2, never released
        for which, name in (("start", start), ("end", end), ("preview", e["preview_state_name"])):
            if name and name not in states:
                problems.append("Episode %s's %s state %s is not a state." % (e["episode_id"], which, name))
        seen, queue = set(), [start]
        while queue:
            n = queue.pop()
            if n in seen or n not in states:
                continue
            seen.add(n)
            for t in out[n]:
                queue.extend(destinations(t))
        if end not in seen:
            problems.append("Episode %s, %s, cannot reach its end state %s." % (e["episode_id"], e["title"], end))
        stuck = sorted(n for n in seen if not out[n] and n != end)
        for n in stuck:
            problems.append("Episode %s stops at %s, which leads nowhere." % (e["episode_id"], n))
        reached |= seen
        if e["preview_state_name"]:
            reached.add(e["preview_state_name"])
    unreached = sorted(set(states) - reached)
    if set(unreached) == KNOWN_UNREACHED:
        notes.append("Two states nothing leads to, cut from the original: %s." % " and ".join(unreached))
    else:
        for n in unreached:
            notes.append("No episode reaches the state %s." % n)

    index = recording_index()
    names = sorted({m["file_name"] for s in story["states"] for m in s["media"]})
    for file_name in names:
        name = os.path.splitext(file_name)[0].lower()
        key = name[:-len("_teaser")] if name.endswith("_teaser") else name
        if len(index.get(key, [])) > 1:
            problems.append("The recording %s is on disk more than once: %s." % (file_name, ", ".join(index[key])))
        elif recording_for(file_name, index) is None:
            problems.append("The recording %s has no MP3 under game/data/audio." % file_name)
    return problems, notes, len(names)


def missions_json(data):
    """missions.json, in mission_descriptor.json's own shape."""
    by_mission = collections.defaultdict(list)
    for e in data["episodes"]:
        episode = {k: v for k, v in e.items() if k != "mission_id"}
        by_mission[e["mission_id"]].append(episode)
    missions = [{"mission_id": m["mission_id"], "description": m["description"],
                 "episodes": by_mission[m["mission_id"]]} for m in data["missions"]]
    company = {"episode_id": 1000, "title": "Reactive Studios", "episode_lock": {"is_locked": False},
               "description": "", "completion_text": "", "credits": data["company_credits"]}
    return {"general": {"version": data["versions"]["missions"]}, "missions": missions,
            "company_credits": company}


def resources_json(data):
    """resources.json, in resource_descriptor.json's own shape."""
    return {"general": {"version": data["versions"]["resources"]},
            "resources": [{"version": r["version"], "name": r["name"], "files": r["files"]}
                          for r in data["resources"]]}


def states_json(data):
    """states.json, in states_descriptor.json's own shape and key order."""
    story = data["story"]
    states = []
    for s in story["states"]:
        ordered = {k: s[k] for k in STATE_KEYS if k in s}
        ordered.update({k: v for k, v in s.items() if k not in ordered})
        states.append(ordered)
    return {"general": {"version": data["versions"]["states"]}, "states": states,
            "transitions": story["transitions"]}


def write_json(name, value):
    path = os.path.join(TEXT, name)
    temp = path + ".tmp"
    with open(temp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, indent=1, ensure_ascii=False)
        f.write("\n")
    os.replace(temp, path)
    return os.path.getsize(path)


def main(argv):
    only_check = "--check" in argv
    data = cygnus_db.read_everything()
    v = data["versions"]
    say("Read from a copy of the database: story version %s, missions version %s, resources version %s."
        % (v["states"], v["missions"], v["resources"]))

    trouble = fix_van_escape(data["story"])
    if trouble:
        say("Problem: " + trouble + ".")
        return 1
    say("Fixed the van escape in Signum Cygni: GRAB IT now leads to %s, and HANG ON to %s."
        % (VAN_SPLIT[0][3], VAN_SPLIT[1][3]))

    problems, notes, recordings = check(data)
    story = data["story"]
    playable = [e for e in data["episodes"] if e["initial_state_name"]]
    say("Checked %d states, %d transitions, %d episodes and %d recordings."
        % (len(story["states"]), len(story["transitions"]), len(playable), recordings))
    for note in notes:
        say("Note: " + note)
    if problems:
        say("%d problem%s found, so nothing was written:" % (len(problems), "" if len(problems) == 1 else "s"))
        for p in problems:
            say("Problem: " + p)
        return 1
    say("Every check passed.")
    if only_check:
        say("Nothing was written, since --check was given.")
        return 0
    for name, value in (("missions.json", missions_json(data)), ("resources.json", resources_json(data)),
                        ("states.json", states_json(data))):
        size = write_json(name, value)
        say("Wrote game/data/text/%s, %d kilobytes." % (name, round(size / 1024)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
