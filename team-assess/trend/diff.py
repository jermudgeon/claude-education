STABLE_THRESHOLD = 0.2
WARNING_THRESHOLD = 1.0


def compute_diff(before: dict, after: dict) -> dict:
    dimension_diffs = {}
    all_keys = set(before["dimensions"]) | set(after["dimensions"])
    for key in sorted(all_keys):
        if key not in before["dimensions"] or key not in after["dimensions"]:
            continue  # skip dimensions not in both snapshots
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
