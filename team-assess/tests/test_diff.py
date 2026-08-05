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
