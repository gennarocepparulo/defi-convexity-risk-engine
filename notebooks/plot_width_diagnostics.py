# ---------------------------------------------------------------------
# Plot Diagnostics: Width, Fees, Jensen (Gamma Drag), Volatility Effects
# ---------------------------------------------------------------------

import os
import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------
# Plot 1 — Objective vs Width
# ---------------------------------------------------------------------
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


# ---------------------------------------------------------------------
# Plot 2 — Rebalancing Frequency vs Width
# ---------------------------------------------------------------------
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


# ---------------------------------------------------------------------
# Plot 3 — PnL Decomposition (Fees vs Jensen vs Net)
# ---------------------------------------------------------------------
def plot_width_fee_decomposition(results_df, sigma):
    df = results_df.sort_values("width_pct")

    plt.figure()

    # Fees (positive)
    plt.plot(
        df["width_pct"],
        df["mean_cum_fees"],
        label="Fees",
        marker="o"
    )

    # Net performance
    plt.plot(
        df["width_pct"],
        df["mean_lp_minus_hodl"],
        label="LP vs HODL",
        marker="o"
    )

    # Jensen proxy (gamma drag)
    plt.plot(
        df["width_pct"],
        df["jensen_proxy"],
        label="Gamma Drag (Jensen)",
        linestyle="--"
    )

    plt.title(f"PnL Decomposition vs Width (σ={sigma})")
    plt.xlabel("Width")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)

    plt.savefig(f"outputs/fees_pnl_jensen_sigma_{sigma}.png")
    plt.close()


# ---------------------------------------------------------------------
# Plot 4 — Volatility Harvesting vs Gamma Drag (Cross-sigma)
# ---------------------------------------------------------------------
def plot_volatility_harvesting(summary_df):
    plt.figure()

    plt.plot(
        summary_df["sigma"],
        summary_df["mean_fees"],
        marker="o",
        label="Fees"
    )

    plt.plot(
        summary_df["sigma"],
        -summary_df["mean_jensen"],
        marker="o",
        label="Gamma Drag (|Jensen|)"
    )

    plt.xlabel("Volatility (σ)")
    plt.ylabel("Magnitude")
    plt.title("Volatility Harvesting vs Gamma Drag")
    plt.legend()
    plt.grid(True)

    plt.savefig("outputs/vol_harvest_vs_gamma.png")
    plt.close()


# ---------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------
if __name__ == "__main__":

    # Ensure output directory exists
    os.makedirs("outputs", exist_ok=True)

    # Volatility levels
    sigmas = [0.2, 0.4, 0.6, 0.8]

    summary_rows = []

    for sigma in sigmas:
        path = f"outputs/results_sigma_{sigma}.csv"

        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing results file: {path}")

        df = pd.read_csv(path)

        # -------------------------------------------------------------
        # Jensen proxy (Gamma Drag)
        # -------------------------------------------------------------
        df["jensen_proxy"] = (
            df["mean_lp_minus_hodl"] - df["mean_cum_fees"]
        )

        # -------------------------------------------------------------
        # Aggregate for volatility-level analysis
        # -------------------------------------------------------------
        summary_rows.append({
            "sigma": sigma,
            "mean_fees": df["mean_cum_fees"].mean(),
            "mean_jensen": df["jensen_proxy"].mean(),
        })

        # -------------------------------------------------------------
        # Generate plots per sigma
        # -------------------------------------------------------------
        plot_width_vs_objective(df, sigma)
        plot_width_vs_rebalances(df, sigma)
        plot_width_fee_decomposition(df, sigma)

        print(f"Generated diagnostics for sigma = {sigma}")

    # -----------------------------------------------------------------
    # Cross-volatility analysis (Wednesday deliverable)
    # -----------------------------------------------------------------
    summary_df = pd.DataFrame(summary_rows)

    # Optional: profitability ratio
    summary_df["fee_to_jensen_ratio"] = (
        summary_df["mean_fees"] / summary_df["mean_jensen"].abs()
    )

    plot_volatility_harvesting(summary_df)

    print("\n=== Volatility Summary ===")
    print(summary_df)

    print("\nAll diagnostic plots generated successfully.")