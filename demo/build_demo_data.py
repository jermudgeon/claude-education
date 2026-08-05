"""Extract a single meeting plus the quarter comparison into one JSON blob for the demo page.

Reads only from simulated-data/aurora-skills, with one labeled exception. Turn timings and
text come from the VTT and its metadata sidecar, the quarter comparison comes from
_comparison/before_after.json, and the elsewhere-contribution counts are tallied from the
Slack export, standups, and pull requests.

The exception is demo/marks.json: behavior-code assignments against rubric/obm-behavior-codes.json,
authored by an AI coder reading the transcript. Assignments are judgment, so they are labeled as
authored everywhere they surface. What this script enforces is fidelity: every mark must cite a
code id that exists in the rubric and a quote that appears verbatim in the cited turn, or the
build fails.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "simulated-data" / "aurora-skills"
MEETING = "2026-06-09_roadmap-review"
ERA = "before-q2-2026"

CUE = re.compile(
    r"^(\d\d:\d\d:\d\d\.\d{3,4}) --> (\d\d:\d\d:\d\d\.\d{3,4})\s*$\n<v ([^>]+)>(.*)$",
    re.MULTILINE,
)


def parse_vtt(path):
    """Return the cue text in file order, so it can be zipped onto the metadata turns."""
    return [m.group(4).strip() for m in CUE.finditer(path.read_text(encoding="utf-8"))]


def load_turns(era, meeting):
    meta = json.loads((DATA / era / "transcripts" / "meta" / f"{meeting}.json").read_text())
    text = parse_vtt(DATA / era / "transcripts" / f"{meeting}.vtt")
    turns = meta["turns"]
    if len(text) != len(turns):
        raise SystemExit(f"cue/turn mismatch: {len(text)} cues vs {len(turns)} turns")
    for turn, line in zip(turns, text):
        turn["text"] = line
    return meta["summary"], turns


def elsewhere_counts(era):
    """Messages, standup entries, and PR comments per person outside the meeting room."""
    counts = {}

    def bump(handle, field, n=1):
        counts.setdefault(handle, {"messages": 0, "standups": 0, "pr_comments": 0})
        counts[handle][field] += n

    export = DATA / era / "slack-export"
    users = json.loads((export / "users.json").read_text())
    by_id = {u["id"]: u.get("name") or u.get("handle") for u in users}

    for day in sorted(export.glob("*/*.json")):
        for msg in json.loads(day.read_text()):
            handle = by_id.get(msg.get("user"))
            if handle:
                bump(handle, "messages")
            for reply in msg.get("replies", []) or []:
                handle = by_id.get(reply.get("user"))
                if handle:
                    bump(handle, "messages")

    standups = json.loads((DATA / era / "standups" / "standups.json").read_text())
    for item in standups.get("entries", []):
        if item.get("handle"):
            bump(item["handle"], "standups")

    prs = json.loads((DATA / era / "git" / "pull_requests.json").read_text())
    for pr in prs.get("pull_requests", []):
        for comment in pr.get("comments", []):
            if comment.get("user"):
                bump(comment["user"], "pr_comments")
        for review in pr.get("reviews", []):
            if review.get("reviewer"):
                bump(review["reviewer"], "pr_comments")

    return counts


def load_coding(turns):
    """Resolve authored marks against the rubric and the transcript, refusing anything unfaithful."""
    rubric = json.loads((ROOT / "rubric" / "obm-behavior-codes.json").read_text())
    codes = {c["id"]: c for c in rubric["codes"]}
    coding = json.loads((Path(__file__).parent / "marks.json").read_text())

    if coding["meeting"] != MEETING or coding["era"] != ERA:
        raise SystemExit(f"marks.json targets {coding['meeting']}, build targets {MEETING}")

    for mark in coding["marks"]:
        code = codes.get(mark["code"])
        if code is None:
            raise SystemExit(f"cue {mark['cue']}: code {mark['code']} not in the rubric")
        turn = turns[mark["cue"] - 1]
        if mark["quote"] not in turn["text"]:
            raise SystemExit(f"cue {mark['cue']}: quote not found verbatim in that turn")
        mark.update(
            dimension=code["dimension"],
            cluster=code["cluster"],
            valence=code["valence"],
            behavior=code["behavior"],
            speaker=turn["speaker"],
            kind=turn["kind"],
            at_s=turn["start_s"],
        )

    for item in coding["uncoded"]:
        turn = turns[item["cue"] - 1]
        if item["quote"] not in turn["text"]:
            raise SystemExit(f"uncoded cue {item['cue']}: quote not found verbatim in that turn")
        item.update(speaker=turn["speaker"], at_s=turn["start_s"])

    coding["rubric"] = {
        "source": "rubric/obm-behavior-codes.json",
        "total_codes": rubric["count"],
        "dimensions": {
            dim: {
                "codes": sum(1 for c in rubric["codes"] if c["dimension"] == dim),
                "clusters": len({c["cluster"] for c in rubric["codes"] if c["dimension"] == dim}),
            }
            for dim in ["Trust", "Conflict", "Commitment", "Accountability", "Results"]
        },
    }
    return coding


def main():
    summary, turns = load_turns(ERA, MEETING)
    comparison = json.loads((DATA / "_comparison" / "before_after.json").read_text())
    ground_truth = json.loads((DATA / "ground_truth.json").read_text())

    blob = {
        "source": {
            "repo": "jermudgeon/claude-education",
            "dataset": "simulated-data/aurora-skills",
            "meeting": MEETING,
            "era": ERA,
            "note": "Synthetic dataset. Every name, quote, and number originates in the repo, not in this demo.",
        },
        "summary": summary,
        "turns": turns,
        "comparison": comparison["comparison"],
        "eras": comparison["eras"],
        "elsewhere": elsewhere_counts(ERA),
        "signals": ground_truth.get("signals", ground_truth),
        "coding": load_coding(turns),
    }

    # Written as a script rather than raw JSON so the page opens straight from
    # the filesystem, with no server and no fetch blocked by CORS.
    out = Path(__file__).parent / "data.js"
    out.write_text("window.DEMO=" + json.dumps(blob, separators=(",", ":")) + ";\n")

    content = [t for t in turns if t["kind"] == "content"]
    print(f"meeting        {summary['title']} ({summary['date']})")
    print(f"turns          {len(turns)} total, {len(content)} content")
    print(f"duration       {summary['duration_min']} min")
    print(f"peak talk      {max(s['talk_pct'] for s in summary['speakers'].values())}%")
    print(f"elsewhere      {len(blob['elsewhere'])} people tallied")
    print(f"coding         {len(blob['coding']['marks'])} marks validated, {len(blob['coding']['uncoded'])} uncoded")
    print(f"wrote          {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
