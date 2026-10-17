"""Write the whole story as plain text, one file per episode, into analysis/script/.

Each file gives the episode's title and description, then every state once,
in the order play reaches them from the episode's start: its scene heading,
the characters' lines, the sound directions, what it sets, and where it goes
next. Every block is headed by its state's name, so a choice can be followed
by searching for the name it leads to. The text is the original's final
data (story version 53, episodes version 18), read by tools/cygnus_db.py.

    python tools/script_text.py
"""
import collections
import os
import re

import cygnus_db

OUT = os.path.join(cygnus_db.ROOT, "analysis", "script")

#: States whose data has a known fault, with the note printed at them.
NOTES = {
    "3_AAB008transition_m1e7": (
        "Note: GRAB IT and HANG ON both lead here, and this state has two automatic exits. "
        "The original took whichever came first in an unordered table, so either ending could "
        "follow either choice. The port sends GRAB IT on to 4_AABA002alexAthleticRefuseMatthewsEND_m1e7 "
        "and HANG ON on to 4_AABB003alexAthleticRefuseAlexEND_m1e7."),
}


def clean(text):
    """A script line without its #a,b# pacing marks."""
    return re.sub(r"\s+", " ", re.sub(r"#\d+,\d+#", " ", text)).strip()


def short(file_name):
    return file_name.rsplit(".", 1)[0]


def destinations(transition):
    if "destination" in transition:
        return [transition["destination"]]
    out = []
    for c in transition.get("conditions", []):
        out += [c["destination_if"], c["destination_else"]]
    return out


def variable_line(v):
    name = v["name"]
    if v.get("command") == "++":
        return "Raises %s by one." % name
    if v.get("command") == "--":
        return "Lowers %s by one." % name
    return "Sets %s to %s." % (name, v.get("value"))


def transition_line(t):
    kind = t["type"]
    if kind == "manual":
        hidden = ", hidden" if t.get("render") is False else ""
        return "Choice %s%s leads to %s." % (t.get("text", ""), hidden, t["destination"])
    if kind == "auto-timeout":
        return "With no choice within %s seconds, goes to %s." % (t.get("duration"), t["destination"])
    if t.get("conditions"):
        c = t["conditions"][0]
        return "If %s, goes to %s; otherwise to %s." % (
            c["expression"], c["destination_if"], c["destination_else"])
    return "Then goes to %s." % t["destination"]


def block(state, outgoing, end_names):
    lines = ["State: %s" % state["name"]]
    voice = [short(m["file_name"]) for m in state.get("media", []) if not m["file_name"].lower().startswith(("back_", "decision_"))]
    back = [short(m["file_name"]) for m in state.get("media", []) if m["file_name"].lower().startswith("back_")]
    decision = [short(m["file_name"]) for m in state.get("media", []) if m["file_name"].lower().startswith("decision_")]
    sound = []
    if voice:
        sound.append("Recording: %s." % ", ".join(voice))
    if back:
        sound.append("Background: %s." % ", ".join(back))
    if decision:
        sound.append("Decision sound: %s." % ", ".join(decision))
    if sound:
        lines.append(" ".join(sound))
    for line in state.get("script", []):
        text = clean(line["text"])
        if line["type"] == "HEADING":
            lines.append("Scene: %s" % text)
        elif line["type"] == "SPEECH":
            lines.append("%s: %s" % (line.get("character", "").title(), text))
        else:
            lines.append(text)
    for v in state.get("variables", []):
        lines.append(variable_line(v))
    for a in state.get("achievements", []):
        lines.append("Earns the achievement %s." % a["achievement_id"].rsplit(".", 1)[-1])
    if state["name"] in NOTES:
        lines.append(NOTES[state["name"]])
    for t in outgoing:
        lines.append(transition_line(t))
    if state["name"] in end_names:
        lines.append("End of the episode.")
    return "\n".join(lines)


def walk(start, out):
    """State names reachable from start, in the order play reaches them."""
    seen, order, queue = set(), [], collections.deque([start])
    while queue:
        name = queue.popleft()
        if name in seen:
            continue
        seen.add(name)
        order.append(name)
        for t in out[name]:
            queue.extend(d for d in destinations(t) if d not in seen)
    return order


def main():
    story, episodes, versions = cygnus_db.read_all()
    states = {s["name"]: s for s in story["states"]}
    out = collections.defaultdict(list)
    for t in story["transitions"]:
        out[t["origin"]].append(t)
    end_names = {e["end_state_name"] for e in episodes}
    playable = [e for e in episodes if e["initial_state_name"]]
    os.makedirs(OUT, exist_ok=True)

    placed = set()
    plans = []
    for e in playable:
        order = [n for n in walk(e["initial_state_name"], out) if n not in placed]
        placed.update(order)
        preview = e["preview_state_name"]
        preview_order = []
        if preview and preview not in placed:
            preview_order = [n for n in walk(preview, out) if n not in placed and n not in end_names]
            placed.update(preview_order)
        plans.append((e, order, preview_order))
    never = [s["name"] for s in story["states"] if s["name"] not in placed]

    written = []
    for i, (e, order, preview_order) in enumerate(plans):
        mission, number = e["episode_id"].split(".")[:2]
        title = "Codename Cygnus, Mission %s, Episode %s: %s" % (mission, number, e["title"])
        head = [title, e["description"],
                "Starts at %s and ends at %s. %d states." % (e["initial_state_name"], e["end_state_name"], len(order)),
                "From the original's final data: story version %s, episodes version %s." % (versions["states"], versions["missions"]),
                "Each block is one state. Search for a state's name to follow a choice to it."]
        parts = ["\n".join(head)]
        parts += [block(states[n], out[n], end_names) for n in order]
        if e["completion_text"]:
            parts.append("When the episode is finished, the game says:\n%s" % e["completion_text"])
        if preview_order:
            parts.append("Preview of the next episode, played after this one.")
            parts += [block(states[n], out[n], end_names) for n in preview_order]
        if i == len(plans) - 1 and never:
            parts.append("States no episode ever reaches, cut from the original.")
            parts += [block(states[n], out[n], end_names) for n in never]
        if e["credits"]:
            credit_lines = ["Credits"]
            for c in e["credits"]:
                if c["title"] and c["credit"]:
                    credit_lines.append("%s: %s" % (c["title"], c["credit"]))
                elif c["credit"] or c["title"]:
                    credit_lines.append(c["credit"] or c["title"])
            parts.append("\n".join(credit_lines))
        name = "m%se%s %s.txt" % (mission, number, e["title"])
        with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n\n".join(parts) + "\n")
        written.append((name, len(order) + len(preview_order)))

    for name, count in written:
        print("Wrote %s, %d states." % (name, count))
    print("States placed: %d of %d." % (len(placed) + len(never), len(states)))


if __name__ == "__main__":
    main()
