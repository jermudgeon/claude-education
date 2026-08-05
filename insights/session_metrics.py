"""Emit one session_metrics document for a meeting: the seam between the layers.

PRD 05 computes the metric contract once; the PRD 06 facilitator and the team-assess scorer
both consume it through this document. It carries the computed metrics and the attributed
quotes that justify them, and nothing scored. Shape is fixed by
insights/schema/session_metrics.schema.json.

Usage:
    python3 insights/session_metrics.py --era before-q2-2026 --meeting 2026-06-09_roadmap-review
    python3 insights/session_metrics.py --era before-q2-2026 --meeting 2026-06-09_roadmap-review --out insights/examples/
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from metrics import (
    DATA,
    SILENT_PCT,
    THRESHOLD_PCT,
    elsewhere_counts,
    measure,
    parse_vtt,
)

NOT_COMPUTED = {
    "dissent_timing": "needs the decision record and cross-meeting context, not one transcript",
    "changed_mind_events": "editorial signal; grounded in authored content, not derivable from counts (open question 5)",
    "reopened_conflict": "needs the same topic tracked across meetings",
    "psych_safety_trend": "the pulse survey is per sprint, not per meeting",
}


def load_meeting(era, meeting_id):
    meta_path = DATA / era / "transcripts" / "meta" / f"{meeting_id}.json"
    vtt_path = DATA / era / "transcripts" / f"{meeting_id}.vtt"
    doc = json.loads(meta_path.read_text(encoding="utf-8"))
    return doc["summary"], doc["turns"], vtt_path


def build(era, meeting_id):
    summary, turns, vtt_path = load_meeting(era, meeting_id)
    cues = parse_vtt(vtt_path)
    if len(cues) != len(turns):
        raise SystemExit(f"cue/turn mismatch: {len(cues)} cues vs {len(turns)} turns")
    m = measure(summary, turns)
    elsewhere = elsewhere_counts(era)

    interrupt_events = []
    evidence = []
    for turn in m["interruptions"]:
        interrupt_events.append(
            {"turn_idx": turn["idx"], "speaker": turn["speaker"], "at_s": turn["start_s"]}
        )
        evidence.append(
            {
                "metric": "interruptions",
                "quote": cues[turn["idx"]][3],
                "source": f"{era}/transcripts/{meeting_id}.vtt",
                "speaker": turn["speaker"],
                "timestamp_s": turn["start_s"],
                "provoked_by": None,
            }
        )

    flagged = [
        {
            "handle": handle,
            "name": m["names"][handle],
            "talk_pct": m["talk_pct"][handle],
            "elsewhere": elsewhere.get(
                handle, {"messages": 0, "standups": 0, "pr_comments": 0}
            ),
        }
        for handle in m["silent"]
    ]

    return {
        "schema_version": "1.0",
        "meeting": {
            "id": summary["id"],
            "title": summary["title"],
            "date": summary["date"],
            "era": summary.get("era"),
            "duration_s": summary["duration_s"],
            "attendee_count": summary["attendee_count"],
        },
        "basis": "content",
        "metrics": {
            "talk_time_balance": {
                "threshold_pct": THRESHOLD_PCT,
                "dominant": {
                    "handle": m["dominant"],
                    "name": m["names"][m["dominant"]],
                    "talk_pct": m["dominant_pct"],
                },
                "breached": m["dominant_pct"] > THRESHOLD_PCT,
                "speakers": {
                    handle: {
                        "name": m["names"][handle],
                        "attended": m["attended"][handle],
                        "talk_s": m["talk_s"][handle],
                        "talk_pct": m["talk_pct"][handle],
                    }
                    for handle in m["names"]
                },
            },
            "questions_vs_assertions": {
                handle: {
                    "questions": m["questions"][handle],
                    "assertions": m["assertions"][handle],
                    "q_to_a": (
                        round(m["questions"][handle] / m["assertions"][handle], 2)
                        if m["assertions"][handle]
                        else None
                    ),
                }
                for handle in m["names"]
            },
            "silent_but_engaged": {
                "silent_pct_ceiling": SILENT_PCT,
                "flagged": flagged,
            },
            "dissent_timing": None,
            "changed_mind_events": None,
            "reopened_conflict": None,
            "interruptions": {"count": len(interrupt_events), "events": interrupt_events},
            "psych_safety_trend": None,
        },
        "not_computed": NOT_COMPUTED,
        "evidence": evidence,
        "provenance": {
            "generator": "insights/session_metrics.py",
            "inputs": [
                f"simulated-data/aurora-skills/{era}/transcripts/{meeting_id}.vtt",
                f"simulated-data/aurora-skills/{era}/transcripts/meta/{meeting_id}.json",
                f"simulated-data/aurora-skills/{era}/slack-export/",
                f"simulated-data/aurora-skills/{era}/standups/standups.json",
                f"simulated-data/aurora-skills/{era}/git/pull_requests.json",
            ],
            "synthetic": True,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--era", required=True)
    parser.add_argument("--meeting", required=True)
    parser.add_argument("--out", help="directory to write <meeting>.session_metrics.json into")
    args = parser.parse_args()

    doc = build(args.era, args.meeting)
    text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        out = Path(args.out) / f"{args.meeting}.session_metrics.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
