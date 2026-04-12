import numpy as np
import matplotlib.pyplot as plt
import os
from src.lp_model import value_lp


def simulate_price_paths(S0, mu, sigma, T, steps, n_paths):
    dt = T / steps
    paths = np.zeros((n_paths, steps))

    for i in range(n_paths):
        prices = [S0]
        for _ in range(steps - 1):
            dW = np.random.normal(0, np.sqrt(dt))
            dS = prices[-1] * (mu * dt + sigma * dW)
            prices.append(prices[-1] + dS)
        paths[i] = prices

    return paths


def simulate_lp_vs_hodl(
    P_a,
    P_b,
    L,
    S0,
    mu=0.0,
    sigma=0.4,
    T=1.0,
    steps=100,
    n_paths=200,
    output_dir="outputs"
):
    paths = simulate_price_paths(S0, mu, sigma, T, steps, n_paths)

    final_lp = []
    final_hodl = []

    V0 = value_lp(S0, P_a, P_b, L)

    # Realistic fee assumption:
    # ~40% APR on a ~$4,400 LP position ≈ $4.80/day
    base_daily_fee = 4.80
    days_per_step = (T * 365) / steps
    fee_per_step = base_daily_fee * days_per_step

    for path in paths:
        fee_accumulator = 0.0

        # accumulate fees while in range (simplified assumption)
        for _ in range(len(path)):
            fee_accumulator += fee_per_step

        final_price = path[-1]

        # LP payoff
        lp_val = value_lp(final_price, P_a, P_b, L)
        lp_val += fee_accumulator

        # HODL payoff (same initial capital)
        hodl_val = (final_price / S0) * V0

        final_lp.append(lp_val)
        final_hodl.append(hodl_val)

    # --- Plot distribution ---
    plt.figure(figsize=(10, 6))

    plt.hist(final_lp, bins=30, alpha=0.6, density=True, label="LP Outcomes")
    plt.hist(final_hodl, bins=30, alpha=0.6, density=True, label="HODL Outcomes")

    plt.xlabel("Final Portfolio Value")
    plt.ylabel("Density")
    plt.title("LP vs HODL: Distribution of Outcomes")
    plt.legend()
    plt.grid(True)

    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "simulation_distribution.png")
    plt.savefig(file_path)
    plt.close()

    print(f"Simulation saved to {file_path}")
    print("Average LP:", np.mean(final_lp))
    print("Average HODL:", np.mean(final_hodl))

    return np.array(final_lp), np.array(final_hodl)