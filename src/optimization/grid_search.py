from typing import Callable, Iterable, Dict, Any, List
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
    Baseline grid search over LP range widths.
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
        })

    return pd.DataFrame(results).sort_values("objective", ascending=False).reset_index(drop=True)
