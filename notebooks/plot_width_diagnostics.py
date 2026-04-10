import matplotlib.pyplot as plt

def plot_width_vs_objective(results_df, sigma):
    plt.figure()
    plt.plot(results_df["width_pct"], results_df["mean_objective"], marker="o")
    plt.title(f"Objective vs Width (σ={sigma})")
    plt.xlabel("Width")
    plt.ylabel("Expected Return")
    plt.grid(True)
    plt.savefig(f"outputs/width_vs_objective_sigma_{sigma}.png")
    plt.close()

def plot_width_vs_rebalances(results_df, sigma):
    plt.figure()
    plt.plot(results_df["width_pct"], results_df["mean_n_rebalances"], marker="o")
    plt.title(f"Rebalancing Frequency vs Width (σ={sigma})")
    plt.xlabel("Width")
    plt.ylabel("Mean Number of Rebalances")
    plt.grid(True)
    plt.savefig(f"outputs/rebalances_vs_width_sigma_{sigma}.png")
    plt.close()

def plot_width_fee_decomposition(results_df, sigma):
    plt.figure()
    plt.plot(results_df["width_pct"], results_df["mean_cum_fees"], label="Fees", marker="o")
    plt.plot(results_df["width_pct"], results_df["mean_lp_minus_hodl"], label="LP vs HODL", marker="o")
    
    plt.title(f"Fees & PnL vs Width (σ={sigma})")
    plt.xlabel("Width")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)
    
    plt.savefig(f"outputs/fees_pnl_vs_width_sigma_{sigma}.png")
    plt.close()        