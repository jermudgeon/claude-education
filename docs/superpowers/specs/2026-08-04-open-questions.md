# Open questions

**Date:** 2026-08-04
**Companion to:** `2026-08-04-facilitator-and-scorer-integration.md`

Every question has a default, so silence never blocks work and any answer can be applied later without a rewrite. Questions marked **blocking** have no safe default.

---

## Product and scope

### 1. Is PRD 06 built, or does PRD 05 ship alone first?

PRD 06 is listed as "Concept (the one genuinely unsolved piece)" and PRD 05 as "Prototype (AUR-11)". PRD 05 has a complete metric contract and a dataset to test against. PRD 06 has an unresolved core design problem.

**Default:** PRD 05 first, all the way to a readout that reproduces the ground-truth table. PRD 06 has no way to know when to intervene until the metric contract actually runs.

### 2. Does the classroom case drive the design, or the team case?

PRD 06 is written for a classroom; the dataset is a working team. The mechanics are shared but the stakes are not: grading students is explicitly a non-goal, and a classroom has a facilitator with authority a peer team does not.

**Default:** build for the team case, which is what the dataset supports, and keep classroom-specific behavior out until there is classroom data.

---

## Measurement

### 3. What is the run-to-run variance of one scoring pass? — blocking

Decides whether the trend feature can ship. The v0.8 spec calls a 0.2 move a direction change with no stated basis. Score identical inputs five times and record the per-dimension spread.

No default. A trend label backed by nothing is worse than no trend label.

### 4. Can the scorer reproduce the ground-truth before-and-after table?

`GROUND_TRUTH.md` publishes eleven signals across two quarters. This is an accuracy test the repo already contains.

**Default:** treat reproducing it as the acceptance criterion for the scorer, and do not render reports until it passes.

### 5. Are the four editorial signals in scope for automated detection?

`GROUND_TRUTH.md` names four signals set as constants in `generate.py` rather than computed: license conflict reopens, regression time to surface, hallway dissent events, and changed-mind-in-room events. They are grounded in authored content but not derivable from counts alone.

**Default:** attempt them with the model, score them against the constants, and report detection rate separately from the computed metrics. Do not blend a detected signal and a counted one into one confidence number.

### 6. Does prosody require audio? (carried from PRD 05)

PRD 05 marks this **UNKNOWN**. The metadata sidecars carry interruption, overlap, and latency, but true prosody needs audio.

**Default:** text and timing only. The dataset's interruption and overlap timings are enough for the interruption metric, and audio ingestion carries consent weight the text path does not.

### 7. How is "confidently wrong" measured? (carried from PRD 06)

PRD 06 marks this **UNKNOWN** and names it the failure mode raised repeatedly in the brainstorm: the facilitator reading the group incorrectly but with conviction.

**Default:** every nudge cites the count that triggered it, as the demo does, so a wrong nudge is visibly wrong rather than merely assertive. That is a mitigation, not a measurement, and the measurement is still open.

---

## Privacy and consent

### 8. Who can read a snapshot? — answered 2026-08-04

Everyone in the session, their manager, both, or only an aggregate. Determines whether people speak freely, which determines whether the data is worth collecting.

**Answered (Erik, 2026-08-04): everyone, no permissions layer, because this is a demo.** In Erik's words: "Everyone right now, dont worry about perms, this is a demo." Revisit before any real team's data is captured; the question returns to blocking at that boundary.

### 9. Does audio get recorded at all?

PRD 05 and 06 both assume a transcript exists and neither says how. A live facilitator implies a microphone.

**Default:** transcript only, and discard audio if any is captured. Question 6's default keeps this viable.

### 10. How long do snapshots live?

Trend analysis wants years; nothing else does.

**Default:** four periods at full fidelity, then scores only, with evidence dropped.

### 11. How does someone opt out mid-session?

Not addressed anywhere. A tool that makes this awkward gets resented into disuse.

**Default:** a visible control that stops capture for everyone, plus a post-session review in which any participant can strike a quote before the `session_metrics` document is written.

---

## Build

### 12. Which speech-to-text provider, and is diarization good enough?

Everything downstream depends on knowing who is speaking. The dataset's VTT files come pre-diarized, so this risk stays invisible until the first real room.

**Default:** pick one, test in an actual multi-person room before building on top of it, and expect manual correction to be a primary interaction rather than a rare fix.

### 13. One repo or several?

team-assess is Python, the facilitator is a web app, and both read the rubric and the metric contract.

**Default:** one repo. Share JSON Schema and the rubric; do not share config.

### 14. Does team-assess run on demand or on a schedule?

The spec's CLI is manual; the trend feature implies a cadence.

**Default:** manual, because a scheduled job emitting noisy trend labels compounds question 3 into a recurring notification nobody trusts.

---

## Answered by documents already in this repo

Recorded so they do not reopen.

- **Are individuals ever scored?** No. PRD 05 non-goals: "surveillance or individual performance scoring. This is a team mirror, not a manager's dashboard." team-assess scores teams; `speaker_id` is stripped before anything reaches a report.
- **Do questions count as participation?** Yes, always, and a question-heavy speaker is never scored low. PRD 05 design constraint 1, ground truth signal 9.
- **Is silence disengagement?** No. Cross-reference other channels first. PRD 05 design constraint 3, ground truth signal 2.
- **Who computes the metrics?** PRD 05, once. PRD 06 and team-assess consume them; neither recomputes.
- **Does the facilitator score anything?** No. It reads the metric contract and decides whether to intervene.
- **What is the product called?** ~~Claude~~ Team Insights, with the wordmark striking through "Claude."
- **Content-only or all-speech metrics?** Both are sanctioned by the dataset (`ground_truth.json` → `metrics_note`). Report which basis is in use; never mix them silently.
