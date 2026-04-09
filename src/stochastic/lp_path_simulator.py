from dataclasses import dataclass
from typing import Dict, Any
import numpy as np
import pandas as pd

from src.strategy.uniswap_v3 import UniswapV3Strategy
from src.stochastic.fee_model import FeeModelConfig, estimate_fee_accrual


@dataclass
class LPSimulationConfig:
    initial_capital: float = 1_000.0
    il_sensitivity: float = 1.0
    include_rebalancing_costs: bool = True


def approximate_impermanent_loss(price_ratio: np.ndarray) -> np.ndarray:
    """
    Standard constant-product style IL approximation:
        IL = 2 * sqrt(R) / (1 + R) - 1
    where R = P_t / P_0

    This is not exact for concentrated liquidity, but it is a useful baseline
    until integrated with a full Uniswap v3 valuation layer.
    """
    r = np.maximum(price_ratio, 1e-12)
    return 2.0 * np.sqrt(r) / (1.0 + r) - 1.0


def simulate_lp_strategy(
    prices: np.ndarray,
    strategy: UniswapV3Strategy,
    fee_config: FeeModelConfig,
    sim_config: LPSimulationConfig
) -> pd.DataFrame:
    """
    Simulate a Uniswap v3 LP strategy along a single price path.

    Parameters
    ----------
    prices : np.ndarray
        Shape (n_steps + 1,)
    strategy : UniswapV3Strategy
    fee_config : FeeModelConfig
    sim_config : LPSimulationConfig

    Returns
    -------
    pd.DataFrame
        Time series of LP metrics
    """
    n_steps = len(prices) - 1
    initial_price = prices[0]
    capital = sim_config.initial_capital

    in_range = np.zeros(len(prices), dtype=bool)
    rebalance_flags = np.zeros(len(prices), dtype=bool)
    rebalance_costs = np.zeros(len(prices))
    center_prices = np.zeros(len(prices))

    for t in range(len(prices)):
        current_price = prices[t]
        in_range[t] = strategy.is_in_range(current_price)
        center_prices[t] = strategy.config.center_price

        if strategy.should_rebalance(current_price, step=t):
            rebalance_flags[t] = True
            if sim_config.include_rebalancing_costs:
                rebalance_costs[t] = strategy.transaction_cost()
            strategy.rebalance(new_center_price=current_price)

    fees_per_step = estimate_fee_accrual(
        prices=prices,
        in_range_mask=in_range,
        config=fee_config
    )

    cumulative_fees = capital * np.cumsum(fees_per_step)

    price_ratio = prices / initial_price
    il_fraction = approximate_impermanent_loss(price_ratio) * sim_config.il_sensitivity
    il_value = capital * il_fraction

    hodl_value = capital * price_ratio
    lp_value = capital + cumulative_fees + il_value - np.cumsum(rebalance_costs)

    net_pnl = lp_value - capital
    hodl_pnl = hodl_value - capital
    relative_lp_vs_hodl = lp_value - hodl_value

    df = pd.DataFrame({
        "step": np.arange(len(prices)),
        "price": prices,
        "center_price": center_prices,
        "in_range": in_range,
        "rebalanced": rebalance_flags,
        "rebalance_cost": rebalance_costs,
        "fee_step": capital * fees_per_step,
        "cum_fees": cumulative_fees,
        "il_fraction": il_fraction,
        "il_value": il_value,
        "lp_value": lp_value,
        "hodl_value": hodl_value,
        "net_pnl": net_pnl,
        "hodl_pnl": hodl_pnl,
        "lp_minus_hodl": relative_lp_vs_hodl,
    })

    return df
