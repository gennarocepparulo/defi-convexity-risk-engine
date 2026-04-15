from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
# Ensure project root in path
# ---------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis.lp_minus_hodl import simulate_lp_minus_hodl
from src.stochastic.price_process import GBMConfig, simulate_gbm_paths
from src.stochastic.fee_model import FeeModelConfig
from src.stochastic.lp_path_simulator import LPSimulationConfig
from src.strategy.uniswap_v3 import LPStrategyConfig, UniswapV3Strategy


# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
SIGMA = 0.4
N_PATHS = 50
WIDTH = 0.20
INITIAL_CAPITAL = 1000.0

OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------
# CORE EXPERIMENT
# ---------------------------------------------------------------------
def run_experiment(fee_tier, rebalance_policy):
    gbm_cfg = GBMConfig(
        s0=2000.0,
        mu=0.0,
        sigma=SIGMA,
        t_horizon=1.0,
        n_steps=252,
        n_paths=N_PATHS,
        seed=42,
    )

    paths = simulate_gbm_paths(gbm_cfg)

    increments_all = []
    final_pnl = []

    # IMPORTANT: each column is one path
    for i in range(paths.shape[1]):
        path = paths[:, i]

        strategy = UniswapV3Strategy(
            LPStrategyConfig(
                center_price=path[0],
                width_pct=WIDTH,
                rebalance_policy=rebalance_policy,
                rebalance_threshold=0.05,
                gas_cost=1.0,
                slippage_coeff=0.001,
                capital=INITIAL_CAPITAL,
            )
        )

        fee_cfg = FeeModelConfig(
            fee_tier=fee_tier,
            volume_multiplier=8.0,
            liquidity_share=1.0,
            reference_width=0.25,
            alpha=0.7,
        )

        sim_cfg = LPSimulationConfig(
            initial_capital=INITIAL_CAPITAL,
            include_rebalancing_costs=True,
        )

        df = simulate_lp_minus_hodl(
            prices=path,
            strategy=strategy,
            fee_config=fee_cfg,
            sim_config=sim_cfg,
        )

       
        increments = df["lp_minus_hodl"].diff().dropna()
        increments_all.append(float(increments.mean()))
        final_pnl.append(float(df["lp_minus_hodl"].iloc[-1]))

    return {
        "mean_increment": float(np.mean(increments_all)),
        "mean_final_pnl": float(np.mean(final_pnl)),
        "std_final_pnl": float(np.std(final_pnl)),
        "prob_positive": float(np.mean(np.array(final_pnl) > 0)),
    }

def plot_pnl_distribution(final_pnl, scenario_name):
    import matplotlib.pyplot as plt
    import numpy as np

    plt.figure(figsize=(7, 4))

    plt.hist(final_pnl, bins=40, density=True, alpha=0.7)
    plt.axvline(0, linestyle="--", linewidth=1)

    plt.title(f"LP - HODL Distribution ({scenario_name})")
    plt.xlabel("LP - HODL")
    plt.ylabel("Density")
    plt.grid(True)
    plt.tight_layout()

    filename = scenario_name.lower().replace(" ", "_").replace("/", "")
    plt.savefig(f"outputs/pnl_distribution_{filename}.png", dpi=150)
    plt.close()
# ---------------------------------------------------------------------
# RUN ALL CASES
# ---------------------------------------------------------------------
def run_all():
    results = []

    scenarios = [
        ("Zero Fees / No Rebal", 0.0, "none"),
        ("Fees / No Rebal", 0.003, "none"),
        ("Fees / Rebal", 0.003, "out_of_range"),
    ]

    for name, fee, rebal in scenarios:
        res = run_experiment(fee, rebal)
        res["scenario"] = name
        results.append(res)

    df = pd.DataFrame(results)

    print("\n=== Martingale Test Results ===")
    print(df)

    df.to_csv(OUTPUT_DIR / "martingale_test_results.csv", index=False)
    return df


# ---------------------------------------------------------------------
# PLOT
# ---------------------------------------------------------------------
def plot_example_path():
    gbm_cfg = GBMConfig(
        s0=2000.0,
        mu=0.0,
        sigma=SIGMA,
        t_horizon=1.0,
        n_steps=252,
        n_paths=1,
        seed=42,
    )

    path = simulate_gbm_paths(gbm_cfg)[:, 0]

    strategy = UniswapV3Strategy(
        LPStrategyConfig(
            center_price=path[0],
            width_pct=WIDTH,
            rebalance_policy="out_of_range",
            gas_cost=1.0,
            slippage_coeff=0.001,
            capital=INITIAL_CAPITAL,
        )
    )

    fee_cfg = FeeModelConfig(
        fee_tier=0.003,
        volume_multiplier=8.0,
        liquidity_share=1.0,
        reference_width=0.25,
        alpha=0.7,
    )

    sim_cfg = LPSimulationConfig(
        initial_capital=INITIAL_CAPITAL,
        include_rebalancing_costs=True,
    )

    df = simulate_lp_minus_hodl(
        prices=path,
        strategy=strategy,
        fee_config=fee_cfg,
        sim_config=sim_cfg,
    )

    plt.figure(figsize=(9, 4))

    plt.plot(df["step"], df["lp_minus_hodl"], label="LP - HODL")

    # Zero line
    plt.axhline(0, linestyle="--", linewidth=1)

    # Highlight negative region
    plt.fill_between(
        df["step"],
        df["lp_minus_hodl"],
        0,
        where=(df["lp_minus_hodl"] < 0),
        alpha=0.2,
    )

    plt.title("LP Relative Performance (Example Path)")
    plt.xlabel("Step")
    plt.ylabel("LP - HODL")

    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / "martingale_example_path.png", dpi=150)
    plt.close()

# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------
if __name__ == "__main__":
    run_all()
    plot_example_path()
