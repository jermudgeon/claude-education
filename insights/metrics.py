"""Second implementation of the PRD 05 rollups, computed from the rows on disk.

generate.py computes its summaries from in-memory structures and then writes both the data
files and the published numbers. Everything here is recomputed from what actually landed on
disk: turn rows in transcripts/meta, cue timings in the VTT files, contribution rows in the
Slack export, standups, and pull requests, and survey rows in pulse.csv. The only facts taken
as given are the roster and who attended, which exist nowhere else in the dataset. Agreement
with _comparison/before_after.json is therefore a check on the files, not an echo of the code
that wrote them.

Definitions are PRD 05's and generate.py's, unchanged: the content basis (kind == "content"
turns only), a group meeting has more than two attendees, and present-but-silent means
attended with under 3% of content airtime.
"""

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "simulated-data" / "aurora-skills"
ERAS = ("before-q2-2026", "after-q3-2026")

THRESHOLD_PCT = 40.0
SILENT_PCT = 3.0

CUE = re.compile(
    r"^(\d\d):(\d\d):(\d\d\.\d\d\d) --> (\d\d):(\d\d):(\d\d\.\d\d\d)\s*$\n<v ([^>]+)>(.*)$",
    re.MULTILINE,
)


def _seconds(hours, minutes, seconds):
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def parse_vtt(path):
    """Return (start_s, end_s, speaker, text) per cue, in file order."""
    return [
        (_seconds(m[1], m[2], m[3]), _seconds(m[4], m[5], m[6]), m[7], m[8].strip())
        for m in CUE.finditer(path.read_text(encoding="utf-8"))
    ]


def meetings(era):
    """Yield (summary, turns, vtt_path) for every meeting in an era, in id order."""
    for meta_path in sorted((DATA / era / "transcripts" / "meta").glob("*.json")):
        doc = json.loads(meta_path.read_text(encoding="utf-8"))
        yield doc["summary"], doc["turns"], DATA / era / "transcripts" / f"{meta_path.stem}.vtt"


def measure(summary, turns):
    """One meeting's numbers, recomputed from its turn rows on the content basis.

    The roster and attendance come from the sidecar summary because no other file records
    who was in the room; every duration, percentage, and count is recomputed from the turns.
    """
    roster = summary["speakers"]
    talk = {handle: 0.0 for handle in roster}
    questions = {handle: 0 for handle in roster}
    assertions = {handle: 0 for handle in roster}
    for turn in turns:
        if turn["kind"] != "content":
            continue
        talk[turn["handle"]] += turn["dur_s"]
        questions[turn["handle"]] += turn["questions"]
        assertions[turn["handle"]] += turn["assertions"]
    total = sum(talk.values())
    pct = {handle: round(100 * talk[handle] / total, 1) for handle in roster}
    attended = {handle: roster[handle]["attended"] for handle in roster}
    dominant = max(roster, key=lambda handle: pct[handle])
    return {
        "id": summary["id"],
        "attendee_count": summary["attendee_count"],
        "names": {handle: roster[handle]["name"] for handle in roster},
        "attended": attended,
        "talk_s": {handle: round(talk[handle], 1) for handle in roster},
        "talk_pct": pct,
        "questions": questions,
        "assertions": assertions,
        "dominant": dominant,
        "dominant_pct": pct[dominant],
        "interruptions": [turn for turn in turns if turn["interrupt"]],
        "silent": [
            handle for handle in roster if attended[handle] and pct[handle] < SILENT_PCT
        ],
    }


def survey_means(era):
    """(psych safety mean, conflict health mean) over every row of pulse.csv."""
    with open(DATA / era / "surveys" / "pulse.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    safety = [int(row["psych_safety_1to5"]) for row in rows]
    conflict = [int(row["conflict_is_healthy_1to5"]) for row in rows]
    return round(sum(safety) / len(safety), 2), round(sum(conflict) / len(conflict), 2)


def _mean(values):
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 1) if values else None


def rollup(era):
    """An era's comparison signals, shaped to match _comparison/before_after.json."""
    per_meeting = [measure(summary, turns) for summary, turns, _ in meetings(era)]
    group = [m for m in per_meeting if m["attendee_count"] > 2]
    naomi_attended = [m for m in group if m["attended"].get("naomi")]
    safety, conflict = survey_means(era)
    return {
        "group_meetings": len(group),
        "peak_dominant_talk_pct": max((m["dominant_pct"] for m in group), default=None),
        "avg_dominant_talk_pct": _mean([m["dominant_pct"] for m in group]),
        "dana_peak_talk_pct": max(
            (m["talk_pct"]["dana"] for m in group if "dana" in m["talk_pct"]), default=None
        ),
        "dana_avg_talk_pct": _mean(
            [m["talk_pct"]["dana"] for m in group if "dana" in m["talk_pct"]]
        ),
        "naomi_avg_talk_pct": _mean([m["talk_pct"]["naomi"] for m in naomi_attended]),
        "naomi_meetings_attended": len(naomi_attended),
        "naomi_silent_meetings": sum(1 for m in naomi_attended if "naomi" in m["silent"]),
        "total_interruptions": sum(len(m["interruptions"]) for m in per_meeting),
        "avg_psych_safety_1to5": safety,
        "avg_conflict_health_1to5": conflict,
    }


def vtt_drift(era):
    """Cue-by-cue disagreements between each VTT and its metadata sidecar.

    The two file families are written separately, so an edit to one can silently orphan the
    other. Returns a list of human-readable problems; empty means they agree.
    """
    problems = []
    for summary, turns, vtt_path in meetings(era):
        cues = parse_vtt(vtt_path)
        if len(cues) != len(turns):
            problems.append(
                f"{summary['id']}: {len(cues)} VTT cues vs {len(turns)} sidecar turns"
            )
            continue
        for turn, (start, end, speaker, _) in zip(turns, cues):
            if (
                abs(turn["start_s"] - start) > 0.0011
                or abs(turn["end_s"] - end) > 0.0011
                or turn["speaker"] != speaker
            ):
                problems.append(
                    f"{summary['id']} cue {turn['idx']}: sidecar "
                    f"({turn['speaker']} {turn['start_s']}-{turn['end_s']}) vs VTT "
                    f"({speaker} {start:.3f}-{end:.3f})"
                )
    return problems


def elsewhere_counts(era):
    """Messages, standup entries, and PR comments per handle, outside the meeting room.

    This is the cross-reference the silent-but-engaged metric requires: silence in the room
    is never reported without the person's contribution volume everywhere else.
    """
    counts = {}

    def bump(handle, field, n=1):
        counts.setdefault(handle, {"messages": 0, "standups": 0, "pr_comments": 0})
        counts[handle][field] += n

    export = DATA / era / "slack-export"
    users = json.loads((export / "users.json").read_text(encoding="utf-8"))
    by_id = {u["id"]: u.get("name") for u in users}

    for day in sorted(export.glob("*/*.json")):
        for message in json.loads(day.read_text(encoding="utf-8")):
            handle = by_id.get(message.get("user"))
            if handle:
                bump(handle, "messages")
            for reply in message.get("replies", []) or []:
                handle = by_id.get(reply.get("user"))
                if handle:
                    bump(handle, "messages")

    standups = json.loads(
        (DATA / era / "standups" / "standups.json").read_text(encoding="utf-8")
    )
    for entry in standups.get("entries", []):
        if entry.get("handle"):
            bump(entry["handle"], "standups")

    prs = json.loads(
        (DATA / era / "git" / "pull_requests.json").read_text(encoding="utf-8")
    )
    for pr in prs.get("pull_requests", []):
        for comment in pr.get("comments", []):
            if comment.get("user"):
                bump(comment["user"], "pr_comments")
        for review in pr.get("reviews", []):
            if review.get("reviewer"):
                bump(review["reviewer"], "pr_comments")

    return counts
