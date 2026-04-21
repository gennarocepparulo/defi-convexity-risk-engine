from dataclasses import dataclass
import numpy as np
import pandas as pd

from src.strategy.uniswap_v3 import UniswapV3Strategy
from src.stochastic.fee_model import FeeModelConfig, estimate_fee_for_step
from src.lp_model import value_lp


# --------------------------------------------------
# Config
# --------------------------------------------------
@dataclass
class LPSimulationConfig:
    initial_capital: float = 1_000.0
    include_rebalancing_costs: bool = True


# --------------------------------------------------
# Helper: liquidity from capital
# --------------------------------------------------
def liquidity_from_capital(price, lower, upper, capital):
    unit_value = value_lp(price, lower, upper, 1.0)

    if unit_value <= 0:
        raise ValueError("Invalid LP valuation for liquidity inference")

    return capital / unit_value


# --------------------------------------------------
# Main simulation
# --------------------------------------------------
def simulate_lp_strategy(
    prices: np.ndarray,
    strategy: UniswapV3Strategy,
    fee_config: FeeModelConfig,
    sim_config: LPSimulationConfig
) -> pd.DataFrame:

    n = len(prices)
    initial_price = float(prices[0])
    initial_capital = float(sim_config.initial_capital)

    # --- arrays ---
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

    lp_value = np.zeros(n)
    hodl_value = np.zeros(n)
    lp_minus_hodl = np.zeros(n)

    # --- HODL ---
    hodl_units = initial_capital / initial_price
    hodl_value[0] = initial_capital

    # --- initial LP ---
    liquidity = liquidity_from_capital(
        initial_price,
        strategy.lower_bound,
        strategy.upper_bound,
        initial_capital
    )

    fee_buffer = 0.0
    total_fee_cum = 0.0
    total_rebalance_cost = 0.0

    lp_value[0] = initial_capital

    # --------------------------------------------------
    # LOOP
    # --------------------------------------------------
    for t in range(1, n):

        price = float(prices[t])
        prev_price = float(prices[t - 1])

        # --- state ---
        center_prices[t] = strategy.config.center_price
        lower_bounds[t] = strategy.lower_bound
        upper_bounds[t] = strategy.upper_bound
        in_range[t] = strategy.is_in_range(price)

        # --------------------------------------------------
        # FEES
        # --------------------------------------------------
        fee_fraction = estimate_fee_for_step(
            prev_price=prev_price,
            current_price=price,
            in_range=bool(in_range[t]),
            width_pct=strategy.config.width_pct,
            config=fee_config,
        )

        fee = lp_value[t - 1] * fee_fraction
        fee_buffer += fee
        total_fee_cum += fee

        fee_step[t] = fee
        cum_fees[t] = total_fee_cum

        # --------------------------------------------------
        # LP VALUE
        # --------------------------------------------------
        lp_mark = value_lp(
            price,
            strategy.lower_bound,
            strategy.upper_bound,
            liquidity
        )

        current_lp_value = lp_mark + fee_buffer

        # --------------------------------------------------
        # REBALANCE (FIXED)
        # --------------------------------------------------
        if strategy.should_rebalance(price, t):

            rebalanced[t] = True

            # cost
            cost = (
                strategy.transaction_cost(current_lp_value)
                if sim_config.include_rebalancing_costs
                else 0.0
            )

            current_lp_value -= cost
            total_rebalance_cost += cost
            rebalance_cost[t] = cost

            # --- move range ---
            strategy.config.center_price = price

            # --- recompute liquidity ---
            liquidity = liquidity_from_capital(
                price,
                strategy.lower_bound,
                strategy.upper_bound,
                current_lp_value
            )

            # --- reset fee buffer ---
            fee_buffer = 0.0

        cum_rebalance_cost[t] = total_rebalance_cost

        # --------------------------------------------------
        # FINAL ACCOUNTING
        # --------------------------------------------------
        lp_value[t] = current_lp_value
        hodl_value[t] = hodl_units * price
        lp_minus_hodl[t] = lp_value[t] - hodl_value[t]

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
        "lp_value": lp_value,
        "hodl_value": hodl_value,
        "lp_minus_hodl": lp_minus_hodl,
    })