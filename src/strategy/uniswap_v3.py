from dataclasses import dataclass


# --------------------------------------------------
# Configuration
# --------------------------------------------------
@dataclass
class LPStrategyConfig:
    center_price: float
    width_pct: float
    rebalance_policy: str = "none"       # "none" | "out_of_range" | "threshold"
    rebalance_threshold: float = 0.05    # used only for "threshold"
    gas_cost: float = 1.0
    slippage_coeff: float = 0.001
    capital: float = 1000.0


# --------------------------------------------------
# Strategy
# --------------------------------------------------
class UniswapV3Strategy:

    def __init__(self, config: LPStrategyConfig):
        self.config = config

    # --------------------------------------------------
    # Range
    # --------------------------------------------------
    @property
    def lower_bound(self) -> float:
        return float(self.config.center_price) * (1.0 - float(self.config.width_pct))

    @property
    def upper_bound(self) -> float:
        return float(self.config.center_price) * (1.0 + float(self.config.width_pct))

    def is_in_range(self, price: float) -> bool:
        return self.lower_bound <= price <= self.upper_bound

    # --------------------------------------------------
    # Rebalancing logic
    # --------------------------------------------------
    def should_rebalance(self, current_price: float, step: int) -> bool:
        """
        Decide whether to rebalance based on policy.

        Policies:
        - "none": never rebalance
        - "out_of_range": rebalance when price exits range
        - "threshold": rebalance when deviation from center exceeds threshold
        """

        policy = str(self.config.rebalance_policy).lower()

        # --- no rebalancing ---
        if policy == "none":
            return False

        # --- rebalance when out of range ---
        if policy == "out_of_range":
            return not self.is_in_range(current_price)

        # --- threshold-based rebalancing ---
        if policy == "threshold":
            center = float(self.config.center_price)
            if center <= 0:
                return False

            deviation = abs(current_price / center - 1.0)
            return deviation > float(self.config.rebalance_threshold)

        # --- unknown policy (fail safe) ---
        return False

    # --------------------------------------------------
    # Transaction cost model
    # --------------------------------------------------
    def transaction_cost(self, notional: float) -> float:
        """
        Cost = gas + slippage

        Slippage increases as width becomes narrower.
        """
        width = max(float(self.config.width_pct), 1e-6)

        gas = float(self.config.gas_cost)
        slippage = float(self.config.slippage_coeff) * float(notional) / width

        return gas + slippage