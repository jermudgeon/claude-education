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
