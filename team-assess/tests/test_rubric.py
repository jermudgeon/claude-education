import pytest
import yaml
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


def test_version_and_sources_present():
    rubric = load_rubric(RUBRIC_PATH)
    assert rubric["version"] == "0.9"
    assert rubric["sources"], "rubric must record its source frameworks"
    assert all(s.get("name") for s in rubric["sources"])


def test_every_dimension_has_facets():
    rubric = load_rubric(RUBRIC_PATH)
    for key, dim in rubric["dimensions"].items():
        assert dim.get("facets"), f"dimension {key} has no facets"


def test_every_facet_is_named_and_has_indicators():
    rubric = load_rubric(RUBRIC_PATH)
    for key, dim in rubric["dimensions"].items():
        for facet in dim["facets"]:
            assert facet.get("name"), f"unnamed facet in dimension {key}"
            healthy = facet.get("healthy") or []
            dysfunction = facet.get("dysfunction") or []
            assert healthy or dysfunction, (
                f"facet {facet['name']} in {key} has no indicators"
            )


@pytest.mark.parametrize(
    "rollup_field,facet_field",
    [("healthy_signals", "healthy"), ("dysfunction_signals", "dysfunction")],
)
def test_rollup_signals_are_verbatim_subset_of_facets(rollup_field, facet_field):
    rubric = load_rubric(RUBRIC_PATH)
    for key, dim in rubric["dimensions"].items():
        from_facets = {
            entry
            for facet in dim["facets"]
            for entry in (facet.get(facet_field) or [])
        }
        for signal in dim[rollup_field]:
            assert signal in from_facets, (
                f"{key}.{rollup_field} entry not found verbatim in any facet "
                f"{facet_field} list: {signal!r}"
            )


def test_malformed_facet_raises_rubric_error(tmp_path):
    rubric = load_rubric(RUBRIC_PATH)
    rubric["dimensions"]["trust"]["facets"] = [{"name": "No indicators"}]
    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump(rubric))
    with pytest.raises(RubricError):
        load_rubric(str(bad))
