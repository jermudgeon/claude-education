# Spec: Tiered Literature-Review Pipeline
### (as executed to build the OBM Behavior Taxonomy, 2026-08-05)

This documents the process actually used to go from an open research question to a finished, filtered, condensed deliverable — so it can be reused on a different topic or audited for how conclusions were reached.

---

## 1. Origin

This pipeline is an ad hoc adaptation of a pre-existing 3-tier opportunity-research pipeline (intake → fitness gate → Tier1 recon → Tier2 investigation → Tier3 synthesis) built for a different purpose (job-opportunity research). The tier/gate/checkpoint *mechanics* were reused; the *content* and *prompts* were built fresh for an academic literature review. No fitness-gate or intake-scraper equivalent applied — this run started directly from a research question the user posed in conversation.

## 2. Roles

- **Orchestrator (O1)** — builds each stage's prompt, launches the stage as a sub-agent, reads the stage's output file (or delegates that read to a Haiku sub-agent when the file is pure research content), applies gate logic, and surfaces a brief to the user for redirection before the next stage launches. The orchestrator does not do primary research or write taxonomy content itself.
- **Stage agents** — one per tier, launched via the Agent tool, each given a self-contained prompt with no memory of prior stages except what's explicitly read from the prior stage's output file.

**Model assignment logic** (escalate only where interpretation is needed, per standing project convention):
| Stage | Model | Why |
|---|---|---|
| Tier 1 (recon) | Sonnet | Needs judgment to identify credible frameworks and rate their rigor, not pure lookup |
| Tier 2 (investigation) | Sonnet | Needs judgment to reconcile sources, apply an operator-directed structure, flag misfits honestly |
| Tier 3 (synthesis) | Opus | Highest-stakes consolidation step; final deliverable quality matters most here |
| Gate-brief extraction | Haiku | Pure extraction of named sections from an already-written file — no interpretation required |
| Post-deliverable revision passes | Sonnet | Requires judgment (reliability assessment, intervention design) but not full synthesis |
| Condensation/reformatting pass | Sonnet | Filtering + dense reformatting, moderate judgment on format density |

## 3. Stage-by-Stage Sequence

### Stage 0 — Scope Setup
Before any research launched, the orchestrator asked the user three questions (via structured choice, not open-ended): output location, research depth (single-pass vs. tiered), and target deliverable format. This fixed the shape of everything downstream before spending any research budget.

### Stage 1 — Tier 1: Broad Reconnaissance
**Model:** Sonnet. **Goal:** survey the landscape broadly — cast a wide net across named, credible frameworks in the target domain.
**Output:** `research/TIER1_RESULTS.md`, with a fixed 5-section structure: Source Catalog, Landscape Overview, Working Hypothesis, Tier 2 Investigation Priorities, Gaps and Unknowns.
**Discipline:** work in batches of 3-5 fetches, write incrementally; hard stop at 25 fetches with a literal checkpoint marker as the file's last line if not finished, else a literal completion marker. This bounds runaway research and gives the orchestrator a deterministic way to detect "did this finish or hit a wall" without re-reading the whole file.

### Gate 1 (between Tier 1 and Tier 2)
The orchestrator delegated a Haiku sub-agent to extract (verbatim, no interpretation) the Working Hypothesis, Tier 2 Priorities, Gaps, and the framework name list from Tier 1's output. This extract — not the raw file — was shown to the user, who was asked for corrections or redirection before Tier 2 launched.

**What the user's redirection produced:** an explicit **Operator Directive** — "organize by behavior content, not process timing; align as closely as possible to Lencioni's Five Dysfunctions" — which was injected **verbatim, as its own labeled section, at the top of the Tier 2 prompt**, with instructions that it overrides any conflicting suggestion from Tier 1. This is the mechanism by which user judgment steers the pipeline without the orchestrator re-deriving or paraphrasing that judgment itself.

### Stage 2 — Tier 2: Deep Investigation
**Model:** Sonnet. **Goal:** verify Tier 1's leads against primary sources where possible, apply the Operator Directive's structure, and honestly separate what fits the imposed structure from what doesn't.
**Output:** `research/TIER2_RESULTS.md`, structured as: Verified Behavior Inventory (organized by the operator-directed structure, not the raw Tier 1 categories), Misfits and Cross-Cutting Material, Hypothesis Status (one row per Tier 1 priority, explicitly marked resolved/partial/open), New Findings, Tier 3 Synthesis Priorities.
**Confidence convention applied throughout:** every claim tagged CONFIRMED (primary-source verified) / LIKELY (secondary source only) / UNRESOLVED (conflicting or unverifiable) — carried forward from a standing project convention, not invented for this run.
**Checkpoint hit:** Tier 2 reached the 25-fetch limit before finishing (systematic paywall/binary-PDF blocks on several primary sources, not a lack of effort) and stopped per its write discipline, ending the file with the checkpoint marker.

### Gate 2 (checkpoint decision + pre-Tier-3 gate, combined)
Because Tier 2 stopped at a checkpoint rather than finishing cleanly, the orchestrator again delegated a Haiku extraction (last line, Hypothesis Status, Tier 3 Priorities, Misfits section) and presented it to the user with two decisions bundled: (a) continue chasing the unresolved items or proceed to synthesis with what exists, and (b) a substantive open design question the research itself had surfaced (whether to add a leader/peer cross-cutting tag). Both answers became a second **Operator Directive**, injected at the very top of the Tier 3 prompt as "Pre-Synthesis Operator Corrections" — the placement-at-top convention is deliberate, so the synthesis agent resolves them before composing anything rather than bolting them on after.

### Stage 3 — Tier 3: Synthesis
**Model:** Opus. **Goal:** consolidate Tier 1 + Tier 2 + both Operator Directives into one coherent, non-specialist-readable final deliverable — not redo the research.
**Output:** `OBM_Behavior_Taxonomy.md` — the first true deliverable (previous stages produced working files, not outputs meant for end use). Structured as: Purpose & How to Use, Five Pillars (each with sub-dimensions and tagged behavior entries), Cross-Cutting Coding Guidance, Excluded/Out-of-Scope (with reasons), Source Bibliography.
**Judgment calls made at this stage were logged inline and indexed in an appendix**, rather than silently resolved — e.g., collapsing duplicate cross-framework entries, splitting ambiguous constructs between pillars. This keeps the synthesis auditable.
**Two safety rules were added by the synthesis agent beyond the brief** (absence-behaviors require a demonstrated occasion, not inferred from low participation; tone/gesture-dependent items flagged for exclusion on text-only transcripts) — these emerged from the agent reasoning about the deliverable's actual use case (transcript coding), not from an explicit instruction. This is noted here because it's a case of a stage agent extending scope in a way that turned out to be load-bearing for the final revision pass (Stage 4a below) — worth watching for in future runs, since it's not guaranteed to happen.

### Acceptance Checkpoint
The finished Tier 3 output was summarized (not dumped in full) back to the user, with an explicit question of whether to accept it as final or request changes — mirroring the base pipeline's requirement that synthesis isn't "done" until the user has actually seen and responded to it, not just until the agent returns.

### Stage 4 — Post-Deliverable Revision Passes
Two further passes were run as **separate, narrowly-scoped agent invocations against the finished deliverable**, rather than being folded back into Tier 3 or re-triggering the whole pipeline:

**4a — Reliability flagging.** Prompted by a user exploratory question ("what happens if we limit findings to X") that was answered narratively first (2-3 sentence tradeoff, no action taken) before the user converted it into an actual instruction. The resulting pass: read the finished taxonomy, evaluate all 182 entries against a stated reliability standard, flag (not delete) unreliable ones in place with a reason and a concrete suggested intervention, and add a summary section. This is an *annotation* pass — structure preserved, nothing removed.

**4b — Condensation.** A pure filter-and-reformat pass: given explicit answers to three clarifying questions (which entries, how much per-entry detail, what the artifact is for), drop the flagged 62 entries entirely and reformat the remaining 120 into a dense, citation-free, page-budget-constrained working reference. No new judgment about behavior content — only judgment about density/legibility trade-offs within a fixed word budget.

## 4. Cross-Cutting Conventions

- **Orchestrator read-delegation.** The orchestrator itself never read a content-bearing research/output file directly — every read of TIER1_RESULTS.md / TIER2_RESULTS.md was delegated to a Haiku sub-agent with an explicit, narrow extraction spec (exact section names, "verbatim, no commentary"). This kept the orchestrator's own context clean and made each gate-brief cheap and fast. Stage agents, by contrast, *do* read prior-stage files directly — the delegation rule applies to orchestration, not to the actual research/synthesis work.
- **Operator Directives as verbatim, positioned injections.** User redirections were never paraphrased into the next agent's brief — they were quoted/restated as their own labeled section and placed either immediately after context (Tier 2) or at the very top, before all else (Tier 3), depending on how load-bearing the correction was for everything that followed.
- **Write discipline / 25-fetch checkpoint.** Any stage doing open-ended web research works in small batches, writes incrementally (so partial progress survives an interruption), and self-stops at a fixed fetch budget with a literal, greppable marker string as the file's last line. This makes "did it finish" a cheap deterministic check rather than something that requires reading and judging the whole file.
- **Confidence tagging.** CONFIRMED / LIKELY / UNRESOLVED applied to every substantive claim from Tier 2 onward, carried through into the final deliverable rather than laundered into unqualified statements.
- **Exploratory questions answered narratively before being executed.** When the user asked a "what happens if" question, it got a short recommendation-plus-tradeoff answer with no file changes — only once the user turned it into an explicit instruction did an agent get launched to act on it.
- **Revisions as scoped, additive passes.** Once a deliverable existed, further changes were separate narrow agent runs against that specific file, not full pipeline re-runs — each with its own tight brief (what to preserve, what to change, what "done" means for that pass alone).

## 5. File Manifest

| File | Produced by | Role |
|---|---|---|
| `research/TIER1_RESULTS.md` | Tier 1 (Sonnet) | Working file — source catalog, draft hypothesis |
| `research/TIER2_RESULTS.md` | Tier 2 (Sonnet) | Working file — verified/structured behavior inventory |
| `OBM_Behavior_Taxonomy.md` | Tier 3 (Opus) | Deliverable — full annotated taxonomy, 182 entries |
| `OBM_Behavior_Taxonomy.md` (revised) | Stage 4a (Sonnet) | Same file, in-place revision — 62 entries flagged with reliability notes + interventions |
| `OBM_Behavior_Taxonomy_Coding_Reference.md` | Stage 4b (Sonnet) | Deliverable — condensed 120-entry, ~3-page working coding sheet |
| `Pipeline_Spec.md` | Orchestrator (direct write) | This document |

## 6. Reusable Template (for applying this to a new topic)

1. Fix scope with the user first (location, depth, deliverable format) — cheap, prevents wasted research.
2. Tier 1 (Sonnet): broad survey, fixed output structure, 25-fetch discipline, ends in a working hypothesis + priorities + gaps.
3. Gate: Haiku-extracted brief → user redirection → verbatim Operator Directive into Tier 2's brief.
4. Tier 2 (Sonnet): deepen/verify against the operator-directed structure, tag confidence, honestly flag misfits, same fetch discipline.
5. Checkpoint/gate: if fetch-limited, decide continue-vs-proceed; combine with any further operator corrections; inject verbatim at the top of Tier 3's brief.
6. Tier 3 (Opus): consolidate into one coherent, audience-appropriate deliverable; log judgment calls rather than silently resolving them.
7. Acceptance checkpoint with the user — explicit accept/revise, not assumed.
8. Further changes: scoped, additive, narrowly-briefed passes against the finished file — annotate before you delete, filter/condense only once the annotated version exists.
