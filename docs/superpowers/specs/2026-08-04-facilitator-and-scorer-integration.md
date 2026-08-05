# How the facilitator, the insights tool, and team-assess fit together

**Date:** 2026-08-04
**Status:** Draft for review
**Reconciles:** PRD 05 (collaboration insights), PRD 06 (classroom / group agent facilitator), and `2026-08-04-team-dysfunction-rubric-design.md` (team-assess v0.8)

---

## What this resolves

Three documents in this repo describe overlapping systems, and it is not obvious from any one of them where the boundaries are.

- **PRD 05** measures collaboration and defines the metric contract.
- **PRD 06** participates in the conversation as a facilitator, and says it "depends on 05's metric contract to know when to intervene."
- **team-assess** scores a team against the Five Dysfunctions and produces a period trend.

They are one product in three layers, and the layering already implied by PRD 06 holds:

| Layer | Document | Job | Timescale |
|---|---|---|---|
| Participate | PRD 06 | Reframe the goal, balance voices, draw out the opposing view | Live, in the room |
| Measure | PRD 05 | Compute the metric contract, nudge, produce readouts | Live and per meeting |
| Score | team-assess | Apply the rubric, persist snapshots, report trends | Per period |

**One rule keeps them from colliding: measurement is computed once, in PRD 05, and both neighbours consume it.** PRD 06 reads it to decide when to intervene. team-assess reads it as evidence. Neither recomputes it, because two implementations of talk-time balance will disagree and the disagreement will be silent.

## Where the earlier draft of this document was wrong

An earlier version of this integration note proposed a fresh set of session observations, including a raw `speaking_time_share` per person. That was wrong twice over, and the repo already says so:

1. **The metric contract exists.** PRD 05 defines eight metrics with sources and healthy directions. Inventing a parallel list guarantees drift. The list below is PRD 05's, unchanged.
2. **Raw airtime share is the specific mistake the dataset was built to catch.** Ground truth signal 2: Naomi attends Q2 meetings, never speaks, and is the top contributor in chat, standups, and pull requests. "A naive airtime metric scores her ~0 and is *wrong*." Signal 9 makes the same point about James, who asks far more than he asserts. Any metric that reads silence as disengagement fails this dataset on purpose.

The correction is not to drop airtime. It is to never report airtime without the cross-reference, which is exactly what PRD 05's `silent-but-engaged` metric specifies.

## The metric contract, unchanged from PRD 05

| Metric | Source | Healthy direction |
|---|---|---|
| Talk-time balance | transcript cue durations | No one holds more than about 40% of airtime |
| Questions vs assertions | `?` vs `.`/`!` per speaker | More questions is participation, **not** low engagement |
| Silent-but-engaged | transcript attendance and chat volume | Flag people who attend silently yet contribute elsewhere, do not score them zero |
| Dissent timing | objection timestamp vs decision | Dissent before the decision is healthy, in the hallway after is not |
| Changed-mind events | stance shift in room | At least one per contested decision means the round moved |
| Reopened conflict | same topic across meetings | A third reopening without new information is suppressed, not settled |
| Interruptions and overlap | overlapping cue timing | Prosody is signal, not noise |
| Psychological safety trend | pulse survey per sprint | Dips around incidents should recover |

PRD 05's three design constraints are binding on all three layers, not just on PRD 05:

1. Questions count as participation.
2. Stay humble. Report patterns, not verdicts about people.
3. Silence is not absence.

## The tension with team-assess, and how it resolves

PRD 05's non-goals say "surveillance or individual performance scoring. This is a team mirror, not a manager's dashboard." team-assess assigns 1-to-5 scores and persists them per period. Those are compatible only if the scoring is strictly team-level.

**Resolution: team-assess scores teams, never individuals.** Evidence retains `speaker_id` in storage so the counts can be recomputed, and strips it before anything reaches a report. This is a constraint on the scorer, not a preference, because the metric contract makes per-person inference trivial the moment attribution leaks into output.

This also settles a question left open in the earlier draft. PRD 05 answers it: individuals are never scored.

## What each layer emits

```
transcript + chat + PRs + standups + retros + surveys
        │
        ▼
   PRD 05  ──►  metric contract, computed once
        │              │
        │              ├──►  PRD 06 reads it live, decides whether to intervene
        │              │
        │              └──►  session_metrics document, one per meeting
        │                          │
        ▼                          ▼
   live nudges              team-assess ingests as evidence
                                   │
                                   ▼
                            snapshot per period, trend, report
```

`session_metrics` is the seam. It carries the computed metrics, the attributed quotes that justify them, and nothing scored. team-assess gains a reader for it in `ingestion/`, which the v0.8 spec already anticipates ("additional formats added via ingestion module"), so no architectural change is required on either side.

Two changes to the team-assess schema make the seam work:

- `evidence` becomes objects rather than bare strings, so speaker, timestamp, and the question that provoked the statement survive ingestion. All three are nullable, so document-sourced evidence is unaffected.
- `input_files` becomes `input_sources` with a type, because a meeting is not a file path.

## The dataset is an accuracy test, not just sample data

`simulated-data/aurora-skills` ships `ground_truth.json`, `GROUND_TRUTH.md`, and a computed before-and-after table across two quarters of the same team. That changes what can be claimed about the scorer.

The v0.8 spec calls a move of more than 0.2 a direction change and more than 1.0 a warning, with no stated basis. Two measurements now settle whether those thresholds mean anything, and both are runnable today:

1. **Repeatability.** Score identical inputs five times and record the per-dimension spread. If run-to-run variance exceeds 0.2, every direction label is noise.
2. **Accuracy.** Score `before-q2-2026` and `after-q3-2026` and check whether the deltas move in the directions the ground-truth table publishes. A scorer that cannot reproduce a documented before-and-after on synthetic data will not be believed on real data.

Ship the trend feature after both, not before. This is the single most important thing to do before writing report-rendering code.

## Naming

The three layers currently have no shared product name. Candidates are in the pull request description; the working names in this document are the PRD numbers deliberately, so nothing has to be renamed twice.

## Build order

1. Compute PRD 05's metric contract over the dataset, and reproduce the `GROUND_TRUTH.md` table. `demo/` in this pull request is a first pass at exactly this.
2. Run the two measurements above against team-assess.
3. Agree the `session_metrics` schema. Both remaining tracks depend on it and neither can start without it.
4. team-assess scorer over document inputs. Trends stay dark until step 2 says otherwise.
5. PRD 06 facilitator: goal capture and restatement first, voice balancing second.
6. First end-to-end run: one live session scored alongside documents from the same period.
