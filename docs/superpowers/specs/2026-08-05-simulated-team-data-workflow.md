# Simulated Team-Data Workflow — Design Spec

**Date:** 2026-08-05
**Status:** Approved
**Purpose:** A repeatable workflow for generating synthetic, internally-consistent team artifacts
to develop and validate a team-assessment tool (or any tool that scores collaboration from
heterogeneous inputs). The Aurora Skills dataset (`simulated-data/aurora-skills/`) is the first
instance produced with this workflow.

---

## 1. When to use this

Use when you need realistic team data to build or test a tool, but real data is unavailable,
sensitive, or lacks a known ground truth. The workflow produces data where **you control exactly
what signals are present**, so you can measure whether the tool detects them.

Do **not** use it as a substitute for real data in the final evaluation of a shipped tool — it is
for development, regression testing, and demos.

---

## 2. Core principles

1. **Seed the signals deliberately.** Every behavior the tool should detect is planted on purpose,
   at a known location. Nothing important is left to chance.
2. **Ground truth is a first-class artifact.** A machine-readable key records every seeded signal,
   its file+location, and the expected detection. The dataset is only as useful as its answer key.
3. **One cast, cross-referenced.** A single roster of people and a single timeline run through every
   artifact (chat, transcripts, PRs, issues, docs) so entity-linking and "who did what" have real hits.
4. **Before → after, and close the loop.** Two periods (dysfunction present → improved) let the tool
   show a trend. Best case: the tool's own assessment of period 1 produces recommendations, the team
   "enacts" them in period 2, and the period-2 assessment validates the change. The loop is traceable.
5. **Separate substance from texture.** Author the signal-bearing dialogue by hand (the "spine");
   generate the realistic filler (roll call, backchannels, pauses) programmatically and tag it, so
   metrics computed from the spine stay exact no matter how much filler is added for realism.
6. **Deterministic generation.** Fixed seed, no wall-clock reads — same inputs produce the same
   output, so the ground truth never drifts from the data.

---

## 3. Workflow phases

### Phase 1 — Scenario & cast
Pick a concrete fictional org, a domain, and a roster (~10-12 people, 2 teams). Give each person a
role and one or two behavioral traits that will carry signals (a dominator, a silent-but-engaged
contributor, a junior who hides a mistake, a Socratic questioner). Fix the timeline (e.g., two
quarters).

### Phase 2 — Signal catalog
Before writing content, list every signal the tool must detect and, for each: the behavior, the
healthy/unhealthy direction, and which artifact type(s) will carry it. This catalog becomes the
ground-truth key. If the tool has a rubric, map each signal to a rubric dimension/facet now.

### Phase 3 — Author the substantive spine
Write the meeting dialogue, chat threads, PR reviews, issues, retros, and docs that carry the
seeded signals. Keep it real and specific — anything generic is filler and should be cut or made
concrete. Cross-reference relentlessly (a chat idea becomes a meeting becomes a PRD).

### Phase 4 — Generate format & texture
A deterministic generator emits the real export formats and wraps transcripts in realistic
procedural texture to reach believable length:
- **Real formats:** Slack export layout, WebVTT transcripts with diarization, PR/issue JSON,
  standup logs, retro-board JSON, survey CSV.
- **Texture (tagged, excluded from metrics):** join logistics, roll call, agenda, status rounds,
  backchannels, screen-share pauses, Q&A, action-item wrap-up, and distributed pauses. Target a
  realistic duration and silence ratio; never stack pauses into one giant gap.
- **Metrics computed from the spine only** (turns tagged `content`, not `texture`).

### Phase 5 — Compute the ground truth
The generator computes the objective metrics (talk-time, question ratios, silent members,
interruptions, survey averages) directly from the data and writes them into the ground-truth files,
so the answer key is derived from the data, not asserted. Editorial signals that aren't computable
(e.g., "a decision reopened 3 times") are set as documented constants.

### Phase 6 — The assessment loop (optional but recommended)
Produce the tool's expected output for period 1 (scores + recommendations). Author period 2 so the
team enacts those recommendations, then produce the period-2 expected output showing the measured
improvement, with a trend vs period 1. Map each recommendation to the period-2 artifacts that
enact it.

### Phase 7 — Verify
Run the generator; validate every JSON parses, every transcript is well-formed and monotonic, and
every requirement holds (duration floors, no unintended silent members, the before/after deltas
point the right way). Re-read a sample as a skeptic.

---

## 4. The content/texture split (the key technique)

The hardest constraint is usually "make it realistic-length" without absurd dead air or corrupting
the metrics. The resolution:

- The **spine** is authored, signal-bearing, and the sole basis for every metric.
- The **texture** is generated, realistic, and tagged `texture` at the cue/turn level.
- Realism (length, rhythm, silence) comes from texture + pauses; **signal fidelity** comes from
  the spine. Because metrics ignore texture, you can add as much realistic filler as needed without
  moving a single seeded number — including keeping a facilitator's procedural chatter from
  inflating their talk-time.

---

## 5. Nuance handling

Raw metrics mislead without context. Encode the context in the data, not just the prose:
- **Dominance vs. leadership:** record who was meant to lead each meeting; a lead dominating a small
  working session is *expected* and flagged as such, while a non-lead dominating (or heavy dominance
  in a large all-hands) is the real signal.
- **Participation vs. airtime:** questions count as participation; cross-reference chat before
  calling anyone disengaged (the silent-but-engaged case).

---

## 6. Deliverables (per dataset)

```
<dataset>/
├── generate.py                 # deterministic generator (formats + texture + computed metrics)
├── README.md                   # overview, cast, structure, how to regenerate
├── ground_truth.json           # machine-readable seeded-signal key (+ rubric mapping)
├── GROUND_TRUTH.md             # narrative version + computed before/after table
├── <period-1>/ , <period-2>/   # per-period: slack-export, transcripts(+meta), git, issues,
│                               #   standups, retros, surveys, _metrics
├── assessments/                # expected tool output per period + the loop mapping
├── _comparison/                # computed before/after deltas
└── prds/ , wiki/               # in-world supporting docs
```

---

## 7. Reuse checklist

- [ ] New scenario, cast, and timeline chosen
- [ ] Signal catalog written and mapped to the tool's rubric
- [ ] Spine authored; every artifact cross-references the same cast/timeline
- [ ] Generator emits real formats + tagged texture; metrics computed from spine only
- [ ] Duration/realism targets met; no stacked silences
- [ ] Ground truth computed and written; editorial constants documented
- [ ] (If applicable) assessment loop: period-1 recommendations → period-2 enactment → validation
- [ ] Verified: JSON valid, transcripts well-formed, requirements hold, deltas correct
- [ ] Deterministic: re-running the generator reproduces the dataset exactly
