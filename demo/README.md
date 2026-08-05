# Demo: the metric contract running on the Aurora Skills dataset

A first pass at step 1 of the build order in
`docs/superpowers/specs/2026-08-04-facilitator-and-scorer-integration.md`: compute PRD 05's metric
contract over data already in this repo and show it three ways.

**Nothing here is invented.** Every name, quote, duration, and percentage is read from
`simulated-data/aurora-skills`. The dataset is synthetic, and it says so; this demo adds no data of
its own.

## Run

```bash
python3 demo/build_demo_data.py     # writes demo/data.js
open demo/index.html                # no server needed
```

`build_demo_data.py` reads only from `simulated-data/aurora-skills` and has no dependencies outside
the standard library.

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

**Meeting readout** is the per-attendee table on both measurement bases. Content-only reproduces the
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
