from pathlib import Path
import sys

# --------------------------------------------------
# Ensure project root in path
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.stochastic.lp_path_simulator import simulate_lp_strategy


# --------------------------------------------------
# Wrapper: LP minus HODL
# --------------------------------------------------
def simulate_lp_minus_hodl(
    prices,
    strategy,
    fee_config,
    sim_config,
):
    """
    Core research variable:

        X_t = LP_value - HODL_value

    This is the key object for:
    - martingale tests
    - convexity analysis
    - strategy optimization
    """

    sim_df = simulate_lp_strategy(
        prices=prices,
        strategy=strategy,
        fee_config=fee_config,
        sim_config=sim_config,
    ).copy()

    # --------------------------------------------------
    # Sanity check (robust to simulator changes)
    # --------------------------------------------------
    required_cols = [
        "step",
        "price",
        "lp_value",
        "hodl_value",
        "cum_fees",
        "in_range",
        "rebalanced",
    ]

    missing = [col for col in required_cols if col not in sim_df.columns]
    if missing:
        raise ValueError(
            f"simulate_lp_strategy is missing columns: {missing}"
        )

    # --------------------------------------------------
    # Core variable
    # --------------------------------------------------
    sim_df["lp_minus_hodl"] = (
        sim_df["lp_value"] - sim_df["hodl_value"]
    )

    # --------------------------------------------------
    # Optional: convexity proxy (cleaner than IL)
    # --------------------------------------------------
    sim_df["convexity_proxy"] = (
        sim_df["lp_minus_hodl"] - sim_df["cum_fees"]
    )

    return sim_df[
        [
            "step",
            "price",
            "lp_value",
            "hodl_value",
            "lp_minus_hodl",
            "cum_fees",
            "convexity_proxy",
            "in_range",
            "rebalanced",
        ]
    ]