# Decision Log — Aurora Skills

Index of Architecture Decision Records. Full records in `wiki/adr/`.

| ADR | Decision | Status | Opened | Settled | Reopens |
|---|---|---|---|---|---|
| [0001](adr/0001-curate-not-federate.md) | Curate, don't federate | Accepted | 2026-04-07 | 2026-04-07 | 0 |
| [0002](adr/0002-no-arbitrary-egress.md) | No arbitrary network egress | Accepted | 2026-04-14 | 2026-04-14 | 0 |
| [0003](adr/0003-tk-license-and-labels.md) | TK license + Local Contexts labels | Accepted | 2026-04-21 | 2026-06-23 | **3** |
| [0004](adr/0004-joint-provenance-schema.md) | One joint provenance schema | Accepted | 2026-05-07 | 2026-05-15 | 0 |

## Note on ADR-0003

ADR-0003 is the outlier: it took **two months and three sessions** to settle, and reopened three
times. This is deliberate signal in the dataset — a decision that was *suppressed rather than
settled* until it was consciously closed on 2026-06-23 with a written reopening bar. Every other
decision closed in the session it was made (dissent arrived before the decision — see ADR-0002).

The contrast between ADR-0002 (dissent before decision, closed same day) and ADR-0003 (dissent in
the hallway, reopened 3×) is the clearest in-repo illustration of the collaboration signals the
insights tool (PRD 05) is built to detect.
