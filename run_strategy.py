from pathlib import Path
import sys
import yaml
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------
# Ensure project root is on PYTHONPATH
# ---------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.stochastic.price_process import GBMConfig, simulate_gbm_paths
from src.stochastic.fee_model import FeeModelConfig
from src.stochastic.lp_path_simulator import LPSimulationConfig, simulate_lp_strategy
from src.strategy.uniswap_v3 import LPStrategyConfig, UniswapV3Strategy


# ---------------------------------------------------------------------
# Load config
# ---------------------------------------------------------------------

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------
# Run strategy
# ---------------------------------------------------------------------

def run_strategy(cfg):

    # --------------------------------------------------------------
    # Price simulation
    # --------------------------------------------------------------
    steps = int(cfg["simulation"]["steps_per_year"] * cfg["simulation"]["horizon_years"])

    gbm_cfg = GBMConfig(
        s0=cfg["market"]["s0"],
        mu=cfg["market"]["mu"],
        sigma=cfg["market"]["sigma"],
        t_horizon=cfg["simulation"]["horizon_years"],
        n_steps=steps,
        n_paths=cfg["simulation"]["n_paths"],
        seed=cfg["simulation"]["seed"],
    )

    paths = simulate_gbm_paths(gbm_cfg)

    # --------------------------------------------------------------
    # Fee model
    # --------------------------------------------------------------
    fee_cfg = FeeModelConfig(
        fee_tier=cfg["fees"]["fee_tier"],
        volume_multiplier=cfg["fees"]["volume_multiplier"],
        liquidity_share=cfg["fees"]["liquidity_share"],
        reference_width=cfg["fees"]["reference_width"],
        alpha=cfg["fees"]["alpha"],
        min_width=cfg["fees"].get("min_width", 0.03),
        min_fee_multiplier=cfg["fees"].get("min_fee_multiplier", 0.5),
        max_fee_multiplier=cfg["fees"].get("max_fee_multiplier", 3.5),
    )

    # --------------------------------------------------------------
    # Simulation config (capital handled INSIDE engine)
    # --------------------------------------------------------------
    sim_cfg = LPSimulationConfig(
        initial_capital=cfg["capital"]["initial_capital"],
        include_rebalancing_costs=True,
    )

    results = []

    # --------------------------------------------------------------
    # Monte Carlo loop (ONE STRATEGY PER PATH)
    # --------------------------------------------------------------
    for i in range(paths.shape[0]):
        prices = paths[i]

        # IMPORTANT: fresh strategy config PER PATH
        strat_cfg = LPStrategyConfig(
            center_price=prices[0],
            width_pct=cfg["strategy"]["width_pct"],
            rebalance_policy=cfg["strategy"]["rebalance_policy"],
            gas_cost=cfg["costs"]["gas_cost"],
            slippage_coeff=cfg["costs"]["slippage_coeff"],
            min_width_for_costs=cfg["costs"].get("min_width_for_costs", 0.03),
            capital=cfg["capital"]["initial_capital"],
        )

        strategy = UniswapV3Strategy(strat_cfg)

        sim_df = simulate_lp_strategy(
            prices=prices,
            strategy=strategy,
            fee_config=fee_cfg,
            sim_config=sim_cfg,
        )

        # ✅ Correct capital-consistent comparison
        final_lp = sim_df["lp_value"].iloc[-1]
        final_hodl = sim_df["hodl_value"].iloc[-1]

        results.append({
            "lp_final": final_lp,
            "hodl_final": final_hodl,
            "lp_minus_hodl": final_lp - final_hodl,
        })

    df = pd.DataFrame(results)

    # --------------------------------------------------------------
    # Summary statistics
    # --------------------------------------------------------------
    summary = {
        "mean_lp": df["lp_final"].mean(),
        "mean_hodl": df["hodl_final"].mean(),
        "mean_lp_minus_hodl": df["lp_minus_hodl"].mean(),
        "std_lp_minus_hodl": df["lp_minus_hodl"].std(),
        "prob_underperform": (df["lp_minus_hodl"] < 0).mean(),
    }

    print("\n=== Strategy Performance ===")
    for k, v in summary.items():
        print(f"{k:25s}: {v:,.4f}")

    return df, summary


# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------

if __name__ == "__main__":
    cfg = load_config()
    run_strategy(cfg)