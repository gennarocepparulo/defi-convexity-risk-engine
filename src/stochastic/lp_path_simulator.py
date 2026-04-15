from dataclasses import dataclass
import numpy as np
import pandas as pd

from src.strategy.uniswap_v3 import UniswapV3Strategy
from src.stochastic.fee_model import FeeModelConfig, estimate_fee_for_step
from src.lp_model import value_lp


@dataclass
class LPSimulationConfig:
    initial_capital: float = 1_000.0
    include_rebalancing_costs: bool = True


def liquidity_from_capital(price: float, lower: float, upper: float, capital: float) -> float:
    """
    Compute liquidity L such that:
        value_lp(price, lower, upper, L) = capital

    Assumes value_lp is linear in L, which is standard for Uniswap v3 liquidity math.
    """
    unit_value = value_lp(price, lower, upper, 1.0)

    if unit_value <= 0:
        raise ValueError(
            f"Cannot infer liquidity from capital: value_lp({price}, {lower}, {upper}, 1.0) = {unit_value}"
        )

    return capital / unit_value


def simulate_lp_strategy(
    prices: np.ndarray,
    strategy: UniswapV3Strategy,
    fee_config: FeeModelConfig,
    sim_config: LPSimulationConfig
) -> pd.DataFrame:
    """
    Simulate a Uniswap v3 LP strategy along a single price path using
    state-based LP valuation via value_lp(price, lower, upper, L).

    Key design:
    - LP is valued from actual position state, not via an IL approximation
    - Fees accrue as an additive cash component
    - Rebalancing recenters the range and re-solves liquidity L so that
      the LP value at rebalance equals current post-cost capital
    - il_value is reported as LOCAL underperformance relative to a local
      HODL benchmark since the last rebalance
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
    # Global HODL benchmark
    # ------------------------------------------------------------------
    hodl_units = initial_capital / initial_price
    hodl_value[0] = initial_capital
    hodl_pnl[0] = 0.0

    # ------------------------------------------------------------------
    # Initial LP state
    # ------------------------------------------------------------------
    center_prices[0] = strategy.config.center_price
    lower_bounds[0] = strategy.lower_bound
    upper_bounds[0] = strategy.upper_bound
    in_range[0] = strategy.is_in_range(initial_price)

    # Solve initial liquidity so LP value matches initial capital
    liquidity = liquidity_from_capital(
        price=initial_price,
        lower=lower_bounds[0],
        upper=upper_bounds[0],
        capital=initial_capital,
    )

    # Fee buffer = cash-like fees accumulated since last rebalance
    fee_buffer = 0.0
    total_fee_cum = 0.0
    total_rebalance_cost = 0.0

    # Local HODL reference since last rebalance (for il_value reporting)
    local_hodl_units = initial_capital / initial_price

    lp_value[0] = initial_capital
    il_value[0] = 0.0
    il_fraction[0] = 0.0
    lp_minus_hodl[0] = 0.0
    net_pnl[0] = 0.0

    # ------------------------------------------------------------------
    # Simulation loop
    # ------------------------------------------------------------------
    for t in range(1, n):
        current_price = float(prices[t])
        prev_price = float(prices[t - 1])

        # Current strategy state
        center_prices[t] = strategy.config.center_price
        lower_bounds[t] = strategy.lower_bound
        upper_bounds[t] = strategy.upper_bound
        in_range[t] = strategy.is_in_range(current_price)

        # --------------------------------------------------------------
        # Fee accrual for this step
        # --------------------------------------------------------------
        fee_fraction_t = estimate_fee_for_step(
            prev_price=prev_price,
            current_price=current_price,
            in_range=bool(in_range[t]),
            width_pct=strategy.config.width_pct,
            config=fee_config,
        )

        # Accrue fees on current LP value from previous step
        fee_value_t = lp_value[t - 1] * fee_fraction_t
        fee_step[t] = fee_value_t
        fee_buffer += fee_value_t
        total_fee_cum += fee_value_t
        cum_fees[t] = total_fee_cum

        # --------------------------------------------------------------
        # State-based LP valuation
        # --------------------------------------------------------------
        lp_mark_to_market = value_lp(
            current_price,
            lower_bounds[t],
            upper_bounds[t],
            liquidity
        )

        current_lp_value = lp_mark_to_market + fee_buffer

        # --------------------------------------------------------------
        # Local IL reporting: LP state value vs local HODL since last reset
        # --------------------------------------------------------------
        local_hodl_value = local_hodl_units * current_price
        current_il_value = lp_mark_to_market - local_hodl_value
        current_il_fraction = (
            current_il_value / local_hodl_value
            if abs(local_hodl_value) > 1e-12
            else 0.0
        )

        # --------------------------------------------------------------
        # Rebalancing
        # --------------------------------------------------------------
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

            # Recenter the LP range
            strategy.rebalance(new_center_price=current_price)

            # Update state after rebalance
            center_prices[t] = strategy.config.center_price
            lower_bounds[t] = strategy.lower_bound
            upper_bounds[t] = strategy.upper_bound
            in_range[t] = strategy.is_in_range(current_price)

            # Re-solve liquidity so the new LP position equals current capital
            liquidity = liquidity_from_capital(
                price=current_price,
                lower=lower_bounds[t],
                upper=upper_bounds[t],
                capital=current_lp_value,
            )

            # Fees are assumed reinvested into the new LP position
            fee_buffer = 0.0

            # Reset local HODL reference for il_value reporting
            local_hodl_units = current_lp_value / current_price

            # After rebalance, local IL is reset
            current_il_value = 0.0
            current_il_fraction = 0.0

        # --------------------------------------------------------------
        # Global accounting
        # --------------------------------------------------------------
        cum_rebalance_cost[t] = total_rebalance_cost
        il_value[t] = current_il_value
        il_fraction[t] = current_il_fraction

        lp_value[t] = current_lp_value
        hodl_value[t] = hodl_units * current_price
        hodl_pnl[t] = hodl_value[t] - initial_capital
        net_pnl[t] = lp_value[t] - initial_capital
        lp_minus_hodl[t] = lp_value[t] - hodl_value[t]

    # Cleanup first step
    hodl_value[0] = initial_capital
    hodl_pnl[0] = 0.0
    net_pnl[0] = 0.0
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