# ~~Claude~~ Team Insights: the metric contract on the Aurora Skills dataset

A first pass at step 1 of the build order in
`docs/superpowers/specs/2026-08-04-facilitator-and-scorer-integration.md`: compute PRD 05's metric
contract over data already in this repo and show it three ways.

**Nothing here is invented.** Every name, quote, duration, and percentage is read from
`simulated-data/aurora-skills`. The dataset is synthetic, and it says so; this demo adds no data of
its own.

## Run

```bash
python3 demo/build_demo_data.py     # writes demo/data.js (one meeting + the quarter comparison)
python3 demo/build_coding_data.py   # writes demo/coding.js (the assessments/ analysis + moments)
open demo/index.html                # no server needed
```

Both build scripts read only from `simulated-data/aurora-skills` and have no dependencies outside
the standard library. When a new analysis lands in `assessments/`, rerun `build_coding_data.py`
and the coding view picks it up.

## The three views

**Live session** replays `2026-06-09_roadmap-review` turn by turn at 60x and runs four rules from
PRD 05's metric contract as the transcript arrives. Each nudge fires only once the evidence exists,
and each cites the count that triggered it and the design constraint it respects.

The meeting was picked because it carries the dataset's strongest seeded signals. What the rules
surface, all of it matching `GROUND_TRUTH.md`:

| Rule | What it finds here |
|---|---|
| Talk-time balance | Dana holds 43% of all speech, 66.2% of content speech, against a 40% healthy ceiling |
| Silence is not absence | 8 of 12 attendees never speak. Naomi is silent here and contributed 9 times elsewhere this quarter |
| Questions are participation | Flags a question-heavy speaker as participating, never as low engagement |
| Interruption | One seeded interruption, logged and explicitly not scored |

**Readout & behavior coding** puts the quarter's analysis and the meeting readout on one page.

The coding half renders the team-assess output shipped in `assessments/` (the dataset's in-world
analysis, not a live model run): per dimension, the score, its confidence, and the trend against
Q2, with a ⚠ on any move over 1.0 points because the scorer's run-to-run variance is unmeasured
(open question 3). Each card carries **one verbatim moment**: a real cue, with its timestamp and
transcript, that embodies why the dimension moved (Ben's 41-minute disclosure is why vulnerability
is up), plus the seeded-signal Q2 → Q3 contrast from `five-dysfunctions-signal-map.json`. Every
card and the page footer drill down into the raw snapshot JSON. The choice of which moment to
feature is `build_coding_data.py`'s; the quotes, timestamps, scores, and trend are all read from
the repo, and extraction fails loudly if a regenerated transcript no longer contains an anchor.

The readout half is the per-attendee table on both measurement bases. Content-only reproduces the
66.2% that `GROUND_TRUTH.md` publishes for this meeting; all-speech is what a live tool actually
hears. Both cross the 40% threshold, so the nudge fires either way. The dataset sanctions both bases
(`ground_truth.json` → `metrics_note`); mixing them silently is the thing to avoid.

**Quarter over quarter** is the eleven-signal before-and-after table straight from
`_comparison/before_after.json`. This is the accuracy test for any scorer built here: reproduce this
table before believing a trend line.

## What this demo is not

It does not score anyone, and it has no model call in it. Every number is arithmetic over the
transcript metadata, which is the point: the metric contract is countable, and the parts that need a
model can be added on top of a layer that already works. Scoring belongs to team-assess, and per
PRD 05 it stays team-level.
