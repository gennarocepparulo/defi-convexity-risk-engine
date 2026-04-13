"""
# Exploratory cost‑only robustness check.
# Superseded by robustness_unified.py

Robustness Analysis: Transaction Cost Sensitivity

This script studies how the optimal Uniswap v3 LP range width
changes as transaction costs (gas + slippage) vary.

The goal is to assess whether the optimal width is robust
or shifts systematically under higher operational friction.
"""

from pathlib import Path
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------
# Ensure project root is on PYTHONPATH
# ---------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.stochastic.price_process import GBMConfig, simulate_gbm_paths
from src.stochastic.fee_model import FeeModelConfig
from src.stochastic.lp_path_simulator import LPSimulationConfig
from src.optimization.grid_search import optimize_width_grid_mc
from src.optimization.objective import expected_net_return

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

# Cost regimes: (gas_cost, slippage_coeff)
COST_REGIMES = [
    (1.0, 0.00025),   # low friction
    (2.0, 0.00050),   # baseline
    (5.0, 0.00100),   # high friction
]

SIGMA = 0.6
SEED = 42
T = 1.0
N_PATHS = 100

WIDTH_GRID = np.round(np.arange(0.10, 0.31, 0.02), 3)

OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------

def plot_cost_sensitivity(summary_df, output_dir):
    plt.figure(figsize=(7, 4))

    cost_index = range(len(summary_df))

    plt.plot(
        cost_index,
        summary_df["optimal_width"],
        marker="o"
    )

    plt.xticks(
        cost_index,
        [
            f"gas={row.gas_cost}\nslip={row.slippage_coeff}"
            for _, row in summary_df.iterrows()
        ]
    )

    plt.title("Optimal LP Width vs Transaction Costs")
    plt.xlabel("Cost Regime")
    plt.ylabel("Optimal Width")
    plt.grid(True)

    out_path = output_dir / "optimal_width_vs_cost.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    print(f"Saved plot to: {out_path}")

# ---------------------------------------------------------------------
# Main robustness analysis
# ---------------------------------------------------------------------

def run_cost_sensitivity():

    rows = []

    fee_cfg = FeeModelConfig(
        fee_tier=0.003,
        volume_multiplier=8.0,
        liquidity_share=1.0,
        reference_width=0.25,
        alpha=0.7,
        min_width=0.03,
        min_fee_multiplier=0.50,
        max_fee_multiplier=3.50,
    )

    sim_cfg = LPSimulationConfig(
        initial_capital=1000.0,
        il_sensitivity=1.0,
        include_rebalancing_costs=True,
    )

    gbm_cfg = GBMConfig(
        s0=2000.0,
        mu=0.05,
        sigma=SIGMA,
        t_horizon=T,
        n_steps=252,
        n_paths=N_PATHS,
        seed=SEED,
    )

    paths = simulate_gbm_paths(gbm_cfg)

    for gas_cost, slippage_coeff in COST_REGIMES:

        results = optimize_width_grid_mc(
            paths=paths,
            center_price=gbm_cfg.s0,
            width_grid=WIDTH_GRID,
            objective_fn=expected_net_return,
            fee_config=fee_cfg,
            sim_config=sim_cfg,
            base_strategy_kwargs={
                "rebalance_policy": "out_of_range",
                "gas_cost": gas_cost,
                "slippage_coeff": slippage_coeff,
            },
            score_mode="sharpe_like",
        )

        best = results.iloc[0]

        rows.append({
    "sigma": SIGMA,
    "T": T,
    "seed": SEED,
    "gas_cost": gas_cost,
    "slippage_coeff": slippage_coeff,
    "optimal_width": best["width_pct"],
    "best_score": best["objective"],
    "mean_objective": best["mean_objective"],
    "std_objective": best["std_objective"],
    "mean_time_in_range": best["mean_time_in_range"],
    "mean_n_rebalances": best["mean_n_rebalances"],
    "mean_cum_fees": best["mean_cum_fees"],
    "mean_lp_minus_hodl": best["mean_lp_minus_hodl"],
    "prob_underperform_hodl": best["prob_underperform_hodl"],
})