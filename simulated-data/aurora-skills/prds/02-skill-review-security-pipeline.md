# PRD 02 — Skill Review & Security Pipeline

- **Owner:** Tomás Reyes (Platform / Security)
- **Status:** In build (escalated P0 after incident 2026-05-04)
- **Related:** Incident #INC-2026-05-04, retro 2026-05-05, ADR-0002, Issue AUR-5

## Problem

Curation is the product (ADR-0001), which means the **review pass is the product**. Two threats
made this concrete in the same week:

1. **External ecosystem risk.** Auditing ecosystems we considered federating with, Tomás
   reproduced a published skill that exfiltrates environment variables on install. This matches
   the Feb 2026 Snyk finding (36% flawed, 76 malicious payloads).
2. **Internal regression.** A validator change (PR #41, 2026-04-30, described only as "small fix,
   nothing major") disabled a capability check to make a test pass. It took four days to surface
   — not because it was hard to find, but because it felt unsafe to admit (see ways-of-working.md,
   the andon-cord norm).

## Goals

- Automated scan on submission: capability diff, static analysis, known-malicious signatures.
- **Mandatory human review pass** for any skill requesting `tk.reference` or a new data source.
- A regression test that **fails loudly if any capability check is disabled** (added in PR #77
  after the incident). Never again silently.
- Blameless incident notes on every incident (AUR-12); pulling the cord early is celebrated.

## Metrics

- Time-to-surface for a safety regression (incident baseline: **4 days** → target: same-day).
- % of TK-referencing skills that pass through community review before publish (target: 100%).
- Reviewer bus factor (**currently 1 — Tomás**; target ≥ 2, tracked in AUR-5).

## Non-goals

- Blocking all risk. The goal is a bounded, auditable surface (ADR-0002), not zero skills.

## Open questions

- Second reviewer: hire vs. train — **UNKNOWN** (owner decision pending).
