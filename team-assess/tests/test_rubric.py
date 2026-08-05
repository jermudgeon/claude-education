import pytest
from pathlib import Path
from rubric.loader import load_rubric, RubricError

RUBRIC_PATH = str(Path(__file__).parent.parent / "rubric" / "five-dysfunctions.yaml")


def test_load_rubric_returns_five_dimensions():
    rubric = load_rubric(RUBRIC_PATH)
    assert set(rubric["dimensions"].keys()) == {
        "trust", "conflict", "commitment", "accountability", "results"
    }


def test_each_dimension_has_required_fields():
    rubric = load_rubric(RUBRIC_PATH)
    for key, dim in rubric["dimensions"].items():
        assert "name" in dim, f"dimension {key} missing 'name'"
        assert "order" in dim, f"dimension {key} missing 'order'"
        assert "healthy_signals" in dim, f"dimension {key} missing 'healthy_signals'"
        assert "dysfunction_signals" in dim, f"dimension {key} missing 'dysfunction_signals'"
        assert "scoring_guidance" in dim, f"dimension {key} missing 'scoring_guidance'"
        assert len(dim["healthy_signals"]) >= 2
        assert len(dim["dysfunction_signals"]) >= 2


def test_dimensions_ordered_1_through_5():
    rubric = load_rubric(RUBRIC_PATH)
    orders = sorted(dim["order"] for dim in rubric["dimensions"].values())
    assert orders == [1, 2, 3, 4, 5]


def test_missing_file_raises_rubric_error():
    with pytest.raises(RubricError):
        load_rubric("rubric/nonexistent.yaml")
