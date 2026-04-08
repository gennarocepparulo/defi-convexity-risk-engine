import numpy as np
import matplotlib.pyplot as plt
import os

from src.lp_model import value_lp


def generate_pnl_comparison(P_a, P_b, L, S0, output_dir="outputs"):
    """
    Compare LP vs HODL portfolio value across price range.
    Visually illustrates impermanent loss / convexity cost.
    """

    prices = np.linspace(P_a * 0.8, P_b * 1.2, 200)

    # --- LP values (nonlinear payoff) ---
    lp_values = [value_lp(p, P_a, P_b, L) for p in prices]

    # --- HODL baseline (linear exposure) ---
    V0 = value_lp(S0, P_a, P_b, L)
    hodl_values = [(p / S0) * V0 for p in prices]

    # --- Convexity cost ---
    convexity_cost = [lp - h for lp, h in zip(lp_values, hodl_values)]

    # ============================
    # LP vs HODL plot
    # ============================
    plt.figure(figsize=(10, 6))

    plt.plot(prices, lp_values, label="LP Value (nonlinear)")
    plt.plot(prices, hodl_values, linestyle="--", label="HODL Value (linear)")

    plt.axvline(P_a, linestyle="--", alpha=0.4)
    plt.axvline(P_b, linestyle="--", alpha=0.4)
    plt.axvline(S0, linestyle=":", label="Current Price")

    plt.title("LP vs HODL PnL Profile")
    plt.xlabel("Price")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid(True)

    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "pnl_comparison.png")
    plt.savefig(file_path, dpi=150, bbox_inches="tight")
    plt.close()

    # ============================
    # Convexity cost plot
    # ============================
    plt.figure(figsize=(10, 5))

    plt.plot(prices, convexity_cost, color="red", label="LP − HODL")

    plt.axhline(0, linestyle="--", color="black", alpha=0.6)
    plt.axvline(S0, linestyle=":", label="Current Price", color="black")

    plt.title("Convexity Cost (Impermanent Loss)")
    plt.xlabel("Price")
    plt.ylabel("Value Difference")
    plt.legend()
    plt.grid(True)

    file_path_cc = os.path.join(output_dir, "convexity_cost.png")
    plt.savefig(file_path_cc, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"📊 PnL comparison saved to {file_path}")
    print(f"📉 Convexity cost saved to {file_path_cc}")
