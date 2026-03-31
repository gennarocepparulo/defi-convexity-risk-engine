import numpy as np
import pandas as pd
from src.lp_model import value_lp, delta_gamma_lp
from src.risk_metrics import (
    p_at_least_one_jump,
    gamma_exposure,
    expected_jump_loss,
    estimate_fee_income
)

# Parameters
S0 = 2000.0
P_a, P_b = 1800.0, 2200.0
L = 1000.0
lambda_per_blk = 0.02
H_blocks = 100

def row_for_price(S, label):
    V = value_lp(S, P_a, P_b, L)
    dlt, gmm = delta_gamma_lp(S, P_a, P_b, L)

    S_shock = 0.9 * S
    V_shock = value_lp(S_shock, P_a, P_b, L)
    shortfall = V_shock - V

    p_jump = p_at_least_one_jump(lambda_per_blk, H_blocks)

    daily_volume = 50_000_000
    total_liquidity = 10_000_000
    fees = estimate_fee_income(L, total_liquidity, daily_volume)

    return {
        "Scenario": label,
        "Price": round(S, 2),
        "Value": round(V, 2),
        "Delta": round(dlt, 6),
        "Gamma": round(gmm, 8),
        "Gamma Exposure": round(gamma_exposure(gmm, S), 2),
        "Shock Loss (-10%)": round(shortfall, 2),
        "Jump Prob": round(p_jump, 4),
        "Expected Jump Loss": round(expected_jump_loss(shortfall, p_jump), 2),
        "Est Daily Fees": round(fees, 2),
    }

def build_dashboard():
    scenarios = [
        (0.9 * S0, "Bear"),
        (S0, "Base"),
        (1.1 * S0, "Bull")
    ]

    rows = [row_for_price(S, label) for S, label in scenarios]
    return pd.DataFrame(rows).set_index("Scenario")