from dataclasses import dataclass
import numpy as np


@dataclass
class FeeModelConfig:
    fee_tier: float = 0.003          # 0.3%
    volume_multiplier: float = 10.0  # crude proxy: trading volume per unit abs return
    liquidity_share: float = 1.0     # LP share of active liquidity
    active_only: bool = True         # fees accrue only if price is in range


def estimate_fee_accrual(
    prices: np.ndarray,
    in_range_mask: np.ndarray,
    config: FeeModelConfig
) -> np.ndarray:
    """
    Estimate path-dependent fee accrual from price changes.

    Parameters
    ----------
    prices : np.ndarray
        Shape (n_steps + 1,)
    in_range_mask : np.ndarray
        Shape (n_steps + 1,)
    config : FeeModelConfig

    Returns
    -------
    np.ndarray
        Fee accrual per step, shape (n_steps + 1,)
    """
    returns = np.zeros_like(prices)
    returns[1:] = np.abs(np.diff(prices) / prices[:-1])

    proxy_volume = config.volume_multiplier * returns
    fees = config.fee_tier * config.liquidity_share * proxy_volume

    if config.active_only:
        fees = fees * in_range_mask.astype(float)

    return fees