from pathlib import Path
import sys

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np

import src.stochastic.price_process
from src.stochastic.fee_model import FeeModelConfig
from src.stochastic.lp_path_simulator import LPSimulationConfig
from src.optimization.grid_search import optimize_width_grid
from src.optimization.objective import expected_net_return

# 1) Simulate price paths
gbm_cfg = src.stochastic.price_process.GBMConfig(
    s0=2000.0,
    mu=0.05,
    sigma=0.60,
    t_horizon=1.0,
    n_steps=252,
    n_paths=1,
    seed=42,
)

paths = src.stochastic.price_process.simulate_gbm_paths(gbm_cfg)
prices = paths[:, 0]

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

# 3) Optimize width over a grid
width_grid = np.linspace(0.05, 0.50, 10)

results = optimize_width_grid(
    prices=prices,
    center_price=prices[0],
    width_grid=width_grid,
    objective_fn=expected_net_return,
    fee_config=fee_cfg,
    sim_config=sim_cfg,
    base_strategy_kwargs={
        "rebalance_policy": "threshold",
        "rebalance_threshold": 0.10,
        "gas_cost": 2.0,
        "slippage_cost": 1.0,
    }
)

print(results.head())