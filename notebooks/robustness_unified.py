"""
Unified Robustness Analysis for Uniswap v3 LP Strategy Optimization

Tests robustness of optimal LP width across:
1. Transaction costs
2. Random seeds
3. Time horizons

Outputs:
- CSV summary
- Robustness plots with error bars
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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

SIGMAS = [0.6]
SEEDS = [42, 123, 999]
HORIZONS = [1.0, 2.0]

COST_REGIMES = [
    (1.0, 0.00025),
    (2.0, 0.00050),  # baseline
    (5.0, 0.00100),
]

WIDTH_GRID = np.round(np.arange(0.10, 0.31, 0.02), 3)
N_PATHS = 100

OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------
# Core robustness engine
# ---------------------------------------------------------------------

def run_robustness():

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

    for sigma in SIGMAS:
        for T in HORIZONS:
            for seed in SEEDS:

                gbm_cfg = GBMConfig(
                    s0=2000.0,
                    mu=0.05,
                    sigma=sigma,
                    t_horizon=T,
                    n_steps=int(252 * T),  # ✅ FIXED
                    n_paths=N_PATHS,
                    seed=seed,
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
                        "sigma": sigma,
                        "T": T,
                        "seed": seed,
                        "gas_cost": gas_cost,
                        "slippage_coeff": slippage_coeff,

                        # baseline flag
                        "is_baseline": (
                            gas_cost == 2.0 and
                            slippage_coeff == 0.0005 and
                            seed == 42 and
                            T == 1.0
                        ),

                        "optimal_width": best["width_pct"],
                        "best_score": best["objective"],
                        "mean_objective": best["mean_objective"],
                        "std_objective": best["std_objective"],
                        "mean_n_rebalances": best["mean_n_rebalances"],
                        "mean_lp_minus_hodl": best["mean_lp_minus_hodl"],
                        "prob_underperform_hodl": best["prob_underperform_hodl"],
                    })

    df = pd.DataFrame(rows)

    out_csv = OUTPUT_DIR / "robustness_unified.csv"
    df.to_csv(out_csv, index=False)

    print(f"\nSaved results to: {out_csv}")
    print(df.head())

    return df

# ---------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------

def plot_robustness(df):

    # --- COST SENSITIVITY (with error bars) ---
    df_cost = (
        df.groupby(["gas_cost", "slippage_coeff"])["optimal_width"]
        .agg(["mean", "std"])
        .reset_index()
    )

    plt.figure()
    x = range(len(df_cost))

    plt.errorbar(x, df_cost["mean"], yerr=df_cost["std"], marker="o")

    plt.xticks(
        x,
        [f"gas={r.gas_cost}\nslip={r.slippage_coeff}" for _, r in df_cost.iterrows()]
    )

    plt.ylabel("Optimal Width")
    plt.title("Optimal Width vs Transaction Costs")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "robustness_costs.png")
    plt.close()

    # --- COST vs PERFORMANCE ---
    df_perf = (
        df.groupby(["gas_cost", "slippage_coeff"])["mean_lp_minus_hodl"]
        .mean()
        .reset_index()
    )

    plt.figure()
    x = range(len(df_perf))

    plt.plot(x, df_perf["mean_lp_minus_hodl"], marker="o")

    plt.xticks(
        x,
        [f"gas={r.gas_cost}\nslip={r.slippage_coeff}" for _, r in df_perf.iterrows()]
    )

    plt.ylabel("LP vs HODL")
    plt.title("Performance vs Transaction Costs")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "robustness_performance_costs.png")
    plt.close()

    # --- SEED STABILITY ---
    df_seed = df.groupby("seed")["optimal_width"].agg(["mean", "std"]).reset_index()

    plt.figure()
    plt.errorbar(df_seed["seed"], df_seed["mean"], yerr=df_seed["std"], marker="o")

    plt.xlabel("Seed")
    plt.ylabel("Optimal Width")
    plt.title("Optimal Width vs Random Seed")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "robustness_seeds.png")
    plt.close()

    # --- HORIZON SENSITIVITY ---
    df_T = df.groupby("T")["optimal_width"].agg(["mean", "std"]).reset_index()

    plt.figure()
    plt.errorbar(df_T["T"], df_T["mean"], yerr=df_T["std"], marker="o")

    plt.xlabel("Time Horizon (years)")
    plt.ylabel("Optimal Width")
    plt.title("Optimal Width vs Time Horizon")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "robustness_horizon.png")
    plt.close()

    print("Saved all robustness plots to outputs/")

# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------

if __name__ == "__main__":
    df = run_robustness()
    plot_robustness(df)