def clamp(min_value: float, max_value: float, value: float) -> float:
    return min(max_value, max(min_value, value))
