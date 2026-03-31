import numpy as np

def amounts_single_range(P, P_a, P_b, L):
    sqrtP, sqrtPa, sqrtPb = np.sqrt(P), np.sqrt(P_a), np.sqrt(P_b)

    if P <= P_a:
        amt0 = L * (sqrtPb - sqrtPa) / (sqrtPa * sqrtPb)
        amt1 = 0.0
    elif P >= P_b:
        amt0 = 0.0
        amt1 = L * (sqrtPb - sqrtPa)
    else:
        amt0 = L * (sqrtPb - sqrtP) / (sqrtP * sqrtPb)
        amt1 = L * (sqrtP - sqrtPa)

    return amt0, amt1

def value_lp(P, P_a, P_b, L):
    amt0, amt1 = amounts_single_range(P, P_a, P_b, L)
    return amt0 * P + amt1

def delta_gamma_lp(P, P_a, P_b, L):
    if P <= P_a:
        amt0, _ = amounts_single_range(P, P_a, P_b, L)
        return amt0, 0.0
    elif P >= P_b:
        return 0.0, 0.0
    else:
        delta = L * (1 / np.sqrt(P) - 1 / np.sqrt(P_b))
        gamma = -0.5 * L * (P ** -1.5)
        return delta, gamma

def p_at_least_one_jump(lambda_per_blk, H_blocks):
    return 1 - np.exp(-lambda_per_blk * H_blocks)

def gamma_exposure(gamma, price):
    return abs(gamma) * (price ** 2)

def expected_jump_loss(loss, prob):
    return loss * prob

def estimate_fee_income(L, total_liquidity, daily_volume, fee_tier=0.003):
    share = L / total_liquidity
    return daily_volume * fee_tier * share