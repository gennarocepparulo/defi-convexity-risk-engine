import numpy as np
import matplotlib.pyplot as plt
import os
from src.lp_model import value_lp


def generate_pnl_comparison(P_a, P_b, L, S0, output_dir="outputs"):
    """
    Compare LP vs HODL PnL across price range
    """

    prices = np.linspace(P_a * 0.8, P_b * 1.2, 200)

    # --- LP values ---
    lp_values = [value_lp(p, P_a, P_b, L) for p in prices]

    # --- HODL baseline ---
    # replicate initial LP portfolio at S0
    V0 = value_lp(S0, P_a, P_b, L)

    # approximate HODL as linear exposure
    hodl_values = [(p / S0) * V0 for p in prices]

    # --- Plot ---
    plt.figure(figsize=(10, 6))

    plt.plot(prices, lp_values, label="LP Value")
    plt.plot(prices, hodl_values, linestyle="--", label="HODL Value")

    # Mark key levels
    plt.axvline(P_a, linestyle="--", alpha=0.5)
    plt.axvline(P_b, linestyle="--", alpha=0.5)
    plt.axvline(S0, linestyle=":", label="Current Price")

    plt.title("LP vs HODL PnL Profile")
    plt.xlabel("Price")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid(True)

    # Save
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "pnl_comparison.png")
    plt.savefig(file_path)
    plt.close()

    print(f"📊 PnL comparison saved to {file_path}")