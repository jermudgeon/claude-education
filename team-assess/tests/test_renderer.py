from renderer.markdown import render_markdown

# New schema: facets nested inside dimensions, trend inside dimension object
SNAPSHOT = {
    "period": "Q2-2025",
    "run_date": "2026-08-04",
    "input_files": ["notes.txt", "retro.md"],
    "overall_health": 3.1,
    "dimensions": {
        "trust": {
            "score": 3.3,
            "evidence": ["Alice asked for help openly"],
            "facets": {
                "vulnerability_psychological_safety": {
                    "score": 2.8,
                    "confidence": "high",
                    "evidence": ["Alice asked for help openly"],
                },
                "contractual_trust_reliability_of_character": {
                    "score": 3.5,
                    "confidence": "medium",
                    "evidence": [],
                },
            },
        },
        "conflict": {
            "score": 2.4,
            "evidence": ["No debate observed in meetings"],
            "facets": {
                "surfacing_disagreement": {
                    "score": 2.4,
                    "confidence": "high",
                    "evidence": ["No debate observed in meetings"],
                },
            },
        },
        "commitment": {
            "score": 3.0,
            "evidence": ["Decisions followed through"],
            "facets": {
                "clarity_of_mission_goals_roles": {
                    "score": 3.0,
                    "confidence": "medium",
                    "evidence": ["Decisions followed through"],
                },
            },
        },
        "accountability": {
            "score": 2.1,
            "evidence": [],
            "facets": {
                "peer_to_peer_accountability": {
                    "score": 2.1,
                    "confidence": "low",
                    "evidence": [],
                },
            },
        },
        "results": {
            "score": 4.7,
            "evidence": ["Team goal cited in retro"],
            "facets": {
                "dependability_delivery": {
                    "score": 4.7,
                    "confidence": "high",
                    "evidence": ["Team goal cited in retro"],
                },
            },
        },
    },
    "recommendations": [
        "Introduce structured norms for peer accountability",
        "Run a dedicated conflict exercise in next offsite",
    ],
}

# New schema: trend is embedded inside each dimension (no top-level trend arg needed)
SNAPSHOT_WITH_TREND = {
    **SNAPSHOT,
    "dimensions": {
        **{k: {**v} for k, v in SNAPSHOT["dimensions"].items()},
    },
}
# Inject trend into dimensions for the trend-test snapshot
SNAPSHOT_WITH_TREND["dimensions"]["trust"] = {
    **SNAPSHOT["dimensions"]["trust"],
    "trend": {
        "compared_to": "Q1-2025",
        "delta": 0.8,
        "direction": "improving",
        "warning": False,
    },
}
SNAPSHOT_WITH_TREND["dimensions"]["conflict"] = {
    **SNAPSHOT["dimensions"]["conflict"],
    "trend": {
        "compared_to": "Q1-2025",
        "delta": 0.4,
        "direction": "improving",
        "warning": False,
    },
}

# Legacy top-level trend dict (kept for backward-compat test)
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


def test_report_with_embedded_dimension_trend_shows_arrow():
    report = render_markdown(SNAPSHOT_WITH_TREND)
    assert "↑" in report


def test_report_with_embedded_dimension_trend_shows_delta():
    report = render_markdown(SNAPSHOT_WITH_TREND)
    assert "+0.8" in report


def test_facet_detail_section_present_when_facets_exist():
    report = render_markdown(SNAPSHOT)
    assert "## Facet Detail" in report


def test_facet_detail_shows_medium_and_high_confidence_facets():
    report = render_markdown(SNAPSHOT)
    assert "vulnerability_psychological_safety" in report
    assert "contractual_trust_reliability_of_character" in report
    assert "dependability_delivery" in report


def test_facet_detail_omits_low_confidence_facets():
    report = render_markdown(SNAPSHOT)
    # peer_to_peer_accountability is low confidence — should not appear in facet detail
    # Check only within the Facet Detail section
    facet_section_start = report.find("## Facet Detail")
    assert facet_section_start != -1
    facet_section = report[facet_section_start:]
    assert "peer_to_peer_accountability" not in facet_section


def test_facet_detail_shows_evidence():
    report = render_markdown(SNAPSHOT)
    assert "Team goal cited in retro" in report


def test_snapshot_without_facets_renders_cleanly():
    snapshot_no_facets = {
        "period": "Q1-2025",
        "run_date": "2026-08-04",
        "input_files": ["notes.txt"],
        "overall_health": 3.0,
        "dimensions": {
            "trust": {"score": 3.0, "evidence": ["Some evidence"]},
        },
        "recommendations": ["Work on trust"],
    }
    report = render_markdown(snapshot_no_facets)
    assert isinstance(report, str)
    assert "## Facet Detail" not in report


def test_report_handles_none_overall_health():
    snapshot_no_health = {**SNAPSHOT, "overall_health": None}
    report = render_markdown(snapshot_no_health)
    assert "N/A" in report
    assert "None" not in report
