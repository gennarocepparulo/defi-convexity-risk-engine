# ---------------------------------------------------------------------
# Volatility-driven Rebalancing Analysis (Friday)
# ---------------------------------------------------------------------

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


def plot_lp_vs_hodl_distribution(lp_minus_hodl_list, sigma):

    plt.figure()

    plt.hist(lp_minus_hodl_list, bins=50)

    # Reference line at 0
    plt.axvline(0, linestyle="--", label="Break-even")

    # Mean & median (🔥 important)
    plt.axvline(np.mean(lp_minus_hodl_list), linestyle="--", label="Mean")
    plt.axvline(np.median(lp_minus_hodl_list), linestyle=":", label="Median")

    plt.title(f"LP vs HODL Distribution (σ={sigma})")
    plt.xlabel("LP - HODL")
    plt.ylabel("Frequency")

    plt.legend()
    plt.grid(True)

    plt.savefig(OUTPUT_DIR / f"lp_vs_hodl_distribution_sigma_{sigma}.png")
    plt.close()

# ---------------------------------------------------------------------
# FIXED STRATEGY PARAMETERS
# ---------------------------------------------------------------------
WIDTH = 0.20
THRESHOLD = 0.10

INITIAL_CAPITAL = 1_000.0
N_PATHS = 2000
N_STEPS = 252

FEE_TIER = 0.003
GAS_COST = 1.0
SLIPPAGE_COEFF = 0.001

SIGMAS = [0.2, 0.4, 0.6, 0.8]

OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------
# Run simulation for a given volatility
# ---------------------------------------------------------------------
def run_sigma_experiment(sigma):

      
    print(f"Running sigma = {sigma}")

    gbm_cfg = GBMConfig(
        s0=2000.0,
        mu=0.0,
        sigma=sigma,
        t_horizon=1.0,
        n_steps=N_STEPS,
        n_paths=N_PATHS,
        seed=42,
    )

    paths = simulate_gbm_paths(gbm_cfg)

    lp_minus_hodl = []
    cum_fees = []
    n_rebalances = []

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

        lp_minus_hodl.append(df["lp_minus_hodl"].iloc[-1])
        cum_fees.append(df["cum_fees"].iloc[-1])

        

        # ✅ FIX: correct column name
        n_rebalances.append(df["rebalanced"].sum())

         # 🔥 ADD THIS LINE HERE (outside loop)
    plot_lp_vs_hodl_distribution(lp_minus_hodl, sigma)

    return {
        "sigma": sigma,
        "mean_lp_minus_hodl": np.mean(lp_minus_hodl),
        "mean_cum_fees": np.mean(cum_fees),
        "mean_n_rebalances": np.mean(n_rebalances),
    }


# ---------------------------------------------------------------------
# Run full volatility sweep
# ---------------------------------------------------------------------
def run_volatility_analysis():

    results = []

    for sigma in SIGMAS:
        res = run_sigma_experiment(sigma)
        results.append(res)

    df = pd.DataFrame(results)

    # Jensen proxy (convexity drag)
    df["jensen_proxy"] = (
        df["mean_lp_minus_hodl"] - df["mean_cum_fees"]
    )

    df.to_csv(OUTPUT_DIR / "volatility_rebalancing_analysis.csv", index=False)

    print("\n=== Volatility Analysis ===")
    print(df)

    return df


# ---------------------------------------------------------------------
# PLOTS
# ---------------------------------------------------------------------
def plot_results(df):

    # --------------------------------------------------
    # 1. Volatility → Rebalancing Frequency
    # --------------------------------------------------
    plt.figure()
    plt.plot(df["sigma"], df["mean_n_rebalances"], marker="o")
    plt.title("Rebalancing Frequency vs Volatility")
    plt.xlabel("Volatility (σ)")
    plt.ylabel("Mean Number of Rebalances")
    plt.grid(True)
    plt.savefig(OUTPUT_DIR / "sigma_vs_rebalances.png")
    plt.close()

    # --------------------------------------------------
    # 2. Volatility → Performance
    # --------------------------------------------------
    plt.figure()
    plt.plot(df["sigma"], df["mean_lp_minus_hodl"], marker="o")
    plt.title("LP vs HODL vs Volatility")
    plt.xlabel("Volatility (σ)")
    plt.ylabel("Mean LP − HODL")
    plt.grid(True)
    plt.savefig(OUTPUT_DIR / "sigma_vs_pnl.png")
    plt.close()

    # --------------------------------------------------
    # 3. Volatility → Convexity Drag
    # --------------------------------------------------
    plt.figure()
    plt.plot(df["sigma"], df["jensen_proxy"], marker="o")
    plt.title("Convexity Drag (Jensen Proxy) vs Volatility")
    plt.xlabel("Volatility (σ)")
    plt.ylabel("Jensen Proxy")
    plt.grid(True)
    plt.savefig(OUTPUT_DIR / "sigma_vs_jensen.png")
    plt.close()

    # --------------------------------------------------
    # 4. 🔥 KEY: Rebalancing → Convexity Drag
    # --------------------------------------------------
    plt.figure()
    plt.scatter(df["mean_n_rebalances"], df["jensen_proxy"])

    for i in range(len(df)):
        plt.text(
            df["mean_n_rebalances"][i],
            df["jensen_proxy"][i],
            f"σ={df['sigma'][i]}"
        )

    plt.xlabel("Mean Number of Rebalances")
    plt.ylabel("Convexity Drag (Jensen Proxy)")
    plt.title("Convexity Drag vs Rebalancing Intensity")
    plt.grid(True)
    plt.savefig(OUTPUT_DIR / "rebalances_vs_jensen.png")
    plt.close()


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------
if __name__ == "__main__":

    df = run_volatility_analysis()
    plot_results(df)

    print("\nAll volatility-driven plots generated.")