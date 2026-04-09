from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np

from src.stochastic.price_process import GBMConfig, simulate_gbm_paths
from src.stochastic.fee_model import FeeModelConfig
from src.stochastic.lp_path_simulator import LPSimulationConfig
from src.optimization.grid_search import optimize_width_grid_mc
from src.optimization.objective import expected_net_return

# 1) Simulate MANY price paths
gbm_cfg = GBMConfig(
    s0=2000.0,
    mu=0.05,
    sigma=0.60,
    t_horizon=1.0,
    n_steps=252,
    n_paths=50,   # Monte Carlo
    seed=42,
)

paths = simulate_gbm_paths(gbm_cfg)

# 2) Configure fee/sim
fee_cfg = FeeModelConfig(
    fee_tier=0.003,
    volume_multiplier=8.0,
    liquidity_share=1.0,
)

sim_cfg = LPSimulationConfig(
    initial_capital=1000.0,
    il_sensitivity=1.0,
    include_rebalancing_costs=True,
)

# 3) Width grid
width_grid = np.linspace(0.05, 0.50, 10)

# 4) Monte Carlo optimization
results = optimize_width_grid_mc(
    paths=paths,
    center_price=gbm_cfg.s0,
    width_grid=width_grid,
    objective_fn=expected_net_return,
    fee_config=fee_cfg,
    sim_config=sim_cfg,
    base_strategy_kwargs={
        "rebalance_policy": "out_of_range",
        "gas_cost": 2.0,
        "slippage_cost": 1.0,
    },
    score_mode="mean",   # start simple
)

print("\nTop results:")
print(results.head())

print("\nDebug view:")
print(results[[
    "width_pct",
    "objective",
    "mean_objective",
    "std_objective",
    "mean_time_in_range",
    "mean_n_rebalances",
    "mean_cum_fees",
    "mean_lp_minus_hodl",
    "prob_underperform_hodl",
]])