import numpy as np
import pandas as pd


def expected_net_return(sim_df: pd.DataFrame) -> float:
    """
    Final LP return relative to initial capital.
    """
    initial_value = sim_df["lp_value"].iloc[0]
    final_value = sim_df["lp_value"].iloc[-1]
    return (final_value / initial_value) - 1.0


def annualized_sharpe_ratio(sim_df: pd.DataFrame, periods_per_year: int = 252) -> float:
    """
    Compute a simple annualized Sharpe ratio from LP value returns.
    """
    values = sim_df["lp_value"].values
    rets = np.diff(values) / np.maximum(values[:-1], 1e-12)

    if len(rets) == 0:
        return 0.0

    vol = np.std(rets)
    if vol < 1e-12:
        return 0.0

    mean_ret = np.mean(rets)
    return np.sqrt(periods_per_year) * mean_ret / vol


def fee_il_tradeoff_score(sim_df: pd.DataFrame) -> float:
    """
    Simple score:
        cumulative fees - absolute final IL
    """
    total_fees = sim_df["cum_fees"].iloc[-1]
    final_il = abs(sim_df["il_value"].iloc[-1])
    return total_fees - final_il
