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

**All-time analysis** is the team-assess run, and only the run. Every score, quote, facet, confidence
and recommendation on the page comes from `team-assess/snapshots/aurora-q{2,3}-2026.json`, the same
output rendered as prose in `team-assess/output/report-aurora-q3-2026.md`. Nothing on the view is this
demo's reading of the data.

The Lencioni pyramid carries each layer's score from the latest run and its movement against the
previous one, with a ⚠ on any move the run itself flagged, because the scorer's run-to-run variance is
unmeasured and a jump over a point could be variance rather than change. Fill opacity follows the
score, so a strong layer reads strong. Below it, priority actions in the run's own words, then one card
per dimension, Trust first, with the verbatim evidence the run cited and each facet's score and
confidence.

Two things this deliberately does not do. It does not compute a score of its own, and a dimension
absent from a run says so rather than showing a zero, because absence of measurement is not a result.

The authored behavior-code marks in `marks.json` are **not** used here. They cover one meeting, and
using them on a page titled all-time made Results read "no signal" while the run scored it 4.4, the
highest of the five. They belong to the live replay, where a single meeting is the subject.

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
