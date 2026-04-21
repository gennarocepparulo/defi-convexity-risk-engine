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

from src.stochastic.price_process import GBMConfig, simulate_gbm_paths

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
SIGMA = 0.4
N_PATHS = 5000
T = 1.0

OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------
# IL FUNCTION
# ---------------------------------------------------------------------
def V_lp(r):
    return 2 * np.sqrt(r) / (1 + r)


def impermanent_loss(r):
    return V_lp(r) - 1.0


# ---------------------------------------------------------------------
# 1. IL CURVE
# ---------------------------------------------------------------------
def plot_il_curve():
    r = np.linspace(0.2, 5.0, 500)
    il = impermanent_loss(r)

    plt.figure(figsize=(7, 4))
    plt.plot(r, il)
    plt.axhline(0, linestyle="--")
    plt.title("Impermanent Loss vs Price Ratio")
    plt.xlabel("Price Ratio (S / S0)")
    plt.ylabel("IL")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / "il_curve.png", dpi=150)
    plt.close()


# ---------------------------------------------------------------------
# 2. JENSEN GAP TEST
# ---------------------------------------------------------------------
def compute_jensen_gap():

    gbm_cfg = GBMConfig(
        s0=1.0,
        mu=0.0,
        sigma=SIGMA,
        t_horizon=T,
        n_steps=252,
        n_paths=N_PATHS,
        seed=42,
    )

    paths = simulate_gbm_paths(gbm_cfg)

    # final price ratio
    r_T = paths[-1, :] / paths[0, :]

    lhs = np.mean(V_lp(r_T))       # E[V(R)]
    rhs = V_lp(np.mean(r_T))       # V(E[R])

    gap = lhs - rhs

    print("\n=== Jensen Gap Test ===")
    print(f"E[V(R)]       : {lhs:.6f}")
    print(f"V(E[R])       : {rhs:.6f}")
    print(f"Gap (LHS-RHS) : {gap:.6f}")

    return r_T


# ---------------------------------------------------------------------
# 3. HISTOGRAM
# ---------------------------------------------------------------------
def plot_il_distribution(r_T):

    il = impermanent_loss(r_T)

    plt.figure(figsize=(7, 4))
    plt.hist(il, bins=60, density=True, alpha=0.7)

    plt.axvline(np.mean(il), linestyle="--", label="Mean IL")
    plt.title("Distribution of Impermanent Loss (GBM)")
    plt.xlabel("IL")
    plt.ylabel("Density")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / "il_distribution.png", dpi=150)
    plt.close()


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------
if __name__ == "__main__":
    plot_il_curve()
    r_T = compute_jensen_gap()
    plot_il_distribution(r_T)

    print("\nSaved outputs:")
    print("- il_curve.png")
    print("- il_distribution.png")