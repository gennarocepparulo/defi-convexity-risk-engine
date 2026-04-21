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
# OPTIMAL PARAMETERS (FROM YOUR GRID)
# ---------------------------------------------------------------------
WIDTH = 0.30
THRESHOLD = 0.30

SIGMA = 0.4
INITIAL_CAPITAL = 1_000.0
N_PATHS = 3000
N_STEPS = 252

FEE_TIER = 0.003
GAS_COST = 1.0
SLIPPAGE_COEFF = 0.001

OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------
# MAIN SIMULATION
# ---------------------------------------------------------------------
def run_optimal_simulation():

    print("\nRunning optimal policy simulation...\n")

    gbm_cfg = GBMConfig(
        s0=2000.0,
        mu=0.0,
        sigma=SIGMA,
        t_horizon=1.0,
        n_steps=N_STEPS,
        n_paths=N_PATHS,
        seed=123,
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
                width_pct=WIDTH,
                rebalance_policy="threshold",
                rebalance_threshold=THRESHOLD,
                gas_cost=GAS_COST,
                slippage_coeff=SLIPPAGE_COEFF,
                capital=INITIAL_CAPITAL,
            )
        )

        fee_cfg = FeeModelConfig(
            fee_tier=FEE_TIER,
            volume_multiplier=8.0,
            liquidity_share=1.0,
            reference_width=WIDTH,
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
        rebalances.append(df["rebalanced"].sum())

    return np.array(pnl), np.array(fees), np.array(rebalances)


# ---------------------------------------------------------------------
# PLOTS
# ---------------------------------------------------------------------
def plot_histogram(pnl):

    plt.figure()
    plt.hist(pnl, bins=50)

    plt.axvline(pnl.mean(), linestyle="--")
    plt.axvline(0.0)

    plt.title("Optimal Policy: LP − HODL Distribution")
    plt.xlabel("LP − HODL")
    plt.ylabel("Frequency")

    plt.grid(True)

    plt.savefig("outputs/optimal_policy_histogram.png")
    plt.close()


def plot_diagnostics(fees, rebalances):

    # Fees distribution
    plt.figure()
    plt.hist(fees, bins=50)
    plt.title("Fee Distribution (Optimal Policy)")
    plt.xlabel("Cumulative Fees")
    plt.grid(True)
    plt.savefig("outputs/optimal_policy_fees.png")
    plt.close()

    # Rebalancing distribution
    plt.figure()
    plt.hist(rebalances, bins=30)
    plt.title("Rebalancing Count Distribution")
    plt.xlabel("Number of Rebalances")
    plt.grid(True)
    plt.savefig("outputs/optimal_policy_rebalances.png")
    plt.close()


# ---------------------------------------------------------------------
# SUMMARY STATS
# ---------------------------------------------------------------------
def print_summary(pnl, fees, rebalances):

    print("\n=== OPTIMAL POLICY RESULTS ===\n")

    print(f"Mean LP - HODL: {np.mean(pnl):.2f}")
    print(f"Std LP - HODL: {np.std(pnl):.2f}")
    print(f"Prob (LP > HODL): {(pnl > 0).mean():.2%}")

    print("\n--- Fees ---")
    print(f"Mean Fees: {np.mean(fees):.2f}")

    print("\n--- Rebalancing ---")
    print(f"Mean # Rebalances: {np.mean(rebalances):.2f}")

    print("\nResults saved in /outputs")


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------
if __name__ == "__main__":

    pnl, fees, rebalances = run_optimal_simulation()

    plot_histogram(pnl)
    plot_diagnostics(fees, rebalances)
    print_summary(pnl, fees, rebalances)