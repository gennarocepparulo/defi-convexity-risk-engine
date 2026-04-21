from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd

from src.stochastic.price_process import GBMConfig, simulate_gbm_paths
from src.stochastic.fee_model import FeeModelConfig
from src.stochastic.lp_path_simulator import LPSimulationConfig
from src.optimization.grid_search import optimize_width_grid_mc
from src.optimization.objective import expected_net_return


def run_volatility_sweep():
    output_dir = PROJECT_ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)

    sigmas = [0.2, 0.4, 0.6, 0.8]

    # Refined local grid around the currently identified optimum region
    width_grid = np.round(np.arange(0.10, 0.31, 0.02), 3)

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
        include_rebalancing_costs=True,
    )

    summary_rows = []
    all_results = []

    for sigma in sigmas:
        gbm_cfg = GBMConfig(
            s0=2000.0,
            mu=0.05,
            sigma=sigma,
            t_horizon=1.0,
            n_steps=252,
            n_paths=100,
            seed=42,
        )

        paths = simulate_gbm_paths(gbm_cfg)

        results = optimize_width_grid_mc(
            paths=paths,
            center_price=gbm_cfg.s0,
            width_grid=width_grid,
            objective_fn=expected_net_return,
            fee_config=fee_cfg,
            sim_config=sim_cfg,
            base_strategy_kwargs={
                "rebalance_policy": "out_of_range",
                "gas_cost": 2.0,
                "slippage_coeff": 0.0005,
            },
            score_mode="sharpe_like",
        )

        results["sigma"] = sigma
        all_results.append(results)
        # ✅ SAVE PER-SIGMA RESULTS (THIS IS THE MISSING LINK)
        results_path = output_dir / f"results_sigma_{sigma}.csv"
        results.to_csv(results_path, index=False)

        best = results.iloc[0]

        summary_rows.append({
            "sigma": sigma,
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

        print(f"\n=== sigma = {sigma:.2f} ===")
        print(results[[
            "width_pct",
            "objective",
            "mean_objective",
            "std_objective",
            "mean_time_in_range",
            "mean_n_rebalances",
            "mean_cum_fees",
            "mean_lp_minus_hodl",
            "prob_underperform_hodl",
        ]])

    summary_df = pd.DataFrame(summary_rows)
    all_results_df = pd.concat(all_results, ignore_index=True)

    summary_path = output_dir / "volatility_sweep_summary.csv"
    full_path = output_dir / "volatility_sweep_full_results.csv"

    summary_df.to_csv(summary_path, index=False)
    all_results_df.to_csv(full_path, index=False)

    print("\n=== Volatility Sweep Summary ===")
    print(summary_df)
    print(f"\nSaved summary to: {summary_path}")
    print(f"Saved full results to: {full_path}")

    return summary_df, all_results_df


if __name__ == "__main__":
    run_volatility_sweep()
