"""Assemble the Scores & trend section: real scorer output when it exists, real moments always.

Reads only what the repo publishes. Snapshots are the real team-assess runs in
team-assess/snapshots/aurora-*.json (the repo removed authored scores in #19 so that scores
only ever come from a real run); when none exist, the section renders pending score slots
rather than invented numbers.
The dimension-to-signal alignment comes from assessments/five-dysfunctions-signal-map.json.
Each moment is a verbatim cue pulled from the transcript it happened in, located by a
distinctive substring; extraction fails loudly if an anchor stops matching, so a regenerated
dataset can never leave a stale quote on the page.

Milliseconds are parsed as an integer over 1000, so a malformed 4-digit field like .1000
(the generator's old carry bug) still lands on the correct second.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "simulated-data" / "aurora-skills"
ASSESS = DATA / "assessments"
RUNS = ROOT / "team-assess" / "snapshots"

CUE = re.compile(
    r"^(\d\d):(\d\d):(\d\d)\.(\d{3,4}) --> (\d\d):(\d\d):(\d\d)\.(\d{3,4})\s*$\n<v ([^>]+)>(.*)$",
    re.MULTILINE,
)

MOMENTS = {
    "trust": {
        "era": "after-q3-2026",
        "meeting": "2026-08-04_minor-incident-retro",
        "anchor": "posted in #incidents within the hour",
        "signal": "hidden_mistake_trust",
    },
    "conflict": {
        "era": "after-q3-2026",
        "meeting": "2026-07-14_beta-arch-review",
        "anchor": "you all just changed my mind in the room",
        "signal": "changed_mind",
    },
    "commitment": {
        "era": "after-q3-2026",
        "meeting": "2026-09-15_q3-retro",
        "anchor": "publish the before/after so other Alaska teams",
        "signal": "reopened_conflict_3x",
    },
    "accountability": {
        "era": "after-q3-2026",
        "meeting": "2026-08-04_minor-incident-retro",
        "anchor": "exactly what I asked him for back in April",
        "signal": "peer_accountability",
    },
    "results": {
        "era": "after-q3-2026",
        "meeting": "2026-09-15_q3-retro",
        "anchor": "The work is still us choosing to look",
        "signal": "learning_from_failure",
    },
}


def seconds(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def find_moment(era, meeting, anchor):
    path = DATA / era / "transcripts" / f"{meeting}.vtt"
    hits = [m for m in CUE.finditer(path.read_text(encoding="utf-8")) if anchor in m.group(10)]
    if len(hits) != 1:
        raise SystemExit(f"anchor {anchor!r} matched {len(hits)} cues in {path.name}, need exactly 1")
    cue = hits[0]
    start = seconds(*cue.group(1, 2, 3, 4))
    summary = json.loads(
        (DATA / era / "transcripts" / "meta" / f"{meeting}.json").read_text(encoding="utf-8")
    )["summary"]
    return {
        "quote": cue.group(10).strip(),
        "timestamp_s": round(start, 1),
        "mmss": f"{int(start // 60):02d}:{int(start % 60):02d}",
        "meeting_id": meeting,
        "meeting_title": summary["title"],
        "meeting_date": summary["date"],
        "era": era,
        "source": f"simulated-data/aurora-skills/{era}/transcripts/{meeting}.vtt",
    }


def period_key(snapshot):
    quarter, year = snapshot["period"].split("-")
    return int(year), int(quarter.lstrip("Q"))


def load_run(path):
    s = json.loads(path.read_text(encoding="utf-8"))
    _, quarter, year = s["period"].split("-")
    return {
        "period": f"{quarter.upper()}-{year}",
        "run_date": s.get("run_date"),
        "overall": s.get("overall_health"),
        "dimensions": {k: {"score": v["score"]} for k, v in s["dimensions"].items()},
    }


def main():
    snapshots = sorted((load_run(p) for p in RUNS.glob("aurora-*.json")), key=period_key)
    current = snapshots[-1] if snapshots else None
    prior = snapshots[-2] if len(snapshots) > 1 else None

    signal_map = json.loads(
        (ASSESS / "five-dysfunctions-signal-map.json").read_text(encoding="utf-8")
    )
    by_signal = {m["signal"]: m for m in signal_map["mappings"]}

    moments = {}
    for dimension, spec in MOMENTS.items():
        moment = find_moment(spec["era"], spec["meeting"], spec["anchor"])
        moment["signal"] = by_signal[spec["signal"]]
        moments[dimension] = moment

    blob = {
        "source": {
            "snapshots_dir": "team-assess/snapshots/",
            "signal_map": "simulated-data/aurora-skills/assessments/five-dysfunctions-signal-map.json",
            "note": "Scores render only from a real team-assess run; none is invented here.",
        },
        "current": current,
        "prior": prior,
        "map": signal_map["mappings"],
        "moments": moments,
    }

    out = Path(__file__).parent / "scores.js"
    out.write_text("window.SCORES=" + json.dumps(blob, separators=(",", ":")) + ";\n", encoding="utf-8")

    for dimension in moments:
        m = moments[dimension]
        print(f"{dimension:<15} {m['mmss']} {m['meeting_id']:<34} {m['quote'][:50]}")
    state = "scores live" if current else "no run yet: score slots render pending"
    print(f"snapshots      {len(snapshots)} found ({state})")
    print(f"wrote          {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
