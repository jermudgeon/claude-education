# PRD 06 — Classroom / Group Agent Facilitator

- **Owner:** Sarah Kowalski (Governance), with Platform
- **Status:** Concept (the one genuinely unsolved piece)
- **Related:** PRD 05 (collaboration insights), kickoff 2026-04-07

## Problem

Every existing skill tool assumes a **1:1** relationship — one human, one agent. A classroom is
not 1:1. It is one agent facilitating a **group of voices** working toward a shared goal. Skill
distribution is already solved (it's a git repo); general registries exist. The market scan in
the brainstorm found the same gap: *"one agent facilitating a group of voices toward a shared
goal — only research prototypes exist (CHI 2026), no product."* This is the differentiator.

## What it does

- **Reframes to a shared understanding.** "Let me say that back so we both understand" — because
  "a box with three stripes" looks different in every head. The agent maintains a shared model of
  the goal and surfaces divergence.
- **Balances voices.** Notices who hasn't spoken and invites them (the facilitator nudge from
  PRD 05), without turning participation into a score.
- **Acts as a source, not an answer.** Like the Socratic course the team admired: it points to
  where to go and asks the question that expands context, rather than handing over the answer.
- **Encourages antithetical thinking.** "I think blue is best; someone else sees red." It draws
  out the opposing view deliberately, because AI tuned for engagement will otherwise smooth
  conflict away — and this team decided conflict, done well, is the point.

## Design tension (open)

AI is optimized for **engagement**; this tool must sometimes do the **opposite** — slow the group
down, introduce friction, make people rely on each other rather than on it. Reconciling "helpful"
with "gets out of the way" is the core unsolved design problem. **UNKNOWN:** how to measure
whether the agent is reading the group correctly vs. confidently wrong (the "confidently wrong"
failure mode named repeatedly in the brainstorm).

## Relationship to PRD 05

PRD 05 (insights) *measures* collaboration after the fact and nudges live. PRD 06 *participates*
in the collaboration as a facilitator. 05 is the mirror; 06 is the extra chair at the table.
06 depends on 05's metric contract to know when to intervene.

## Non-goals

- Replacing the teacher or the team lead. It facilitates; humans decide.
- Grading students or ranking contributors.
