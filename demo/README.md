# ~~Claude~~ Team Insights: the metric contract on the Aurora Skills dataset

A first pass at step 1 of the build order in
`docs/superpowers/specs/2026-08-04-facilitator-and-scorer-integration.md`: compute PRD 05's metric
contract over data already in this repo and show it three ways.

**Nothing here is invented, with one labeled exception.** Every name, quote, duration, and
percentage is read from `simulated-data/aurora-skills`. The dataset is synthetic, and it says so;
this demo adds no data of its own. The exception is `marks.json`: behavior-code assignments against
`rubric/obm-behavior-codes.json`, authored by an AI coder reading the transcript. Assignments are
judgment and are labeled as authored everywhere they surface; the build validates that every mark
cites a real code id and a quote that appears verbatim in the cited turn, and fails otherwise.

## Run

```bash
python3 demo/build_demo_data.py     # writes demo/data.js
open demo/index.html                # no server needed
```

`build_demo_data.py` reads only from `simulated-data/aurora-skills` and has no dependencies outside
the standard library.

## The four views

**Live session** replays `2026-06-09_roadmap-review` turn by turn at a selectable 15x/60x/240x and
runs four rules from PRD 05's metric contract as the transcript arrives. Each nudge fires only once
the evidence exists, and each cites the count that triggered it and the design constraint it
respects. A second rail docks rubric marks as the replay reaches the turns they cite, with a
running five-dimension tally.

The meeting was picked because it carries the dataset's strongest seeded signals. What the rules
surface, all of it matching `GROUND_TRUTH.md`:

| Rule | What it finds here |
|---|---|
| Talk-time balance | Dana holds 43% of all speech, 66.2% of content speech, against a 40% healthy ceiling |
| Silence is not absence | 8 of 12 attendees never speak. Naomi is silent here and contributed 9 times elsewhere this quarter |
| Questions are participation | Flags a question-heavy speaker as participating, never as low engagement |
| Interruption | One seeded interruption, logged and explicitly not scored |

**Analysis** is the rubric consuming the same meeting, with the Lencioni pyramid at the top: five
layers, Trust at the base, each showing the meeting's marks and cluster-spread confidence, each
clicking through to its evidence. Below it, 14 authored marks over the 120-code book, grouped by
dimension in pyramid order, each with its stable code id, verbatim quote, and speaker. It follows the team-assess spec's rules: evidence cites a code id, observations matching
no code are reported as `uncoded` candidates rather than folded into a score, cluster spread caps
confidence, and no 1–5 score appears because the scorer that would compute one is not built. The
view also names what the codebook cannot see: Dana's 66.2% dominance is an aggregate, so it belongs
to the metric contract, not to any single-utterance code. The two layers are complements.

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
PRD 05 it stays team-level. The coding view holds the same line from the other side: marks were
authored once, offline, and the page only renders them; a live build would replace `marks.json`
with a model call whose output obeys the same validation.
