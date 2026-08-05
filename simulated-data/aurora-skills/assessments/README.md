# Assessments — the Q2 → feedback → Q3 loop (scoring is external)

**This dataset does not score anything.** The `team-assess` tool and the team running it produce
the scored assessments (dimension scores, confidence, overall health, trend). What lives here is
the **data-side** of the loop: the seeded signals, their mapping to the rubric, and the qualitative
recommendations the Q3 content was authored to answer.

```
Q2 data ──(team-assess: someone else scores)──▶ recommendations
                                                     │
                                        the team enacts them in Q3
                                                     │
Q3 data ──(team-assess scores again)──▶ improvement on the targeted dimensions
```

| File | What it is |
|---|---|
| `q2-anticipated-recommendations.md` | The qualitative recommendations the Q2 dysfunctions should surface, and the Q3 artifacts that answer each. **No scores.** |
| `five-dysfunctions-signal-map.json` | Every seeded signal → rubric v0.9 dimension + observable facet + verbatim act, before vs after. Data ground truth, not a score. |

## What is and isn't asserted here

- **Not asserted:** any 1–5 dysfunction score, confidence level, overall health, or trend delta —
  those are the scorer's output.
- **Asserted (objective, computed from the data):** talk-time %, question ratios, silent-member
  counts, interruption counts, reopen counts, and the pulse-survey values. These are inputs/facts,
  in `../_comparison/before_after.json` and `../<era>/_metrics/`.

## Discrimination traps

The dataset deliberately includes **false positives** — content that a shallow scorer misreads.
See `../ground_truth.json → discrimination_traps` for each trap, what it looks like, what it
actually is, and where it lives. A good scorer must tell the seeded true signals apart from these.
