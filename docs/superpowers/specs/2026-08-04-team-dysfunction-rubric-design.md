# Team Dysfunction Assessment Tool — Design Spec

**Date:** 2026-08-04  
**Version:** 0.9 (OBM behavior codebook merged into the rubric)  
**Status:** Approved

---

## Overview

`team-assess` is a Python CLI tool that periodically evaluates team health using the Five Dysfunctions of a Team framework (Lencioni). It ingests heterogeneous team artifacts, scores each dysfunction dimension via Claude, persists snapshots, and produces a before/after trend report with prioritized action recommendations for the team.

The rubric slot reserved for an additional academic framework is now filled: `rubric/obm-behavior-codes.md` holds 120 observable behavior codes, grouped by dimension and behavior cluster, and `rubric/obm-behavior-codes.json` is the generated form the scoring prompt loads.

---

## Architecture

### Approach

LLM-as-Scorer (Option A): all input documents are fed to Claude with a structured scoring prompt. Claude returns scored dimensions, evidence, and recommendations as JSON. A separate rendering layer produces the human-readable report.

Option C (structured extraction + rubric scoring layer) is reserved as a future upgrade path when the rubric matures.

### Directory Structure

```
team-assess/
├── assess.py          # CLI entrypoint
├── ingestion/         # file readers per type (txt, md, pdf, csv, json)
├── prompts/           # scoring prompt templates
├── rubric/            # Five Dysfunctions definitions + scoring criteria
├── snapshots/         # persisted JSON runs (one file per period label)
├── output/            # generated reports
└── config.toml        # API key, model, output format preferences
```

### Data Flow

```
input directory
    → ingest (read all supported files)
    → concatenate / chunk content
    → score via Claude API (structured JSON response)
    → save snapshot (snapshots/<period>.json)
    → diff against prior snapshot if present
    → render report (output/report-<period>.md)
```

### Supported Input Formats

Any mix of: plain text, Markdown, PDF, CSV, JSON. Additional formats added via ingestion module.

---

## Rubric: Five Dysfunctions

Scored on a **1–5 scale** (1 = severe dysfunction, 5 = fully healthy).

| # | Dysfunction | Healthy signals |
|---|---|---|
| 1 | Absence of Trust | Vulnerability, admitting mistakes, asking for help |
| 2 | Fear of Conflict | Direct debate, voicing disagreement, challenging ideas openly |
| 3 | Lack of Commitment | Clear decisions, follow-through, alignment after debate |
| 4 | Avoidance of Accountability | Peer feedback, calling out missed commitments |
| 5 | Inattention to Results | Focus on shared team goals over individual recognition |

The pyramid structure is respected: lower-layer dysfunctions are weighted in interpretation (poor trust undermines all layers above it).

For each dimension, Claude provides:
- A score (1–5)
- Confidence level (low / medium / high) based on signal volume in inputs
- 2–4 evidence items: direct quotes or behavioral observations from input documents, each tagged with the behavior code it matches

### Behavior codebook

`rubric/obm-behavior-codes.md` is the canonical source; `build_codes.py` regenerates `obm-behavior-codes.json` from it. Editing the JSON directly is a bug.

| Dimension | Codes | Clusters |
|---|---|---|
| Trust | 25 | 5 |
| Conflict | 24 | 6 |
| Commitment | 23 | 5 |
| Accountability | 21 | 5 |
| Results | 27 | 6 |

Each code carries a stable id (`TRU-01-P1`), its dimension, its behavior cluster, a valence (`positive` raises the dimension, `negative` lowers it), and the behavior text. Ids are stable across text edits, so a snapshot taken today stays comparable after the wording is sharpened.

Three rules bind the scorer to the codebook:

1. **Every evidence item cites a code id.** An observation that matches no code is not evidence; it is a candidate new code, reported separately under `uncoded` rather than folded silently into a score.
2. **Codes are markable from the record, not inferred from mood.** The behavior must be present in what was said or done. This is what keeps two runs over the same inputs from disagreeing.
3. **Cluster spread constrains confidence.** A dimension whose marks all land in one cluster is `low` confidence regardless of how many marks there are, because one cluster is one behavior pattern, not a dimension.

Scores follow from the marked balance: the positive and negative counts per dimension, weighted by cluster spread, rather than from an unanchored 1–5 judgment. Negative codes are not merely absent positives, so a dimension can hold both and score mid-range with high confidence.

Coding is team-level. Marks retain `speaker_id` in storage so counts can be recomputed, and it is stripped before anything reaches a report, per the scorer constraint in `2026-08-04-facilitator-and-scorer-integration.md`.

---

## Snapshot Schema

One JSON file per period, saved to `snapshots/<period-label>.json`:

```json
{
  "period": "Q1-2025",
  "run_date": "2026-08-04",
  "input_files": ["meeting-notes.md", "retro.txt"],
  "dimensions": {
    "trust": {
      "score": 3.0,
      "confidence": "medium",
      "marks": { "positive": 7, "negative": 3, "clusters": 4 },
      "evidence": [
        {
          "code": "TRU-01-P1",
          "valence": "positive",
          "quote": "I got the migration order wrong, that one's on me.",
          "source": "2026-06-09_roadmap-review.vtt",
          "speaker_id": "stripped-before-report"
        }
      ],
      "uncoded": ["Observation that matched no code..."]
    },
    "conflict": { "score": 2.5, "confidence": "high", "evidence": [...] },
    "commitment": { "score": 3.2, "confidence": "medium", "evidence": [...] },
    "accountability": { "score": 2.1, "confidence": "low", "evidence": [...] },
    "results": { "score": 3.4, "confidence": "medium", "evidence": [...] }
  },
  "overall_health": 2.84,   // mean of all 5 dimension scores
  "recommendations": [
    "Action recommendation 1...",
    "Action recommendation 2..."
  ]
}
```

---

## Trend Analysis

When two snapshots exist, the tool computes a before/after diff:

- Score delta per dimension (e.g., +0.8, -0.3)
- Direction label: improving / declining / stable (threshold: ±0.2)
- Warning flag if any dimension moves more than 1.0 point
- Overall health delta

Trend data is included in both the JSON snapshot and the rendered report.

---

## Output

Each run produces:
- `snapshots/<period>.json` — persisted for trend diffs and future Option C migration
- `output/report-<period>.md` — human-readable narrative for the team

### `output/report-<period>.md` — Human-readable narrative

```
# Team Health Assessment — Q2-2025
Overall Health: 3.1 / 5  (↑ from 2.8 in Q1-2025)

## Dimension Scores
Trust            ████░░  3.4  ↑ +0.8
Conflict         ███░░░  2.9  ↑ +0.4
Commitment       ███░░░  3.0  →  0.0
Accountability   ██░░░░  2.1  ↓ -0.3  ⚠
Results          ████░░  3.2  ↑ +0.2

## Priority Actions
1. [Accountability] — Specific recommendation...
2. [Conflict] — Specific recommendation...

## Evidence Highlights
### Trust
- "Quote from meeting notes..."
```

Dimensions are listed highest-dysfunction-first in the Priority Actions section.

### `snapshots/<period>.json` — Machine-readable record for future diffs and Option C migration

---

## CLI Interface

```
team-assess --input ./data/q1 --period Q1-2025
team-assess --input ./data/q2 --period Q2-2025 --compare Q1-2025
```

Options:
- `--input` — directory of input files
- `--period` — label for this snapshot (used in filenames and reports)
- `--compare` — period label to diff against (optional)
- `--output` — output directory (default: `./output`)
- `--config` — path to config.toml (default: `./config.toml`)

---

## Configuration (`config.toml`)

```toml
[claude]
model = "claude-sonnet-5"
api_key_env = "ANTHROPIC_API_KEY"

[output]
format = "markdown"   # future: html, json-only

[rubric]
framework = "five-dysfunctions"   # extensible for additional frameworks
codebook = "rubric/obm-behavior-codes.json"
```

---

## Future Extensions

- **Option C upgrade**: Introduce structured extraction layer — LLM tags evidence to dimensions, separate scorer applies rubric to tagged evidence. Enables auditability and easier rubric extension.
- **Additional frameworks**: `rubric/` holds multiple framework definitions; the OBM codebook is the first, and `[rubric] framework` selects among them.
- **Codebook growth**: `uncoded` observations accumulated across runs are the input to a review that promotes recurring ones to new codes. Adding a code never renumbers existing ids.
- **Multiple audience views**: Same snapshot data rendered differently for team vs. manager vs. coach audiences.
- **HTML/PDF output**: Additional renderers added to output layer without changing core pipeline.
