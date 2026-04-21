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
# GLOBAL PARAMETERS
# ---------------------------------------------------------------------
SIGMA = 0.4
INITIAL_CAPITAL = 1_000.0
N_PATHS = 1000
N_STEPS = 252

FEE_TIER = 0.003
GAS_COST = 1.0
SLIPPAGE_COEFF = 0.001

OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------
# CORE SIMULATION FUNCTION
# ---------------------------------------------------------------------
def run_experiment(width, threshold):

    gbm_cfg = GBMConfig(
        s0=2000.0,
        mu=0.0,
        sigma=SIGMA,
        t_horizon=1.0,
        n_steps=N_STEPS,
        n_paths=N_PATHS,
        seed=42,
    )

    paths = simulate_gbm_paths(gbm_cfg)

    pnl = []
    fees = []
    rebalances = []

    for i in range(paths.shape[1]):
        prices = paths[:, i]

        strategy = UniswapV3Strategy(
            LPStrategyConfig(
                center_price=prices[0],
                width_pct=width,
                rebalance_policy="threshold",
                rebalance_threshold=threshold,
                gas_cost=GAS_COST,
                slippage_coeff=SLIPPAGE_COEFF,
                capital=INITIAL_CAPITAL,
            )
        )

        fee_cfg = FeeModelConfig(
            fee_tier=FEE_TIER,
            volume_multiplier=8.0,
            liquidity_share=1.0,
            reference_width=width,
            alpha=0.7,
        )

        sim_cfg = LPSimulationConfig(
            initial_capital=INITIAL_CAPITAL,
            include_rebalancing_costs=True,
        )

        df = simulate_lp_minus_hodl(
            prices=prices,
            strategy=strategy,
            fee_config=fee_cfg,
            sim_config=sim_cfg,
        )

        pnl.append(df["lp_minus_hodl"].iloc[-1])
        fees.append(df["cum_fees"].iloc[-1])
        rebalances.append(df["rebalanced"].sum())  # ✅ FIXED

    return {
        "mean_lp_minus_hodl": np.mean(pnl),
        "mean_cum_fees": np.mean(fees),
        "mean_n_rebalances": np.mean(rebalances),
    }


# ---------------------------------------------------------------------
# GRID SWEEP
# ---------------------------------------------------------------------
def run_grid():

    WIDTHS = [0.05, 0.10, 0.20, 0.30]
    THRESHOLDS = np.linspace(0.01, 0.30, 10)

    results = []

    for w in WIDTHS:
        for th in THRESHOLDS:
            print(f"Running width={w}, threshold={th:.3f}")

            res = run_experiment(w, th)

            res["width"] = w
            res["threshold"] = th

            # Jensen proxy
            res["jensen_proxy"] = (
                res["mean_lp_minus_hodl"] - res["mean_cum_fees"]
            )

            results.append(res)

    df = pd.DataFrame(results)

    df.to_csv(OUTPUT_DIR / "width_threshold_grid.csv", index=False)

    return df


# ---------------------------------------------------------------------
# HEATMAP PLOT
# ---------------------------------------------------------------------
def plot_heatmap(df):

    pivot = df.pivot(
        index="width",
        columns="threshold",
        values="mean_lp_minus_hodl"
    )

    plt.figure(figsize=(10, 6))

    im = plt.imshow(pivot, aspect="auto")

    plt.colorbar(im, label="LP - HODL")

    plt.xticks(
        ticks=np.arange(len(pivot.columns)),
        labels=[f"{t:.2f}" for t in pivot.columns],
        rotation=45
    )

    plt.yticks(
        ticks=np.arange(len(pivot.index)),
        labels=[f"{w:.2f}" for w in pivot.index]
    )

    plt.xlabel("Rebalancing Threshold")
    plt.ylabel("Width")
    plt.title("LP Performance Heatmap (Width vs Threshold)")

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "heatmap_width_threshold.png")
    plt.close()


# ---------------------------------------------------------------------
# BEST PARAMETER EXTRACTION
# ---------------------------------------------------------------------
def find_optimum(df):

    best = df.loc[df["mean_lp_minus_hodl"].idxmax()]

    print("\n=== GLOBAL OPTIMUM ===")
    print(best)


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------
if __name__ == "__main__":

    df = run_grid()

    print("\n=== GRID RESULTS ===")
    print(df.head())

    plot_heatmap(df)
    find_optimum(df)

    print("\nHeatmap saved to outputs/heatmap_width_threshold.png")