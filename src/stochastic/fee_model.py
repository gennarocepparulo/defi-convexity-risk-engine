from dataclasses import dataclass
import numpy as np


@dataclass
class FeeModelConfig:
    fee_tier: float = 0.003
    volume_multiplier: float = 10.0
    liquidity_share: float = 1.0
    active_only: bool = True

    # Smoothed concentration effect
    reference_width: float = 0.25
    alpha: float = 0.7
    min_width: float = 0.03
    min_fee_multiplier: float = 0.50
    max_fee_multiplier: float = 3.50


def concentration_factor(width_pct: float, config: FeeModelConfig) -> float:
    """
    Smoothed concentration factor:
        (reference_width / width_pct)^alpha
    clipped to avoid unrealistic extremes.
    """
    effective_width = max(width_pct, config.min_width)

    raw = (config.reference_width / effective_width) ** config.alpha
    clipped = float(
        np.clip(raw, config.min_fee_multiplier, config.max_fee_multiplier)
    )

    return clipped


def estimate_fee_for_step(
    prev_price: float,
    current_price: float,
    in_range: bool,
    width_pct: float,
    config: FeeModelConfig,
) -> float:
    """
    Return fee accrual as a FRACTION of base capital/value for the current step.

    IMPORTANT GUARANTEES:
    - If fee_tier == 0.0 → return 0.0 exactly
    - If active_only and not in_range → return 0.0
    """

    # ------------------------------------------------------------
    # HARD ZERO-FEE GUARD (CRITICAL)
    # ------------------------------------------------------------
    if config.fee_tier == 0.0:
        return 0.0

    # ------------------------------------------------------------
    # Only accrue fees when LP is active
    # ------------------------------------------------------------
    if config.active_only and not in_range:
        return 0.0

    # ------------------------------------------------------------
    # Proxy volume from price movement
    # ------------------------------------------------------------
    abs_return = abs(current_price - prev_price) / max(prev_price, 1e-12)
    proxy_volume = config.volume_multiplier * abs_return

    # ------------------------------------------------------------
    # Concentration effect
    # ------------------------------------------------------------
    conc = concentration_factor(width_pct, config)

    fee_fraction = (
        config.fee_tier
        * config.liquidity_share
        * proxy_volume
        * conc
    )

    return float(fee_fraction)


def estimate_fee_accrual(
    prices: np.ndarray,
    in_range_mask: np.ndarray,
    width_pct: float,
    config: FeeModelConfig,
) -> np.ndarray:
    """
    Vectorized fee accrual over a price path.
    """
    fees = np.zeros(len(prices), dtype=float)

    # ------------------------------------------------------------
    # HARD ZERO-FEE SHORT-CIRCUIT
    # ------------------------------------------------------------
    if config.fee_tier == 0.0:
        return fees

    for t in range(1, len(prices)):
        fees[t] = estimate_fee_for_step(
            prev_price=prices[t - 1],
            current_price=prices[t],
            in_range=bool(in_range_mask[t]),
            width_pct=width_pct,
            config=config,
        )

    return fees