from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class LPStrategyConfig:
    center_price: float
    width_pct: float
    rebalance_policy: str = "none"   # "none", "out_of_range", "threshold", "time"
    rebalance_threshold: Optional[float] = None
    rebalance_every_n_steps: Optional[int] = None

    gas_cost: float = 0.0
    slippage_coeff: float = 0.0              # k in k * capital / width
    min_width_for_costs: float = 0.03

    capital: float = 1_000.0
    fee_tier: float = 0.003


class UniswapV3Strategy:
    def __init__(self, config: LPStrategyConfig):
        self.config = config

    @property
    def lower_bound(self) -> float:
        return self.config.center_price * (1.0 - self.config.width_pct)

    @property
    def upper_bound(self) -> float:
        return self.config.center_price * (1.0 + self.config.width_pct)

    def active_range(self) -> Tuple[float, float]:
        return self.lower_bound, self.upper_bound

    def is_in_range(self, price: float) -> bool:
        return self.lower_bound <= price <= self.upper_bound

    def transaction_cost(self, capital_base: float) -> float:
        """
        Transaction cost = gas + slippage.
        Slippage scales inversely with width.
        """
        effective_width = max(self.config.width_pct, self.config.min_width_for_costs)
        slippage_cost = self.config.slippage_coeff * capital_base / effective_width
        return self.config.gas_cost + slippage_cost

    def should_rebalance(self, current_price: float, step: int) -> bool:
        if self.config.rebalance_policy == "none":
            return False

        if self.config.rebalance_policy == "out_of_range":
            return not self.is_in_range(current_price)

        if self.config.rebalance_policy == "threshold":
            if self.config.rebalance_threshold is None:
                return False
            deviation = abs(current_price - self.config.center_price) / self.config.center_price
            return deviation >= self.config.rebalance_threshold

        if self.config.rebalance_policy == "time":
            if self.config.rebalance_every_n_steps is None:
                return False
            return step > 0 and step % self.config.rebalance_every_n_steps == 0

        return False

    def rebalance(self, new_center_price: float) -> None:
        self.config.center_price = new_center_price