import numpy as np


def accumulate_fees(S0, volume_per_day, fee_rate, liquidity_share, days):
    """
    Simple fee accumulation model
    """
    daily_fees = volume_per_day * fee_rate * liquidity_share
    total_fees = daily_fees * days
    return total_fees