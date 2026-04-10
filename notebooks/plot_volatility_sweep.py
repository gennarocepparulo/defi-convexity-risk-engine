from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
output_dir = PROJECT_ROOT / "outputs"

summary_path = output_dir / "volatility_sweep_summary.csv"
full_path = output_dir / "volatility_sweep_full_results.csv"

summary_df = pd.read_csv(summary_path)
full_df = pd.read_csv(full_path)

# -----------------------------
# Plot 1: Optimal width vs sigma
# -----------------------------
plt.figure(figsize=(7, 4))
plt.plot(summary_df["sigma"], summary_df["optimal_width"], marker="o")
plt.xlabel("Volatility (σ)")
plt.ylabel("Optimal Width")
plt.title("Optimal LP Width vs Volatility")
plt.grid(True)
plt.tight_layout()
plt.savefig(output_dir / "optimal_width_vs_volatility.png", dpi=150)
plt.show()

# ------------------------------------
# Plot 2: LP outperformance vs sigma
# ------------------------------------
plt.figure(figsize=(7, 4))
plt.plot(summary_df["sigma"], summary_df["mean_lp_minus_hodl"], marker="o")
plt.xlabel("Volatility (σ)")
plt.ylabel("Mean LP Outperformance vs HODL")
plt.title("LP Performance vs Volatility")
plt.grid(True)
plt.tight_layout()
plt.savefig(output_dir / "performance_vs_volatility.png", dpi=150)
plt.show()

# ------------------------------------
# Plot 3: Downside risk vs sigma
# ------------------------------------
plt.figure(figsize=(7, 4))
plt.plot(summary_df["sigma"], summary_df["prob_underperform_hodl"], marker="o")
plt.xlabel("Volatility (σ)")
plt.ylabel("Probability(LP < HODL)")
plt.title("Downside Risk vs Volatility")
plt.grid(True)
plt.tight_layout()
plt.savefig(output_dir / "risk_vs_volatility.png", dpi=150)
plt.show()

# ------------------------------------
# Plot 4: Risk-adjusted score vs width
# ------------------------------------
plt.figure(figsize=(8, 5))
for sigma in sorted(full_df["sigma"].unique()):
    df_sigma = full_df[full_df["sigma"] == sigma].sort_values("width_pct")
    plt.plot(
        df_sigma["width_pct"],
        df_sigma["objective"],
        marker="o",
        label=f"σ={sigma:.1f}"
    )

plt.xlabel("Width")
plt.ylabel("Risk-adjusted Score (mean / std)")
plt.title("Risk-adjusted Score vs Width")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(output_dir / "score_vs_width_by_sigma.png", dpi=150)
plt.show()

# ------------------------------------
# Plot 5: Fees vs width by sigma
# ------------------------------------
plt.figure(figsize=(8, 5))
for sigma in sorted(full_df["sigma"].unique()):
    df_sigma = full_df[full_df["sigma"] == sigma].sort_values("width_pct")
    plt.plot(
        df_sigma["width_pct"],
        df_sigma["mean_cum_fees"],
        marker="o",
        label=f"σ={sigma:.1f}"
    )

plt.xlabel("Width")
plt.ylabel("Mean Cumulative Fees")
plt.title("Fee Income vs Width")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(output_dir / "fees_vs_width_by_sigma.png", dpi=150)
plt.show()
