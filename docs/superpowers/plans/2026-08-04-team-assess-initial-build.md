# Team Assess — Initial Build Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI (`team-assess`) that ingests heterogeneous team artifacts, scores them against an externalized Five Dysfunctions rubric via Claude, persists snapshots, and renders a before/after trend report in Markdown.

**Architecture:** The rubric lives as a YAML file (`rubric/five-dysfunctions.yaml`) loaded at runtime — not embedded in code or prompts. A prompt builder reads the rubric and constructs the Claude scoring request. Claude returns structured JSON via tool use, which is saved as a snapshot and optionally diffed against a prior period's snapshot before rendering.

**Tech Stack:** Python 3.11+, `anthropic` SDK, `pyyaml`, `pypdf`, `tomllib` (stdlib), `pytest`, `argparse` (stdlib)

---

## File Map

| File | Responsibility |
|---|---|
| `team-assess/assess.py` | CLI entrypoint — wires all modules together |
| `team-assess/config.py` | Loads and validates `config.toml` |
| `team-assess/config.toml` | User configuration (model, API key env var, paths) |
| `team-assess/rubric/five-dysfunctions.yaml` | Externalized rubric: dimensions, signals, scoring guidance |
| `team-assess/rubric/loader.py` | Loads and validates rubric YAML into a typed dict |
| `team-assess/ingestion/readers.py` | Per-format file readers: txt, md, csv, json, pdf |
| `team-assess/ingestion/scanner.py` | Scans an input directory, dispatches to readers, returns labelled content |
| `team-assess/prompts/builder.py` | Builds the Claude scoring prompt from rubric + content |
| `team-assess/scorer/claude_scorer.py` | Calls Claude API via tool use, parses response into snapshot dict |
| `team-assess/snapshots/store.py` | Saves and loads snapshot JSON files |
| `team-assess/trend/diff.py` | Computes before/after diff between two snapshots |
| `team-assess/renderer/markdown.py` | Renders snapshot (+ optional trend) to Markdown report |
| `team-assess/tests/test_rubric.py` | Tests for rubric loader |
| `team-assess/tests/test_readers.py` | Tests for ingestion readers |
| `team-assess/tests/test_scanner.py` | Tests for directory scanner |
| `team-assess/tests/test_builder.py` | Tests for prompt builder |
| `team-assess/tests/test_scorer.py` | Tests for Claude scorer (mocked API) |
| `team-assess/tests/test_store.py` | Tests for snapshot store |
| `team-assess/tests/test_diff.py` | Tests for trend diff |
| `team-assess/tests/test_renderer.py` | Tests for Markdown renderer |
| `team-assess/tests/fixtures/` | Sample input files and rubric for tests |

---

## Task 1: Project Scaffold

**Files:**
- Create: `team-assess/requirements.txt`
- Create: `team-assess/pyproject.toml`
- Create: `team-assess/pytest.ini`
- Create: `team-assess/tests/__init__.py`
- Create: `team-assess/tests/fixtures/.gitkeep`

- [ ] **Step 1: Create directory structure**

```bash
cd /Users/jhaustin/Code/Idealoft/claude-education
mkdir -p team-assess/{ingestion,prompts,rubric,scorer,snapshots,trend,renderer,output,tests/fixtures}
touch team-assess/tests/__init__.py team-assess/tests/fixtures/.gitkeep
touch team-assess/{ingestion,prompts,scorer,trend,renderer}/__init__.py
```

- [ ] **Step 2: Write `requirements.txt`**

```
anthropic>=0.34.0
pyyaml>=6.0
pypdf>=4.0
pytest>=8.0
pytest-mock>=3.14
```

- [ ] **Step 3: Write `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "team-assess"
version = "0.8.0"
requires-python = ">=3.11"
dependencies = [
    "anthropic>=0.34.0",
    "pyyaml>=6.0",
    "pypdf>=4.0",
]

[project.scripts]
team-assess = "assess:main"
```

- [ ] **Step 4: Write `pytest.ini`**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

- [ ] **Step 5: Install dependencies**

```bash
cd team-assess && pip install -r requirements.txt
```

Expected: no errors, packages installed.

- [ ] **Step 6: Verify pytest runs (empty suite)**

```bash
cd team-assess && pytest -v
```

Expected: `no tests ran`

- [ ] **Step 7: Commit**

```bash
git add team-assess/
git commit -m "chore: scaffold team-assess project"
```

---

## Task 2: Externalized Rubric

**Files:**
- Create: `team-assess/rubric/five-dysfunctions.yaml`
- Create: `team-assess/rubric/__init__.py`
- Create: `team-assess/rubric/loader.py`
- Create: `team-assess/tests/test_rubric.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_rubric.py
import pytest
from rubric.loader import load_rubric, RubricError

def test_load_rubric_returns_five_dimensions():
    rubric = load_rubric("rubric/five-dysfunctions.yaml")
    assert set(rubric["dimensions"].keys()) == {
        "trust", "conflict", "commitment", "accountability", "results"
    }

def test_each_dimension_has_required_fields():
    rubric = load_rubric("rubric/five-dysfunctions.yaml")
    for key, dim in rubric["dimensions"].items():
        assert "name" in dim, f"dimension {key} missing 'name'"
        assert "order" in dim, f"dimension {key} missing 'order'"
        assert "healthy_signals" in dim, f"dimension {key} missing 'healthy_signals'"
        assert "dysfunction_signals" in dim, f"dimension {key} missing 'dysfunction_signals'"
        assert "scoring_guidance" in dim, f"dimension {key} missing 'scoring_guidance'"
        assert len(dim["healthy_signals"]) >= 2
        assert len(dim["dysfunction_signals"]) >= 2

def test_dimensions_ordered_1_through_5():
    rubric = load_rubric("rubric/five-dysfunctions.yaml")
    orders = sorted(dim["order"] for dim in rubric["dimensions"].values())
    assert orders == [1, 2, 3, 4, 5]

def test_missing_file_raises_rubric_error():
    with pytest.raises(RubricError):
        load_rubric("rubric/nonexistent.yaml")
```

- [ ] **Step 2: Run test — verify it fails**

```bash
cd team-assess && pytest tests/test_rubric.py -v
```

Expected: `ModuleNotFoundError: No module named 'rubric'`

- [ ] **Step 3: Write `rubric/five-dysfunctions.yaml`**

```yaml
framework: five-dysfunctions
version: "0.8"
description: "Lencioni's Five Dysfunctions of a Team"

dimensions:
  trust:
    name: "Absence of Trust"
    order: 1
    description: >
      Team members are unwilling to be vulnerable with one another.
      Without trust, no other healthy team behavior is possible.
    healthy_signals:
      - "Admitting mistakes, weaknesses, or gaps in knowledge"
      - "Asking teammates for help without defensiveness"
      - "Giving colleagues benefit of the doubt"
      - "Taking risks and showing vulnerability in group settings"
      - "Acknowledging uncertainty or areas of personal limitation"
    dysfunction_signals:
      - "Concealing mistakes or covering up failures"
      - "Reluctance to ask for help; struggling alone"
      - "Jumping to negative conclusions about colleagues' motives"
      - "Defensive or guarded communication patterns"
      - "Avoiding or dreading one-on-ones and feedback conversations"
    scoring_guidance: |
      Score 1-2: Clear guardedness, blame-orientation, or cover-up behavior present.
        Members do not admit mistakes. Asking for help is rare or absent.
      Score 3: Mixed signals — some vulnerability present but also visible guardedness.
        Trust exists in pockets but is not team-wide.
      Score 4-5: Team openly admits mistakes, asks for help freely, gives benefit
        of the doubt as default. Vulnerability is normalized.

  conflict:
    name: "Fear of Conflict"
    order: 2
    description: >
      Team avoids direct, unfiltered debate of ideas. Without healthy conflict,
      commitment suffers because buy-in never forms through genuine debate.
    healthy_signals:
      - "Direct disagreement expressed openly in meetings"
      - "Ideas challenged on merit without personal attack"
      - "Team debates and then reaches clear resolution"
      - "Minority positions voiced and heard before decisions"
      - "Conflict is visible and resolved, not suppressed"
    dysfunction_signals:
      - "Meetings end in artificial harmony with no real debate"
      - "Disagreements surface in side conversations, not the room"
      - "Personal criticism substitutes for idea debate"
      - "Issues go unresolved and resurface repeatedly"
      - "Team avoids sensitive topics; walking on eggshells"
    scoring_guidance: |
      Score 1-2: Conflict is avoided or political. Real disagreements suppressed.
        Decisions made without genuine buy-in debate.
      Score 3: Some debate occurs but often incomplete; important topics sometimes skirted.
      Score 4-5: Team engages in direct, passionate debate of ideas. Conflict is
        productive and resolved. Decisions emerge from genuine buy-in.

  commitment:
    name: "Lack of Commitment"
    order: 3
    description: >
      Without having had their say in genuine conflict, team members do not commit
      to decisions — even ones they publicly agree to.
    healthy_signals:
      - "Clear decisions made with explicit agreement"
      - "Follow-through on commitments without reminders"
      - "Alignment after debate, even when not everyone agreed initially"
      - "Deadlines and agreements treated as firm"
      - "Revisiting decisions is rare and requires new information"
    dysfunction_signals:
      - "Decisions relitigated repeatedly without new information"
      - "Ambiguity about what was actually decided"
      - "Stated agreement not followed by action"
      - "Dependencies missed because commitments were not clear"
      - "Frequent 'I thought we decided X' confusion"
    scoring_guidance: |
      Score 1-2: Decisions frequently revisited. Ambiguity about commitments is normal.
        Follow-through is unreliable; stated agreements often not enacted.
      Score 3: Commitment is inconsistent — clear on some things, fuzzy on others.
      Score 4-5: Team makes clear decisions and follows through. Alignment is genuine.
        Revisiting decisions is the exception, not the norm.

  accountability:
    name: "Avoidance of Accountability"
    order: 4
    description: >
      Without commitment, people do not hold peers accountable — they rationalize
      missed expectations as understandable given unclear agreements.
    healthy_signals:
      - "Team members call out missed commitments directly and promptly"
      - "Peer feedback given without escalating to management"
      - "High standards expected of all team members equally"
      - "Underperformance is addressed rather than worked around"
      - "Accountability is horizontal, not just top-down"
    dysfunction_signals:
      - "Poor performance or missed commitments tolerated without comment"
      - "Issues escalated to manager rather than addressed peer-to-peer"
      - "Resentment builds silently instead of being raised directly"
      - "Standards applied inconsistently across team members"
      - "People work around underperformers rather than addressing it"
    scoring_guidance: |
      Score 1-2: Accountability is absent or management-dependent. Peer feedback rare.
        Underperformance goes unaddressed; team works around problems.
      Score 3: Some peer accountability exists but inconsistently. Some issues surfaced,
        others silently tolerated.
      Score 4-5: Team holds each other accountable directly and promptly. Standards
        are high and applied equally. Feedback is normal, not an event.

  results:
    name: "Inattention to Results"
    order: 5
    description: >
      Without accountability, team members prioritize personal status, ego, or
      departmental concerns over collective team outcomes.
    healthy_signals:
      - "Decisions explicitly weighed against team goals"
      - "Individual recognition deferred to team achievement"
      - "Cross-functional help offered without being asked"
      - "Team outcome treated as the primary success metric"
      - "Members celebrate team wins, not just personal milestones"
    dysfunction_signals:
      - "Decisions optimized for individual or departmental benefit"
      - "Team goal discussions crowded out by status and visibility concerns"
      - "Reluctance to help other sub-teams or functions"
      - "Personal metrics prioritized over shared outcomes"
      - "Team wins attributed to individuals rather than collective effort"
    scoring_guidance: |
      Score 1-2: Individual or departmental interests dominate. Team outcome is nominal.
        Recognition, credit, and decisions skew heavily toward personal benefit.
      Score 3: Team outcomes matter but compete visibly with individual interests.
      Score 4-5: Team success is the clear primary metric. Members actively support
        each other and defer personal recognition to collective achievement.
```

- [ ] **Step 4: Write `rubric/__init__.py`**

```python
```

(empty)

- [ ] **Step 5: Write `rubric/loader.py`**

```python
from pathlib import Path
import yaml


class RubricError(Exception):
    pass


def load_rubric(path: str) -> dict:
    rubric_path = Path(path)
    if not rubric_path.exists():
        raise RubricError(f"Rubric file not found: {path}")
    try:
        with rubric_path.open() as f:
            rubric = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise RubricError(f"Invalid YAML in rubric file: {e}") from e

    _validate_rubric(rubric)
    return rubric


def _validate_rubric(rubric: dict) -> None:
    required_fields = ["name", "order", "healthy_signals", "dysfunction_signals", "scoring_guidance"]
    dimensions = rubric.get("dimensions", {})
    if not dimensions:
        raise RubricError("Rubric must define at least one dimension under 'dimensions'")
    for key, dim in dimensions.items():
        for field in required_fields:
            if field not in dim:
                raise RubricError(f"Dimension '{key}' is missing required field '{field}'")
```

- [ ] **Step 6: Run tests — verify they pass**

```bash
cd team-assess && pytest tests/test_rubric.py -v
```

Expected: 4 tests pass.

- [ ] **Step 7: Commit**

```bash
git add team-assess/rubric/ team-assess/tests/test_rubric.py
git commit -m "feat: externalize Five Dysfunctions rubric as YAML with loader"
```

---

## Task 3: Ingestion Readers

**Files:**
- Create: `team-assess/ingestion/readers.py`
- Create: `team-assess/tests/test_readers.py`
- Create: `team-assess/tests/fixtures/sample.txt`
- Create: `team-assess/tests/fixtures/sample.md`
- Create: `team-assess/tests/fixtures/sample.csv`
- Create: `team-assess/tests/fixtures/sample.json`

- [ ] **Step 1: Write fixture files**

`tests/fixtures/sample.txt`:
```
Team standup notes.
Alice admitted she was blocked and asked for help.
Bob disagreed with the approach but the team aligned after debate.
```

`tests/fixtures/sample.md`:
```markdown
# Retrospective Notes

## What went well
- Alice admitted she was struggling and the team stepped up.

## What could improve
- Decisions were relitigated twice this sprint.
```

`tests/fixtures/sample.csv`:
```
date,author,note
2025-01-10,Alice,"I should have flagged this blocker sooner"
2025-01-10,Bob,"We need to stop revisiting closed decisions"
```

`tests/fixtures/sample.json`:
```json
[
  {"type": "feedback", "author": "Alice", "text": "I should have flagged this blocker sooner"},
  {"type": "feedback", "author": "Bob", "text": "We need to stop revisiting closed decisions"}
]
```

- [ ] **Step 2: Write failing tests**

```python
# tests/test_readers.py
import pytest
from pathlib import Path
from ingestion.readers import read_txt, read_md, read_csv, read_json

FIXTURES = Path(__file__).parent / "fixtures"

def test_read_txt_returns_string():
    result = read_txt(FIXTURES / "sample.txt")
    assert "Alice admitted she was blocked" in result
    assert isinstance(result, str)

def test_read_md_returns_string():
    result = read_md(FIXTURES / "sample.md")
    assert "Retrospective Notes" in result
    assert isinstance(result, str)

def test_read_csv_returns_string_with_all_rows():
    result = read_csv(FIXTURES / "sample.csv")
    assert "Alice" in result
    assert "Bob" in result
    assert isinstance(result, str)

def test_read_json_returns_string():
    result = read_json(FIXTURES / "sample.json")
    assert "Alice" in result
    assert isinstance(result, str)

def test_read_txt_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        read_txt(FIXTURES / "nonexistent.txt")
```

- [ ] **Step 3: Run tests — verify they fail**

```bash
cd team-assess && pytest tests/test_readers.py -v
```

Expected: `ModuleNotFoundError: No module named 'ingestion.readers'`

- [ ] **Step 4: Write `ingestion/readers.py`**

```python
import csv
import json
from pathlib import Path


def read_txt(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def read_md(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def read_csv(path: Path) -> str:
    lines = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lines.append(" | ".join(f"{k}: {v}" for k, v in row.items()))
    return "\n".join(lines)


def read_json(path: Path) -> str:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return json.dumps(data, indent=2)
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
cd team-assess && pytest tests/test_readers.py -v
```

Expected: 5 tests pass.

- [ ] **Step 6: Commit**

```bash
git add team-assess/ingestion/ team-assess/tests/test_readers.py team-assess/tests/fixtures/
git commit -m "feat: ingestion readers for txt, md, csv, json"
```

---

## Task 4: PDF Reader

**Files:**
- Modify: `team-assess/ingestion/readers.py`
- Create: `team-assess/tests/fixtures/sample.pdf` (generated in test setup)
- Modify: `team-assess/tests/test_readers.py`

- [ ] **Step 1: Write failing test**

Add to `tests/test_readers.py`:

```python
from ingestion.readers import read_pdf

def test_read_pdf_returns_string(tmp_path):
    # Create a minimal PDF using pypdf's writer
    from pypdf import PdfWriter
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    pdf_path = tmp_path / "test.pdf"
    with open(pdf_path, "wb") as f:
        writer.write(f)
    # Blank PDF returns empty string (no text), not an error
    result = read_pdf(pdf_path)
    assert isinstance(result, str)

def test_read_pdf_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        read_pdf(FIXTURES / "nonexistent.pdf")
```

- [ ] **Step 2: Run test — verify it fails**

```bash
cd team-assess && pytest tests/test_readers.py::test_read_pdf_returns_string -v
```

Expected: `ImportError` or `AttributeError` — `read_pdf` not defined.

- [ ] **Step 3: Add PDF reader to `ingestion/readers.py`**

```python
def read_pdf(path: Path) -> str:
    from pypdf import PdfReader
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
cd team-assess && pytest tests/test_readers.py -v
```

Expected: all 7 tests pass.

- [ ] **Step 5: Commit**

```bash
git add team-assess/ingestion/readers.py team-assess/tests/test_readers.py
git commit -m "feat: add PDF reader to ingestion module"
```

---

## Task 5: Directory Scanner

**Files:**
- Create: `team-assess/ingestion/scanner.py`
- Create: `team-assess/tests/test_scanner.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_scanner.py
import pytest
from pathlib import Path
from ingestion.scanner import scan_directory, UnsupportedFormatError

FIXTURES = Path(__file__).parent / "fixtures"

def test_scan_returns_labelled_content(tmp_path):
    (tmp_path / "notes.txt").write_text("Team notes here", encoding="utf-8")
    (tmp_path / "retro.md").write_text("# Retro\nWent well.", encoding="utf-8")
    result = scan_directory(tmp_path)
    assert "notes.txt" in result
    assert "Team notes here" in result
    assert "retro.md" in result
    assert "Went well." in result

def test_scan_skips_unsupported_extensions(tmp_path):
    (tmp_path / "notes.txt").write_text("Valid content", encoding="utf-8")
    (tmp_path / "image.png").write_bytes(b"\x89PNG")
    result = scan_directory(tmp_path)
    assert "Valid content" in result
    assert "image.png" not in result

def test_scan_empty_directory_returns_empty_string(tmp_path):
    result = scan_directory(tmp_path)
    assert result == ""

def test_scan_raises_for_nonexistent_directory():
    with pytest.raises(NotADirectoryError):
        scan_directory(Path("/nonexistent/path"))
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd team-assess && pytest tests/test_scanner.py -v
```

Expected: `ModuleNotFoundError: No module named 'ingestion.scanner'`

- [ ] **Step 3: Write `ingestion/scanner.py`**

```python
from pathlib import Path
from ingestion.readers import read_txt, read_md, read_csv, read_json, read_pdf


class UnsupportedFormatError(Exception):
    pass


READERS = {
    ".txt": read_txt,
    ".md": read_md,
    ".csv": read_csv,
    ".json": read_json,
    ".pdf": read_pdf,
}


def scan_directory(directory: Path) -> str:
    directory = Path(directory)
    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    sections = []
    for file_path in sorted(directory.iterdir()):
        if not file_path.is_file():
            continue
        reader = READERS.get(file_path.suffix.lower())
        if reader is None:
            continue
        content = reader(file_path)
        if content.strip():
            sections.append(f"--- {file_path.name} ---\n{content}")

    return "\n\n".join(sections)
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
cd team-assess && pytest tests/test_scanner.py -v
```

Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add team-assess/ingestion/scanner.py team-assess/tests/test_scanner.py
git commit -m "feat: directory scanner dispatches to per-format readers"
```

---

## Task 6: Prompt Builder

**Files:**
- Create: `team-assess/prompts/builder.py`
- Create: `team-assess/tests/test_builder.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_builder.py
from prompts.builder import build_scoring_prompt

SAMPLE_RUBRIC = {
    "framework": "five-dysfunctions",
    "dimensions": {
        "trust": {
            "name": "Absence of Trust",
            "order": 1,
            "description": "Team members are unwilling to be vulnerable.",
            "healthy_signals": ["Admitting mistakes"],
            "dysfunction_signals": ["Concealing mistakes"],
            "scoring_guidance": "Score 1-2: guardedness. Score 4-5: open vulnerability.",
        },
    },
}

SAMPLE_CONTENT = "Alice admitted she was blocked and asked for help."


def test_prompt_contains_dimension_name():
    prompt = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "Absence of Trust" in prompt

def test_prompt_contains_healthy_signals():
    prompt = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "Admitting mistakes" in prompt

def test_prompt_contains_dysfunction_signals():
    prompt = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "Concealing mistakes" in prompt

def test_prompt_contains_team_content():
    prompt = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "Alice admitted she was blocked" in prompt

def test_prompt_contains_scoring_guidance():
    prompt = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "Score 1-2" in prompt
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd team-assess && pytest tests/test_builder.py -v
```

Expected: `ModuleNotFoundError: No module named 'prompts.builder'`

- [ ] **Step 3: Write `prompts/builder.py`**

```python
def build_scoring_prompt(rubric: dict, content: str) -> str:
    dimensions_text = _format_dimensions(rubric["dimensions"])
    return f"""You are an expert team coach assessing team health using the {rubric.get("framework", "Five Dysfunctions")} framework.

Below are the dimensions to score, followed by team artifacts to analyze.

## Scoring Dimensions

{dimensions_text}

## Team Artifacts

{content}

## Instructions

Analyze the team artifacts above and score each dimension on a scale of 1 to 5:
- 1 = severe dysfunction clearly present
- 3 = mixed signals, some healthy and some dysfunctional behavior
- 5 = healthy team behavior strongly demonstrated

For each dimension provide:
- score: a number from 1.0 to 5.0 (decimals allowed)
- confidence: "low", "medium", or "high" based on how much relevant signal was present
- evidence: a list of 2-4 direct quotes or specific behavioral observations from the artifacts

Also provide:
- recommendations: a list of 3-5 specific, actionable recommendations for the team, ordered by priority (most dysfunctional dimension first)

Return ONLY valid JSON matching the schema provided via the tool definition. Do not add commentary outside the JSON.
"""


def _format_dimensions(dimensions: dict) -> str:
    sorted_dims = sorted(dimensions.items(), key=lambda x: x[1]["order"])
    parts = []
    for key, dim in sorted_dims:
        healthy = "\n  - ".join(dim["healthy_signals"])
        dysfunctional = "\n  - ".join(dim["dysfunction_signals"])
        parts.append(f"""### {dim['order']}. {dim['name']} (key: `{key}`)
{dim['description']}

Healthy signals:
  - {healthy}

Dysfunction signals:
  - {dysfunctional}
{_format_facets(dim.get("facets"))}
Scoring guidance:
{dim['scoring_guidance']}""")
    return "\n\n".join(parts)


def _format_facets(facets: list | None) -> str:
    """Emit the rubric's observable behavioral facets (v0.9+). Empty string if absent."""
    if not facets:
        return ""
    blocks = ["\nBehavioral facets (observable acts, + healthy / - dysfunctional):"]
    for facet in facets:
        lines = [f"  {facet['name']}:"]
        lines += [f"    + {b}" for b in facet.get("healthy") or []]
        lines += [f"    - {b}" for b in facet.get("dysfunction") or []]
        blocks.append("\n".join(lines))
    return "\n".join(blocks) + "\n"
```

Note: the rubric's `healthy_signals` / `dysfunction_signals` are a verbatim subset of the facet
entries, so the two sections above intentionally overlap — the rollup is the short list the model
scores against, the facets give it the full observable vocabulary for evidence extraction.

- [ ] **Step 4: Run tests — verify they pass**

```bash
cd team-assess && pytest tests/test_builder.py -v
```

Expected: 5 tests pass.

- [ ] **Step 5: Commit**

```bash
git add team-assess/prompts/builder.py team-assess/tests/test_builder.py
git commit -m "feat: prompt builder constructs scoring prompt from rubric"
```

---

## Task 7: Claude Scorer

**Files:**
- Create: `team-assess/scorer/claude_scorer.py`
- Create: `team-assess/tests/test_scorer.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_scorer.py
import pytest
from unittest.mock import MagicMock, patch
from scorer.claude_scorer import ClaudeScorer, ScoringError

SAMPLE_RUBRIC = {
    "framework": "five-dysfunctions",
    "dimensions": {
        "trust": {"name": "Absence of Trust", "order": 1, "description": "", "healthy_signals": [], "dysfunction_signals": [], "scoring_guidance": ""},
        "conflict": {"name": "Fear of Conflict", "order": 2, "description": "", "healthy_signals": [], "dysfunction_signals": [], "scoring_guidance": ""},
        "commitment": {"name": "Lack of Commitment", "order": 3, "description": "", "healthy_signals": [], "dysfunction_signals": [], "scoring_guidance": ""},
        "accountability": {"name": "Avoidance of Accountability", "order": 4, "description": "", "healthy_signals": [], "dysfunction_signals": [], "scoring_guidance": ""},
        "results": {"name": "Inattention to Results", "order": 5, "description": "", "healthy_signals": [], "dysfunction_signals": [], "scoring_guidance": ""},
    },
}

MOCK_CLAUDE_RESPONSE = {
    "dimensions": {
        "trust": {"score": 3.0, "confidence": "medium", "evidence": ["Alice asked for help"]},
        "conflict": {"score": 2.5, "confidence": "high", "evidence": ["No debate observed"]},
        "commitment": {"score": 3.5, "confidence": "medium", "evidence": ["Decisions followed through"]},
        "accountability": {"score": 2.0, "confidence": "low", "evidence": ["No peer feedback seen"]},
        "results": {"score": 3.2, "confidence": "medium", "evidence": ["Team goal mentioned"]},
    },
    "recommendations": ["Address accountability directly", "Introduce structured conflict norms"],
}


def _make_mock_client(response_data: dict):
    mock_content = MagicMock()
    mock_content.type = "tool_use"
    mock_content.input = response_data

    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_message.stop_reason = "tool_use"

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    return mock_client


def test_score_returns_snapshot_with_all_dimensions():
    mock_client = _make_mock_client(MOCK_CLAUDE_RESPONSE)
    scorer = ClaudeScorer({"model": "claude-sonnet-4-6"}, client=mock_client)
    snapshot = scorer.score("Some team content", SAMPLE_RUBRIC, "Q1-2025", ["notes.txt"])
    assert set(snapshot["dimensions"].keys()) == {"trust", "conflict", "commitment", "accountability", "results"}

def test_score_computes_overall_health():
    mock_client = _make_mock_client(MOCK_CLAUDE_RESPONSE)
    scorer = ClaudeScorer({"model": "claude-sonnet-4-6"}, client=mock_client)
    snapshot = scorer.score("Some team content", SAMPLE_RUBRIC, "Q1-2025", ["notes.txt"])
    expected = round((3.0 + 2.5 + 3.5 + 2.0 + 3.2) / 5, 2)
    assert snapshot["overall_health"] == expected

def test_score_includes_period_and_metadata():
    mock_client = _make_mock_client(MOCK_CLAUDE_RESPONSE)
    scorer = ClaudeScorer({"model": "claude-sonnet-4-6"}, client=mock_client)
    snapshot = scorer.score("Some team content", SAMPLE_RUBRIC, "Q1-2025", ["notes.txt"])
    assert snapshot["period"] == "Q1-2025"
    assert "run_date" in snapshot
    assert snapshot["input_files"] == ["notes.txt"]

def test_score_includes_recommendations():
    mock_client = _make_mock_client(MOCK_CLAUDE_RESPONSE)
    scorer = ClaudeScorer({"model": "claude-sonnet-4-6"}, client=mock_client)
    snapshot = scorer.score("Some team content", SAMPLE_RUBRIC, "Q1-2025", ["notes.txt"])
    assert len(snapshot["recommendations"]) >= 1
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd team-assess && pytest tests/test_scorer.py -v
```

Expected: `ModuleNotFoundError: No module named 'scorer.claude_scorer'`

- [ ] **Step 3: Write `scorer/claude_scorer.py`**

```python
from datetime import date
from prompts.builder import build_scoring_prompt

SCORING_TOOL = {
    "name": "record_team_assessment",
    "description": "Record the structured team health assessment results",
    "input_schema": {
        "type": "object",
        "properties": {
            "dimensions": {
                "type": "object",
                "description": "Scores for each dysfunction dimension",
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number", "minimum": 1, "maximum": 5},
                        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
                        "evidence": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    },
                    "required": ["score", "confidence", "evidence"],
                },
            },
            "recommendations": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "description": "Prioritized action recommendations for the team",
            },
        },
        "required": ["dimensions", "recommendations"],
    },
}


class ScoringError(Exception):
    pass


class ClaudeScorer:
    def __init__(self, claude_config: dict, client=None):
        self._model = claude_config.get("model", "claude-sonnet-4-6")
        if client is not None:
            self._client = client
        else:
            import anthropic
            api_key_env = claude_config.get("api_key_env", "ANTHROPIC_API_KEY")
            self._client = anthropic.Anthropic()

    def score(self, content: str, rubric: dict, period: str, input_files: list[str]) -> dict:
        prompt = build_scoring_prompt(rubric, content)
        message = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            tools=[SCORING_TOOL],
            tool_choice={"type": "any"},
            messages=[{"role": "user", "content": prompt}],
        )

        tool_result = self._extract_tool_result(message)
        return self._build_snapshot(tool_result, period, input_files)

    def _extract_tool_result(self, message) -> dict:
        for block in message.content:
            if block.type == "tool_use":
                return block.input
        raise ScoringError("Claude did not return a tool_use response")

    def _build_snapshot(self, tool_result: dict, period: str, input_files: list[str]) -> dict:
        dimensions = tool_result["dimensions"]
        scores = [dim["score"] for dim in dimensions.values()]
        overall_health = round(sum(scores) / len(scores), 2) if scores else 0.0
        return {
            "period": period,
            "run_date": date.today().isoformat(),
            "input_files": input_files,
            "dimensions": dimensions,
            "overall_health": overall_health,
            "recommendations": tool_result["recommendations"],
        }
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
cd team-assess && pytest tests/test_scorer.py -v
```

Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add team-assess/scorer/claude_scorer.py team-assess/tests/test_scorer.py
git commit -m "feat: Claude scorer calls API via tool use, returns structured snapshot"
```

---

## Task 8: Snapshot Store

**Files:**
- Create: `team-assess/snapshots/__init__.py`
- Create: `team-assess/snapshots/store.py`
- Create: `team-assess/tests/test_store.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_store.py
import pytest
import json
from pathlib import Path
from snapshots.store import save_snapshot, load_snapshot, SnapshotNotFoundError

SAMPLE_SNAPSHOT = {
    "period": "Q1-2025",
    "run_date": "2026-08-04",
    "input_files": ["notes.txt"],
    "dimensions": {
        "trust": {"score": 3.0, "confidence": "medium", "evidence": ["Alice asked for help"]},
    },
    "overall_health": 3.0,
    "recommendations": ["Improve trust"],
}


def test_save_and_load_roundtrip(tmp_path):
    save_snapshot(SAMPLE_SNAPSHOT, snapshots_dir=tmp_path)
    loaded = load_snapshot("Q1-2025", snapshots_dir=tmp_path)
    assert loaded["period"] == "Q1-2025"
    assert loaded["overall_health"] == 3.0

def test_save_creates_json_file(tmp_path):
    save_snapshot(SAMPLE_SNAPSHOT, snapshots_dir=tmp_path)
    assert (tmp_path / "Q1-2025.json").exists()

def test_load_missing_snapshot_raises(tmp_path):
    with pytest.raises(SnapshotNotFoundError):
        load_snapshot("Q4-2099", snapshots_dir=tmp_path)

def test_save_overwrites_existing(tmp_path):
    save_snapshot(SAMPLE_SNAPSHOT, snapshots_dir=tmp_path)
    updated = {**SAMPLE_SNAPSHOT, "overall_health": 4.0}
    save_snapshot(updated, snapshots_dir=tmp_path)
    loaded = load_snapshot("Q1-2025", snapshots_dir=tmp_path)
    assert loaded["overall_health"] == 4.0
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd team-assess && pytest tests/test_store.py -v
```

Expected: `ModuleNotFoundError: No module named 'snapshots.store'`

- [ ] **Step 3: Write `snapshots/__init__.py`** (empty)

- [ ] **Step 4: Write `snapshots/store.py`**

```python
import json
from pathlib import Path

DEFAULT_SNAPSHOTS_DIR = Path("snapshots")


class SnapshotNotFoundError(Exception):
    pass


def save_snapshot(snapshot: dict, snapshots_dir: Path = DEFAULT_SNAPSHOTS_DIR) -> Path:
    snapshots_dir = Path(snapshots_dir)
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    path = snapshots_dir / f"{snapshot['period']}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)
    return path


def load_snapshot(period: str, snapshots_dir: Path = DEFAULT_SNAPSHOTS_DIR) -> dict:
    path = Path(snapshots_dir) / f"{period}.json"
    if not path.exists():
        raise SnapshotNotFoundError(f"No snapshot found for period: {period}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
cd team-assess && pytest tests/test_store.py -v
```

Expected: 4 tests pass.

- [ ] **Step 6: Commit**

```bash
git add team-assess/snapshots/ team-assess/tests/test_store.py
git commit -m "feat: snapshot store save and load with JSON persistence"
```

---

## Task 9: Trend Diff

**Files:**
- Create: `team-assess/trend/diff.py`
- Create: `team-assess/tests/test_diff.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_diff.py
from trend.diff import compute_diff

BEFORE = {
    "period": "Q1-2025",
    "overall_health": 2.8,
    "dimensions": {
        "trust": {"score": 2.5, "confidence": "medium", "evidence": []},
        "conflict": {"score": 2.0, "confidence": "high", "evidence": []},
        "commitment": {"score": 3.0, "confidence": "medium", "evidence": []},
        "accountability": {"score": 2.4, "confidence": "low", "evidence": []},
        "results": {"score": 4.1, "confidence": "medium", "evidence": []},
    },
    "recommendations": [],
}

AFTER = {
    "period": "Q2-2025",
    "overall_health": 3.1,
    "dimensions": {
        "trust": {"score": 3.3, "confidence": "medium", "evidence": []},
        "conflict": {"score": 2.4, "confidence": "high", "evidence": []},
        "commitment": {"score": 3.0, "confidence": "medium", "evidence": []},
        "accountability": {"score": 2.1, "confidence": "low", "evidence": []},
        "results": {"score": 4.7, "confidence": "medium", "evidence": []},
    },
    "recommendations": [],
}


def test_diff_overall_health_delta():
    diff = compute_diff(BEFORE, AFTER)
    assert round(diff["overall_health_delta"], 2) == 0.3

def test_diff_dimension_delta():
    diff = compute_diff(BEFORE, AFTER)
    assert round(diff["dimensions"]["trust"]["delta"], 1) == 0.8

def test_diff_direction_improving():
    diff = compute_diff(BEFORE, AFTER)
    assert diff["dimensions"]["trust"]["direction"] == "improving"

def test_diff_direction_stable():
    diff = compute_diff(BEFORE, AFTER)
    assert diff["dimensions"]["commitment"]["direction"] == "stable"

def test_diff_direction_declining():
    diff = compute_diff(BEFORE, AFTER)
    assert diff["dimensions"]["accountability"]["direction"] == "declining"

def test_diff_warns_large_movement():
    diff = compute_diff(BEFORE, AFTER)
    # trust moved +0.8, results moved +0.6 — neither exceeds 1.0
    assert diff["dimensions"]["trust"]["warning"] is False
    # Manufacture a large movement
    big_after = {**AFTER, "dimensions": {**AFTER["dimensions"], "trust": {"score": 4.9, "confidence": "medium", "evidence": []}}}
    diff2 = compute_diff(BEFORE, big_after)
    assert diff2["dimensions"]["trust"]["warning"] is True

def test_diff_includes_before_and_after_periods():
    diff = compute_diff(BEFORE, AFTER)
    assert diff["before_period"] == "Q1-2025"
    assert diff["after_period"] == "Q2-2025"
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd team-assess && pytest tests/test_diff.py -v
```

Expected: `ModuleNotFoundError: No module named 'trend.diff'`

- [ ] **Step 3: Write `trend/diff.py`**

```python
STABLE_THRESHOLD = 0.2
WARNING_THRESHOLD = 1.0


def compute_diff(before: dict, after: dict) -> dict:
    dimension_diffs = {}
    for key in after["dimensions"]:
        if key not in before["dimensions"]:
            continue
        delta = after["dimensions"][key]["score"] - before["dimensions"][key]["score"]
        dimension_diffs[key] = {
            "before_score": before["dimensions"][key]["score"],
            "after_score": after["dimensions"][key]["score"],
            "delta": round(delta, 2),
            "direction": _direction(delta),
            "warning": abs(delta) >= WARNING_THRESHOLD,
        }

    overall_delta = round(after["overall_health"] - before["overall_health"], 2)
    return {
        "before_period": before["period"],
        "after_period": after["period"],
        "overall_health_delta": overall_delta,
        "overall_direction": _direction(overall_delta),
        "dimensions": dimension_diffs,
    }


def _direction(delta: float) -> str:
    if delta > STABLE_THRESHOLD:
        return "improving"
    if delta < -STABLE_THRESHOLD:
        return "declining"
    return "stable"
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
cd team-assess && pytest tests/test_diff.py -v
```

Expected: 7 tests pass.

- [ ] **Step 5: Commit**

```bash
git add team-assess/trend/diff.py team-assess/tests/test_diff.py
git commit -m "feat: trend diff computes before/after deltas with direction and warnings"
```

---

## Task 10: Markdown Renderer

**Files:**
- Create: `team-assess/renderer/markdown.py`
- Create: `team-assess/tests/test_renderer.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_renderer.py
from renderer.markdown import render_markdown

SNAPSHOT = {
    "period": "Q2-2025",
    "run_date": "2026-08-04",
    "input_files": ["notes.txt", "retro.md"],
    "overall_health": 3.1,
    "dimensions": {
        "trust": {"score": 3.3, "confidence": "medium", "evidence": ["Alice asked for help openly"]},
        "conflict": {"score": 2.4, "confidence": "high", "evidence": ["No debate observed in meetings"]},
        "commitment": {"score": 3.0, "confidence": "medium", "evidence": ["Decisions followed through"]},
        "accountability": {"score": 2.1, "confidence": "low", "evidence": ["No peer feedback seen"]},
        "results": {"score": 4.7, "confidence": "medium", "evidence": ["Team goal cited in retro"]},
    },
    "recommendations": [
        "Introduce structured norms for peer accountability",
        "Run a dedicated conflict exercise in next offsite",
    ],
}

TREND = {
    "before_period": "Q1-2025",
    "after_period": "Q2-2025",
    "overall_health_delta": 0.3,
    "overall_direction": "improving",
    "dimensions": {
        "trust": {"delta": 0.8, "direction": "improving", "warning": False, "before_score": 2.5, "after_score": 3.3},
        "conflict": {"delta": 0.4, "direction": "improving", "warning": False, "before_score": 2.0, "after_score": 2.4},
        "commitment": {"delta": 0.0, "direction": "stable", "warning": False, "before_score": 3.0, "after_score": 3.0},
        "accountability": {"delta": -0.3, "direction": "declining", "warning": False, "before_score": 2.4, "after_score": 2.1},
        "results": {"delta": 0.6, "direction": "improving", "warning": False, "before_score": 4.1, "after_score": 4.7},
    },
}


def test_report_contains_period():
    report = render_markdown(SNAPSHOT)
    assert "Q2-2025" in report

def test_report_contains_overall_health():
    report = render_markdown(SNAPSHOT)
    assert "3.1" in report

def test_report_contains_all_dimensions():
    report = render_markdown(SNAPSHOT)
    for dim in ["Trust", "Conflict", "Commitment", "Accountability", "Results"]:
        assert dim in report

def test_report_contains_recommendations():
    report = render_markdown(SNAPSHOT)
    assert "peer accountability" in report

def test_report_contains_evidence():
    report = render_markdown(SNAPSHOT)
    assert "Alice asked for help openly" in report

def test_report_with_trend_shows_delta():
    report = render_markdown(SNAPSHOT, trend=TREND)
    assert "+0.3" in report or "0.3" in report
    assert "Q1-2025" in report

def test_report_with_trend_shows_direction_arrows():
    report = render_markdown(SNAPSHOT, trend=TREND)
    assert "↑" in report or "↓" in report

def test_report_without_trend_renders_cleanly():
    report = render_markdown(SNAPSHOT)
    assert isinstance(report, str)
    assert len(report) > 100
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd team-assess && pytest tests/test_renderer.py -v
```

Expected: `ModuleNotFoundError: No module named 'renderer.markdown'`

- [ ] **Step 3: Write `renderer/markdown.py`**

```python
DIMENSION_LABELS = {
    "trust": "Trust",
    "conflict": "Conflict",
    "commitment": "Commitment",
    "accountability": "Accountability",
    "results": "Results",
}

DIRECTION_ARROWS = {
    "improving": "↑",
    "declining": "↓",
    "stable": "→",
}


def render_markdown(snapshot: dict, trend: dict | None = None) -> str:
    lines = []
    period = snapshot["period"]

    health = snapshot["overall_health"]
    if trend:
        delta = trend["overall_health_delta"]
        direction = DIRECTION_ARROWS[trend["overall_direction"]]
        prior = trend["before_period"]
        health_line = f"Overall Health: {health} / 5  ({direction} {_fmt_delta(delta)} from {prior})"
    else:
        health_line = f"Overall Health: {health} / 5"

    lines.append(f"# Team Health Assessment — {period}")
    lines.append(f"{health_line}")
    lines.append("")

    lines.append("## Dimension Scores")
    lines.append("")

    dims_sorted = _sort_dimensions_by_score(snapshot["dimensions"])
    for key, dim in dims_sorted:
        label = DIMENSION_LABELS.get(key, key.title())
        score = dim["score"]
        bar = _score_bar(score)
        if trend and key in trend["dimensions"]:
            t = trend["dimensions"][key]
            arrow = DIRECTION_ARROWS[t["direction"]]
            delta_str = f"{arrow} {_fmt_delta(t['delta'])}"
            warning = "  ⚠" if t["warning"] else ""
            lines.append(f"{label:<16} {bar}  {score:.1f}  {delta_str}{warning}")
        else:
            lines.append(f"{label:<16} {bar}  {score:.1f}")

    lines.append("")
    lines.append("## Priority Actions")
    lines.append("")
    for i, rec in enumerate(snapshot["recommendations"], 1):
        lines.append(f"{i}. {rec}")

    lines.append("")
    lines.append("## Evidence Highlights")
    for key, dim in dims_sorted:
        label = DIMENSION_LABELS.get(key, key.title())
        lines.append(f"\n### {label}")
        for evidence in dim.get("evidence", []):
            lines.append(f'- "{evidence}"')

    lines.append("")
    lines.append(f"*Inputs: {', '.join(snapshot['input_files'])}*")
    lines.append(f"*Run date: {snapshot['run_date']}*")

    return "\n".join(lines)


def _sort_dimensions_by_score(dimensions: dict) -> list:
    return sorted(dimensions.items(), key=lambda x: x[1]["score"])


def _score_bar(score: float) -> str:
    filled = round(score)
    return "█" * filled + "░" * (5 - filled)


def _fmt_delta(delta: float) -> str:
    return f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}"
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
cd team-assess && pytest tests/test_renderer.py -v
```

Expected: 8 tests pass.

- [ ] **Step 5: Commit**

```bash
git add team-assess/renderer/markdown.py team-assess/tests/test_renderer.py
git commit -m "feat: markdown renderer produces team health report with optional trend"
```

---

## Task 11: Config Loader

**Files:**
- Create: `team-assess/config.py`
- Create: `team-assess/config.toml`

- [ ] **Step 1: Write `config.toml`**

```toml
[claude]
model = "claude-sonnet-4-6"
api_key_env = "ANTHROPIC_API_KEY"

[output]
format = "markdown"

[rubric]
framework = "five-dysfunctions"
path = "rubric/five-dysfunctions.yaml"

[paths]
snapshots_dir = "snapshots"
output_dir = "output"
```

- [ ] **Step 2: Write `config.py`**

```python
import tomllib
from pathlib import Path


DEFAULT_CONFIG = {
    "claude": {"model": "claude-sonnet-4-6", "api_key_env": "ANTHROPIC_API_KEY"},
    "output": {"format": "markdown"},
    "rubric": {"framework": "five-dysfunctions", "path": "rubric/five-dysfunctions.yaml"},
    "paths": {"snapshots_dir": "snapshots", "output_dir": "output"},
}


def load_config(path: str = "config.toml") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        return DEFAULT_CONFIG
    with config_path.open("rb") as f:
        user_config = tomllib.load(f)
    return _merge(DEFAULT_CONFIG, user_config)


def _merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result
```

- [ ] **Step 3: Verify config loads without errors**

```bash
cd team-assess && python -c "from config import load_config; c = load_config(); print(c['claude']['model'])"
```

Expected: `claude-sonnet-4-6`

- [ ] **Step 4: Commit**

```bash
git add team-assess/config.py team-assess/config.toml
git commit -m "feat: config loader with toml and defaults fallback"
```

---

## Task 12: CLI Entrypoint

**Files:**
- Create: `team-assess/assess.py`

- [ ] **Step 1: Write `assess.py`**

```python
import argparse
import sys
from pathlib import Path

from config import load_config
from ingestion.scanner import scan_directory
from rubric.loader import load_rubric
from scorer.claude_scorer import ClaudeScorer
from snapshots.store import save_snapshot, load_snapshot, SnapshotNotFoundError
from trend.diff import compute_diff
from renderer.markdown import render_markdown


def main():
    parser = argparse.ArgumentParser(
        description="Assess team health using the Five Dysfunctions framework"
    )
    parser.add_argument("--input", required=True, help="Directory of input files")
    parser.add_argument("--period", required=True, help="Label for this snapshot (e.g. Q1-2025)")
    parser.add_argument("--compare", help="Period label to diff against")
    parser.add_argument("--output", help="Output directory (overrides config)")
    parser.add_argument("--config", default="config.toml", help="Path to config.toml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    output_dir = Path(args.output or cfg["paths"]["output_dir"])
    snapshots_dir = Path(cfg["paths"]["snapshots_dir"])

    print(f"Scanning input directory: {args.input}")
    content = scan_directory(Path(args.input))
    if not content.strip():
        print("Error: no readable content found in input directory.", file=sys.stderr)
        sys.exit(1)

    input_files = [f.name for f in sorted(Path(args.input).iterdir()) if f.is_file()]

    print(f"Loading rubric: {cfg['rubric']['path']}")
    rubric = load_rubric(cfg["rubric"]["path"])

    print("Scoring with Claude...")
    scorer = ClaudeScorer(cfg["claude"])
    snapshot = scorer.score(content, rubric, args.period, input_files)

    save_snapshot(snapshot, snapshots_dir=snapshots_dir)
    print(f"Snapshot saved to {snapshots_dir}/{args.period}.json")

    trend = None
    if args.compare:
        try:
            prior = load_snapshot(args.compare, snapshots_dir=snapshots_dir)
            trend = compute_diff(prior, snapshot)
            print(f"Trend computed vs {args.compare}")
        except SnapshotNotFoundError:
            print(f"Warning: no snapshot found for period '{args.compare}', skipping trend.", file=sys.stderr)

    report = render_markdown(snapshot, trend=trend)

    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"report-{args.period}.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify help output**

```bash
cd team-assess && python assess.py --help
```

Expected: usage printed with `--input`, `--period`, `--compare`, `--output`, `--config` options.

- [ ] **Step 3: Run full test suite**

```bash
cd team-assess && pytest -v
```

Expected: all tests pass (no failures).

- [ ] **Step 4: Commit**

```bash
git add team-assess/assess.py
git commit -m "feat: CLI entrypoint wires ingestion, scoring, snapshot, trend, and rendering"
```

---

## Task 13: Final Cleanup and Push

- [ ] **Step 1: Add `.gitignore`**

```
__pycache__/
*.pyc
*.pyo
.env
snapshots/
output/
*.egg-info/
dist/
.pytest_cache/
```

- [ ] **Step 2: Run full test suite one final time**

```bash
cd team-assess && pytest -v
```

Expected: all tests pass.

- [ ] **Step 3: Commit and push**

```bash
git add team-assess/.gitignore
git commit -m "chore: add gitignore for team-assess"
git push origin main
```

---

## Smoke Test (Manual — requires `ANTHROPIC_API_KEY` set)

After implementation is complete, create a sample input directory and run end-to-end:

```bash
mkdir -p /tmp/team-sample
cat > /tmp/team-sample/retro.txt << 'EOF'
Sprint Retrospective Notes

Alice openly admitted she had missed the deadline and asked for help catching up.
Bob raised a concern about the architecture decision but the team moved forward without debating it.
The team agreed to the Q3 roadmap in the meeting but three people later said they didn't really agree.
No one called out the missed delivery on the auth service - it just slipped.
EOF

cd team-assess && python assess.py --input /tmp/team-sample --period Q1-2025
# Then run again with a second input to test trend:
python assess.py --input /tmp/team-sample --period Q2-2025 --compare Q1-2025
cat output/report-Q2-2025.md
```
