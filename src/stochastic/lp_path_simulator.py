from dataclasses import dataclass
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
    Constant-product impermanent loss proxy.

    IL(R) = 2 * sqrt(R) / (1 + R) - 1

    This represents RELATIVE underperformance vs HODL,
    NOT principal decay.
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

    ECONOMICALLY CORRECT ACCOUNTING:
    - LP principal is fixed (does NOT decay)
    - Impermanent loss is a relative PnL term vs HODL
    - Rebalancing resets IL reference, not capital
    """

    n = len(prices)
    if n < 2:
        raise ValueError("prices must contain at least two observations")

    initial_price = float(prices[0])
    initial_capital = float(sim_config.initial_capital)

    # ------------------------------------------------------------------
    # Output arrays
    # ------------------------------------------------------------------
    steps = np.arange(n)
    center_prices = np.zeros(n)
    lower_bounds = np.zeros(n)
    upper_bounds = np.zeros(n)

    in_range = np.zeros(n, dtype=bool)
    rebalanced = np.zeros(n, dtype=bool)

    fee_step = np.zeros(n)
    cum_fees = np.zeros(n)

    rebalance_cost = np.zeros(n)
    cum_rebalance_cost = np.zeros(n)

    il_fraction = np.zeros(n)
    il_value = np.zeros(n)

    lp_value = np.zeros(n)
    hodl_value = np.zeros(n)
    net_pnl = np.zeros(n)
    hodl_pnl = np.zeros(n)
    lp_minus_hodl = np.zeros(n)

    # ------------------------------------------------------------------
    # HODL benchmark
    # ------------------------------------------------------------------
    hodl_units = initial_capital / initial_price
    hodl_value[0] = initial_capital
    hodl_pnl[0] = 0.0

    # ------------------------------------------------------------------
    # ✅ LP ACCOUNTING (CORRECT)
    # ------------------------------------------------------------------
    lp_principal = initial_capital        # FIXED principal
    reference_price = initial_price       # IL reference (resets on rebalance)
    segment_fee_cum = 0.0
    total_fee_cum = 0.0
    total_rebalance_cost = 0.0

    # Initial state
    center_prices[0] = strategy.config.center_price
    lower_bounds[0] = strategy.lower_bound
    upper_bounds[0] = strategy.upper_bound
    in_range[0] = strategy.is_in_range(initial_price)

    lp_value[0] = initial_capital
    lp_minus_hodl[0] = 0.0

    # ------------------------------------------------------------------
    # Simulation loop
    # ------------------------------------------------------------------
    for t in range(1, n):
        current_price = float(prices[t])
        prev_price = float(prices[t - 1])

        center_prices[t] = strategy.config.center_price
        lower_bounds[t] = strategy.lower_bound
        upper_bounds[t] = strategy.upper_bound
        in_range[t] = strategy.is_in_range(current_price)

        # -------------------------
        # Fees
        # -------------------------
        fee_fraction_t = estimate_fee_for_step(
            prev_price=prev_price,
            current_price=current_price,
            in_range=bool(in_range[t]),
            width_pct=strategy.config.width_pct,
            config=fee_config
        )

        fee_value_t = lp_principal * fee_fraction_t
        fee_step[t] = fee_value_t
        segment_fee_cum += fee_value_t
        total_fee_cum += fee_value_t
        cum_fees[t] = total_fee_cum

        # -------------------------
        # Impermanent loss (PnL term)
        # -------------------------
        ratio = current_price / max(reference_price, 1e-12)
        current_il_fraction = (
            approximate_impermanent_loss(ratio) * sim_config.il_sensitivity
        )

        # ✅ IL is relative vs HODL, NOT principal decay
        current_il_value = initial_capital * current_il_fraction

        current_lp_value = (
            lp_principal
            + segment_fee_cum
            + current_il_value
        )

        # -------------------------
        # Rebalance
        # -------------------------
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

            # ✅ Reset IL reference, NOT principal
            reference_price = current_price
            segment_fee_cum = 0.0
            current_il_fraction = 0.0
            current_il_value = 0.0

        # -------------------------
        # Accounting
        # -------------------------
        cum_rebalance_cost[t] = total_rebalance_cost
        il_fraction[t] = current_il_fraction
        il_value[t] = current_il_value
        lp_value[t] = current_lp_value

        hodl_value[t] = hodl_units * current_price
        hodl_pnl[t] = hodl_value[t] - initial_capital

        net_pnl[t] = lp_value[t] - initial_capital
        lp_minus_hodl[t] = lp_value[t] - hodl_value[t]

    # Cleanup first step
    net_pnl[0] = 0.0
    hodl_value[0] = initial_capital
    hodl_pnl[0] = 0.0
    lp_minus_hodl[0] = 0.0

    return pd.DataFrame({
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