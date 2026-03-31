import matplotlib.pyplot as plt
import numpy as np
import os
from src.lp_model import delta_gamma_lp


def generate_risk_curves(P_a, P_b, L, current_price, output_dir="outputs"):
    # Price range (wide enough to show full behavior)
    prices = np.linspace(P_a * 0.8, P_b * 1.2, 100)

    deltas = []
    gammas = []

    for p in prices:
        d, g = delta_gamma_lp(p, P_a, P_b, L)
        deltas.append(d)
        gammas.append(g)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # --- Delta Plot ---
    ax1.plot(prices, deltas, label="Delta")
    ax1.axvline(P_a, linestyle="--", alpha=0.6, label="Lower Bound (P_a)")
    ax1.axvline(P_b, linestyle="--", alpha=0.6, label="Upper Bound (P_b)")
    ax1.axvline(current_price, linestyle=":", label="Current Price")
    ax1.set_ylabel("Delta")
    ax1.set_title("Uniswap v3 LP Delta Profile")
    ax1.legend()
    ax1.grid(True)

    # --- Gamma Plot ---
    ax2.plot(prices, gammas, label="Gamma")
    ax2.axvline(P_a, linestyle="--", alpha=0.6)
    ax2.axvline(P_b, linestyle="--", alpha=0.6)
    ax2.axvline(current_price, linestyle=":")
    ax2.set_xlabel("Price")
    ax2.set_ylabel("Gamma")
    ax2.set_title("Uniswap v3 LP Gamma (Convexity)")
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()

    # Save output
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "risk_curves.png")
    plt.savefig(file_path)
    plt.close()

    print(f"📈 Risk curves saved to {file_path}")
