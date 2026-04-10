from dataclasses import dataclass
from typing import Dict
import numpy as np
import pandas as pd

from src.strategy.uniswap_v3 import UniswapV3Strategy
from src.stochastic.fee_model import FeeModelConfig, estimate_fee_for_step


@dataclass
class LPSimulationConfig:
    initial_capital: float = 1_000.0
    il_sensitivity: float = 1.0
    include_rebalancing_costs: bool = True


def approximate_impermanent_loss(price_ratio: float) -> float:
    """
    Standard constant-product style IL approximation:

        IL = 2 * sqrt(R) / (1 + R) - 1

    where R = P_t / P_ref

    Notes
    -----
    - This is not exact concentrated-liquidity accounting.
    - However, when combined with IL reset after rebalance,
      it provides a much more realistic baseline than a
      single global reference price.
    """
    r = max(price_ratio, 1e-12)
    return 2.0 * np.sqrt(r) / (1.0 + r) - 1.0


def simulate_lp_strategy(
    prices: np.ndarray,
    strategy: UniswapV3Strategy,
    fee_config: FeeModelConfig,
    sim_config: LPSimulationConfig
) -> pd.DataFrame:
    """
    Simulate a Uniswap v3 LP strategy along a single price path.

    This version includes:
    - width-dependent fee intensity
    - rebalance-aware IL reset
    - explicit rebalancing costs
    - LP vs HODL comparison

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
    n = len(prices)
    if n < 2:
        raise ValueError("prices must contain at least two observations")

    initial_price = float(prices[0])
    initial_capital = float(sim_config.initial_capital)

    # Output arrays
    steps = np.arange(n)
    center_prices = np.zeros(n, dtype=float)
    lower_bounds = np.zeros(n, dtype=float)
    upper_bounds = np.zeros(n, dtype=float)

    in_range = np.zeros(n, dtype=bool)
    rebalanced = np.zeros(n, dtype=bool)

    fee_step = np.zeros(n, dtype=float)
    cum_fees = np.zeros(n, dtype=float)

    rebalance_cost = np.zeros(n, dtype=float)
    cum_rebalance_cost = np.zeros(n, dtype=float)

    il_fraction = np.zeros(n, dtype=float)
    il_value = np.zeros(n, dtype=float)

    lp_value = np.zeros(n, dtype=float)
    hodl_value = np.zeros(n, dtype=float)
    net_pnl = np.zeros(n, dtype=float)
    hodl_pnl = np.zeros(n, dtype=float)
    lp_minus_hodl = np.zeros(n, dtype=float)

    # HODL benchmark
    hodl_units = initial_capital / initial_price
    hodl_value[0] = initial_capital
    hodl_pnl[0] = 0.0

    # Segment-based LP accounting
    base_value = initial_capital          # value at the start of the active segment
    reference_price = initial_price       # IL reference resets after each rebalance
    segment_fee_cum = 0.0                 # fees earned since last rebalance
    total_fee_cum = 0.0
    total_rebalance_cost = 0.0

    # Initial state
    center_prices[0] = strategy.config.center_price
    lower_bounds[0] = strategy.lower_bound
    upper_bounds[0] = strategy.upper_bound
    in_range[0] = strategy.is_in_range(initial_price)
    lp_value[0] = initial_capital
    lp_minus_hodl[0] = 0.0

    for t in range(1, n):
        current_price = float(prices[t])
        prev_price = float(prices[t - 1])

        # State before possible rebalance
        center_prices[t] = strategy.config.center_price
        lower_bounds[t] = strategy.lower_bound
        upper_bounds[t] = strategy.upper_bound
        in_range[t] = strategy.is_in_range(current_price)

        # Fee accrual for this step
        fee_fraction_t = estimate_fee_for_step(
            prev_price=prev_price,
            current_price=current_price,
            in_range=bool(in_range[t]),
            width_pct=strategy.config.width_pct,
            config=fee_config
        )

        fee_value_t = base_value * fee_fraction_t
        fee_step[t] = fee_value_t
        segment_fee_cum += fee_value_t
        total_fee_cum += fee_value_t
        cum_fees[t] = total_fee_cum

        # IL relative to the current segment reference price
        ratio = current_price / max(reference_price, 1e-12)
        current_il_fraction = (
            approximate_impermanent_loss(ratio) * sim_config.il_sensitivity
        )
        current_il_value = base_value * current_il_fraction

        current_lp_value = base_value + segment_fee_cum + current_il_value

        # Rebalance decision
        if strategy.should_rebalance(current_price=current_price, step=t):
            rebalanced[t] = True

            cost_t = (
    strategy.transaction_cost(current_lp_value)
    if sim_config.include_rebalancing_costs
    else 0.0
)
            rebalance_cost[t] = cost_t
            total_rebalance_cost += cost_t
            current_lp_value -= cost_t

            # Reset the LP around the new center
            strategy.rebalance(new_center_price=current_price)

            # New segment starts from current value
            base_value = current_lp_value
            reference_price = current_price
            segment_fee_cum = 0.0

            # After rebalance, local IL resets
            current_il_fraction = 0.0
            current_il_value = 0.0

        cum_rebalance_cost[t] = total_rebalance_cost
        il_fraction[t] = current_il_fraction
        il_value[t] = current_il_value
        lp_value[t] = current_lp_value

        hodl_value[t] = hodl_units * current_price
        hodl_pnl[t] = hodl_value[t] - initial_capital

        net_pnl[t] = lp_value[t] - initial_capital
        lp_minus_hodl[t] = lp_value[t] - hodl_value[t]

    # Fill any uninitialized benchmark slots consistently
    net_pnl[0] = 0.0
    hodl_value[0] = initial_capital
    hodl_pnl[0] = 0.0
    lp_minus_hodl[0] = 0.0

    df = pd.DataFrame({
        "step": steps,
        "price": prices,
        "center_price": center_prices,
        "lower_bound": lower_bounds,
        "upper_bound": upper_bounds,
        "in_range": in_range,
        "rebalanced": rebalanced,
        "fee_step": fee_step,
        "cum_fees": cum_fees,
        "rebalance_cost": rebalance_cost,
        "cum_rebalance_cost": cum_rebalance_cost,
        "il_fraction": il_fraction,
        "il_value": il_value,
        "lp_value": lp_value,
        "hodl_value": hodl_value,
        "net_pnl": net_pnl,
        "hodl_pnl": hodl_pnl,
        "lp_minus_hodl": lp_minus_hodl,
    })

    return df