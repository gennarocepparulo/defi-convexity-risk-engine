from src.stochastic.lp_path_simulator import simulate_lp_strategy
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def simulate_lp_minus_hodl(
    prices,
    strategy,
    fee_config,
    sim_config,
):
    """
    Run LP strategy simulation and isolate the research variable:

        X_t = V_t^{LP} - V_t^{HODL}

    Returns
    -------
    DataFrame
        Contains:
        - step
        - price
        - lp_value
        - hodl_value
        - lp_minus_hodl
        - cum_fees
        - il_value
        - in_range
        - rebalanced
    """
    sim_df = simulate_lp_strategy(
        prices=prices,
        strategy=strategy,
        fee_config=fee_config,
        sim_config=sim_config,
    ).copy()

    required_cols = [
        "step",
        "price",
        "lp_value",
        "hodl_value",
        "cum_fees",
        "il_value",
        "in_range",
        "rebalanced",
    ]

    missing = [col for col in required_cols if col not in sim_df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns from simulate_lp_strategy: {missing}"
        )

    sim_df["lp_minus_hodl"] = sim_df["lp_value"] - sim_df["hodl_value"]

    return sim_df[
        [
            "step",
            "price",
            "lp_value",
            "hodl_value",
            "lp_minus_hodl",
            "cum_fees",
            "il_value",
            "in_range",
            "rebalanced",
        ]
    ]
