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
