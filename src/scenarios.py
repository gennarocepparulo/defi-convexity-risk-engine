import numpy as np
import pandas as pd
from src.lp_model import value_lp, delta_gamma_lp
from src.risk_metrics import (
    p_at_least_one_jump,
    gamma_exposure,
    expected_jump_loss,
    estimate_fee_income
)
from src.price_fetcher import get_token_market_data, get_coingecko_price

# Parameters
P_a, P_b = 1800.0, 2200.0
L = 1000.0
lambda_per_blk = 0.001
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

    # --- Risk calculations ---
    expected_loss = expected_jump_loss(shortfall, p_jump)

    risk_reward = abs(expected_loss) / fees if fees != 0 else None

return {
        "Scenario": label,
        "Price": round(S, 2),
        "Value": round(V, 2),
        "Delta": round(dlt, 6),
        "Gamma": round(gmm, 8),
        "Gamma Exposure": round(gamma_exposure(gmm, S), 2),
        "Shock Loss (-10%)": round(shortfall, 2),
        "Jump Prob": round(p_jump, 4),
        "Expected Jump Loss": round(expected_loss, 2),
        "Est Daily Fees": round(fees, 2),
        "Risk/Reward": round(risk_reward, 2) if risk_reward is not None else None,
    }

return {
    "Scenario": label,
    "Price": round(S, 2),
    "Value": round(V, 2),
    "Delta": round(dlt, 6),
    "Gamma": round(gmm, 8),
    "Gamma Exposure": round(gamma_exposure(gmm, S), 2),
    "Shock Loss (-10%)": round(shortfall, 2),
    "Jump Prob": round(p_jump, 4),
    "Expected Jump Loss": round(expected_loss, 2),
    "Est Daily Fees": round(fees, 2),
    "Risk/Reward": round(risk_reward, 2) if risk_reward is not None else None,
}

def build_dashboard(use_real_price=True, token_id="ethereum"):
    """
    Build dashboard with real-time or static prices
    token_id: 'ethereum', 'uniswap', 'aave', etc.
    """
    if use_real_price:
        S0 = get_coingecko_price(token_id=token_id)
        if S0 is None:
            print(f"⚠️  Could not fetch {token_id} price, using default S0=2000")
            S0 = 2000.0
        else:
            print(f"✅ Real-time {token_id.upper()} price: ${S0}")
    else:
        S0 = 2000.0
    
    scenarios = [
        (0.9 * S0, "Bear (-10%)"),
        (S0, "Base (Current)"),
        (1.1 * S0, "Bull (+10%)")
    ]

    rows = [row_for_price(S, label) for S, label in scenarios]
    return pd.DataFrame(rows).set_index("Scenario")
    
for idx, row in df.iterrows():
    if row["Risk/Reward"] is not None:
        if row["Risk/Reward"] > 3:
            print(f"⚠️ {idx}: Risk too high vs fees")
        else:
            print(f"✅ {idx}: Acceptable risk level")
