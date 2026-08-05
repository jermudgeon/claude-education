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
    if not rubric or not isinstance(rubric, dict):
        raise RubricError("Rubric file is empty or not a valid YAML mapping")
    required_fields = ["name", "order", "description", "healthy_signals", "dysfunction_signals", "scoring_guidance"]
    dimensions = rubric.get("dimensions", {})
    if not dimensions:
        raise RubricError("Rubric must define at least one dimension under 'dimensions'")
    for key, dim in dimensions.items():
        for field in required_fields:
            if field not in dim:
                raise RubricError(f"Dimension '{key}' is missing required field '{field}'")
        _validate_facets(key, dim)


def _validate_facets(key: str, dim: dict) -> None:
    """Facets are optional so pre-0.9 rubric files still load, but must be well formed."""
    if "facets" not in dim:
        return
    facets = dim["facets"]
    if not isinstance(facets, list) or not facets:
        raise RubricError(f"Dimension '{key}' has a 'facets' key that is not a non-empty list")
    for i, facet in enumerate(facets):
        if not isinstance(facet, dict) or not facet.get("name"):
            raise RubricError(f"Dimension '{key}' facet {i} is missing a 'name'")
        valences = [facet.get(v) for v in ("healthy", "dysfunction")]
        if not any(isinstance(v, list) and v for v in valences):
            raise RubricError(
                f"Dimension '{key}' facet '{facet['name']}' must define a non-empty "
                "'healthy' or 'dysfunction' list"
            )
