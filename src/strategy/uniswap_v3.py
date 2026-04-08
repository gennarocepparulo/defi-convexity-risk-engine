"""
Uniswap v3 LP strategy module.

This file defines strategy-level abstractions for:
- liquidity range selection
- rebalancing rules
- transaction cost handling
"""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class StrategyConfig:
    lower_bound: float
    upper_bound: float
    rebalance_policy: str = "none"   # e.g. "none", "threshold", "time"
    rebalance_threshold: Optional[float] = None
    gas_cost: float = 0.0
    slippage_cost: float = 0.0


class UniswapV3Strategy:
    def __init__(self, config: StrategyConfig):
        self.config = config

    def range_width(self) -> float:
        return self.config.upper_bound - self.config.lower_bound

    def should_rebalance(self, current_price: float) -> bool:
        if self.config.rebalance_policy == "none":
            return False

        if self.config.rebalance_policy == "threshold":
            if self.config.rebalance_threshold is None:
                return False
            mid = 0.5 * (self.config.lower_bound + self.config.upper_bound)
            deviation = abs(current_price - mid) / mid
            return deviation >= self.config.rebalance_threshold

        return False

    def transaction_cost(self) -> float:
        return self.config.gas_cost + self.config.slippage_cost

    def active_range(self) -> Tuple[float, float]:
        return self.config.lower_bound, self.config.upper_bound
