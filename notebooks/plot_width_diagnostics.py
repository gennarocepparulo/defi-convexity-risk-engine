# 1. Imports
import os
import pandas as pd
import matplotlib.pyplot as plt

# 2. Plotting functions
def plot_width_vs_objective(results_df, sigma):
    df = results_df.sort_values("width_pct")

    plt.figure()
    plt.plot(df["width_pct"], df["mean_objective"], marker="o")
    plt.title(f"Objective vs Width (σ={sigma})")
    plt.xlabel("Width")
    plt.ylabel("Expected Net LP Return")
    plt.grid(True)
    plt.savefig(f"outputs/width_vs_objective_sigma_{sigma}.png")
    plt.close()


def plot_width_vs_rebalances(results_df, sigma):
    df = results_df.sort_values("width_pct")

    plt.figure()
    plt.plot(df["width_pct"], df["mean_n_rebalances"], marker="o")
    plt.title(f"Rebalancing Frequency vs Width (σ={sigma})")
    plt.xlabel("Width")
    plt.ylabel("Mean Number of Rebalances")
    plt.grid(True)
    plt.savefig(f"outputs/rebalances_vs_width_sigma_{sigma}.png")
    plt.close()


def plot_width_fee_decomposition(results_df, sigma):
    df = results_df.sort_values("width_pct")

    plt.figure()
    plt.plot(df["width_pct"], df["mean_cum_fees"], label="Fees", marker="o")
    plt.plot(df["width_pct"], df["mean_lp_minus_hodl"], label="LP vs HODL", marker="o")

    plt.title(f"Fees & Net PnL vs Width (σ={sigma})")
    plt.xlabel("Width")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)

    plt.savefig(f"outputs/fees_pnl_vs_width_sigma_{sigma}.png")
    plt.close()


# 3. Main execution block
if __name__ == "__main__":

    # Ensure output directory exists
    os.makedirs("outputs", exist_ok=True)

    # Volatility levels analyzed
    sigmas = [0.2, 0.4, 0.6, 0.8]

    for sigma in sigmas:
        path = f"outputs/results_sigma_{sigma}.csv"

        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing results file: {path}")

        df = pd.read_csv(path)

        plot_width_vs_objective(df, sigma)
        plot_width_vs_rebalances(df, sigma)
        plot_width_fee_decomposition(df, sigma)

        print(f"Generated width diagnostics for sigma = {sigma}")

    print("All width diagnostic plots generated successfully.")