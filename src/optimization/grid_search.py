from typing import Callable, Iterable, Dict, Any, List
import numpy as np
import pandas as pd

from src.strategy.uniswap_v3 import LPStrategyConfig, UniswapV3Strategy
from src.stochastic.fee_model import FeeModelConfig
from src.stochastic.lp_path_simulator import LPSimulationConfig, simulate_lp_strategy


def optimize_width_grid(
    prices,
    center_price: float,
    width_grid: Iterable[float],
    objective_fn: Callable[[pd.DataFrame], float],
    fee_config: FeeModelConfig,
    sim_config: LPSimulationConfig,
    base_strategy_kwargs: Dict[str, Any] = None,
) -> pd.DataFrame:
    """
    Single-path baseline grid search.
    Kept for debugging and scenario analysis.
    """
    results: List[Dict[str, Any]] = []
    base_strategy_kwargs = base_strategy_kwargs or {}

    for width_pct in width_grid:
        config = LPStrategyConfig(
            center_price=center_price,
            width_pct=width_pct,
            fee_tier=fee_config.fee_tier,
            capital=sim_config.initial_capital,
            **base_strategy_kwargs
        )
        strategy = UniswapV3Strategy(config)

        sim_df = simulate_lp_strategy(
            prices=prices,
            strategy=strategy,
            fee_config=fee_config,
            sim_config=sim_config
        )

        score = objective_fn(sim_df)

        results.append({
            "width_pct": width_pct,
            "objective": score,
            "final_lp_value": sim_df["lp_value"].iloc[-1],
            "final_hodl_value": sim_df["hodl_value"].iloc[-1],
            "lp_minus_hodl": sim_df["lp_minus_hodl"].iloc[-1],
            "cum_fees": sim_df["cum_fees"].iloc[-1],
            "final_il_value": sim_df["il_value"].iloc[-1],
            "time_in_range": sim_df["in_range"].mean(),
            "n_rebalances": sim_df["rebalanced"].sum(),
        })

    return pd.DataFrame(results).sort_values("objective", ascending=False).reset_index(drop=True)


def optimize_width_grid_mc(
    paths: np.ndarray,
    center_price: float,
    width_grid: Iterable[float],
    objective_fn: Callable[[pd.DataFrame], float],
    fee_config: FeeModelConfig,
    sim_config: LPSimulationConfig,
    base_strategy_kwargs: Dict[str, Any] = None,
    score_mode: str = "mean",
    risk_aversion: float = 0.0,
) -> pd.DataFrame:
    """
    Monte Carlo grid search over LP width.

    Parameters
    ----------
    paths : np.ndarray
        Shape (n_steps + 1, n_paths)
    center_price : float
        Initial center price used to initialize each strategy
    width_grid : iterable
        Candidate width_pct values
    objective_fn : callable
        Function mapping sim_df -> scalar objective (e.g. expected_net_return)
    fee_config : FeeModelConfig
    sim_config : LPSimulationConfig
    base_strategy_kwargs : dict
        Extra arguments passed into LPStrategyConfig
    score_mode : str
        "mean"              -> score = mean(objective)
        "mean_minus_lambda_std" -> score = mean(objective) - lambda * std(objective)
        "sharpe_like"       -> score = mean(objective) / std(objective)
    risk_aversion : float
        Lambda used only if score_mode = "mean_minus_lambda_std"
    """
    results: List[Dict[str, Any]] = []
    base_strategy_kwargs = base_strategy_kwargs or {}

    n_paths = paths.shape[1]

    for width_pct in width_grid:
        path_scores = []
        final_lp_values = []
        final_hodl_values = []
        lp_minus_hodl_values = []
        cum_fees_values = []
        final_il_values = []
        time_in_range_values = []
        n_rebalances_values = []

        for i in range(n_paths):
            prices = paths[:, i]

            # IMPORTANT: reset strategy for each path
            config = LPStrategyConfig(
                center_price=center_price,
                width_pct=width_pct,
                fee_tier=fee_config.fee_tier,
                capital=sim_config.initial_capital,
                **base_strategy_kwargs
            )
            strategy = UniswapV3Strategy(config)

            sim_df = simulate_lp_strategy(
                prices=prices,
                strategy=strategy,
                fee_config=fee_config,
                sim_config=sim_config
            )

            path_scores.append(objective_fn(sim_df))
            final_lp_values.append(sim_df["lp_value"].iloc[-1])
            final_hodl_values.append(sim_df["hodl_value"].iloc[-1])
            lp_minus_hodl_values.append(sim_df["lp_minus_hodl"].iloc[-1])
            cum_fees_values.append(sim_df["cum_fees"].iloc[-1])
            final_il_values.append(sim_df["il_value"].iloc[-1])
            time_in_range_values.append(sim_df["in_range"].mean())
            n_rebalances_values.append(sim_df["rebalanced"].sum())

        path_scores = np.array(path_scores, dtype=float)
        mean_score = float(np.mean(path_scores))
        std_score = float(np.std(path_scores))

        if score_mode == "mean":
            aggregate_score = mean_score
        elif score_mode == "mean_minus_lambda_std":
            aggregate_score = mean_score - risk_aversion * std_score
        elif score_mode == "sharpe_like":
            aggregate_score = mean_score / std_score if std_score > 1e-12 else 0.0
        else:
            raise ValueError(f"Unknown score_mode: {score_mode}")

        lp_minus_hodl_values = np.array(lp_minus_hodl_values, dtype=float)

        results.append({
            "width_pct": width_pct,
            "objective": aggregate_score,
            "mean_objective": mean_score,
            "std_objective": std_score,
            "mean_final_lp_value": float(np.mean(final_lp_values)),
            "mean_final_hodl_value": float(np.mean(final_hodl_values)),
            "mean_lp_minus_hodl": float(np.mean(lp_minus_hodl_values)),
            "prob_underperform_hodl": float(np.mean(lp_minus_hodl_values < 0.0)),
            "mean_cum_fees": float(np.mean(cum_fees_values)),
            "mean_final_il_value": float(np.mean(final_il_values)),
            "mean_time_in_range": float(np.mean(time_in_range_values)),
            "mean_n_rebalances": float(np.mean(n_rebalances_values)),
        })

    return (
        pd.DataFrame(results)
        .sort_values("objective", ascending=False)
        .reset_index(drop=True)
    )
