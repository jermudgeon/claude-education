# Q2 → Q3 loop: anticipated recommendations (score-free)

**Scoring is not done here.** The `team-assess` tool (and the people running it) produce the scored
assessment — dimension scores, confidence, overall health, trend. This dataset does **not** assert
those numbers.

What this file provides is the qualitative side of the loop, so evaluators can check the tool's Q2
output against what Q3 actually addresses: the **anticipated recommendations** that the Q2
dysfunctions should surface, and the Q3 artifacts authored to answer each one. These are derived
from the seeded Q2 signals (see `../ground_truth.json`), not from a score.

| Dimension | Q2 dysfunction seeded (what the tool should surface) | Anticipated recommendation | Q3 artifacts that enact it |
|---|---|---|---|
| **Trust** | Ben conceals a broken check for 4 days (PR #41) | Make mistakes safe; blameless notes; celebrate the andon cord | AUR-12; `2026-07-10_blameless-practice`; PR #115; `#incidents 2026-08-04` |
| **Conflict** | Dana 56–66% airtime; Mark's hallway objection | Dissent in the room before decisions; balance airtime | AUR-13; `2026-07-17_facilitation-format`; `2026-07-14_beta-arch-review` |
| **Commitment** | License decision reopened 3× without new info | Close decisions with a written reopening bar | AUR-18; `2026-08-25_decision-hygiene`; `wiki/adr/0003` |
| **Accountability** | Tomás a security SPOF; late upward surfacing | Horizontal peer feedback; remove single points of failure | AUR-16; `2026-07-24_reviewer-onboarding` |
| **Results** | Dana optimizes for fundraiser optics over sequencing | Shared outcome over individual optics | `2026-08-11_outcome-over-optics`; `2026-09-15_q3-retro` |

## How to produce the actual scored assessment

Run the tool over each quarter; it emits the scores/recommendations/trend:

```
team-assess --input ../before-q2-2026 --period Q2-2026
team-assess --input ../after-q3-2026  --period Q3-2026 --compare Q2-2026
```

The dataset's job is to make those runs meaningful: the Q2 dysfunctions are seeded and located in
`../ground_truth.json`, mapped to rubric v0.9 facets in `five-dysfunctions-signal-map.json`, and the
Q3 content is authored to respond to the anticipated recommendations above — so a correct tool
should score Q3 higher than Q2 on exactly the targeted dimensions.
