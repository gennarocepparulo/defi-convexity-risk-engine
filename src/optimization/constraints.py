def validate_width_bounds(width_pct: float, min_width: float = 0.01, max_width: float = 1.0) -> None:
    if not (min_width <= width_pct <= max_width):
        raise ValueError(
            f"width_pct must be between {min_width:.4f} and {max_width:.4f}, got {width_pct:.4f}"
        )


def validate_positive_capital(capital: float) -> None:
    if capital <= 0:
        raise ValueError("Capital must be strictly positive.")