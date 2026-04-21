import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from src.lp_model import value_lp


# -----------------------------
# 1. Fetch historical prices
# -----------------------------
def get_historical_prices(token_id="ethereum", days=365):
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart"
    
    params = {
        "vs_currency": "usd",
        "days": days
    }

    response = requests.get(url, params=params)
    data = response.json()

    prices = data["prices"]

    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
    
    return df[["date", "price"]]


# -----------------------------
# 2. Backtest engine
# -----------------------------
def run_backtest(P_a, P_b, L, token_id="ethereum", days=365, output_dir="outputs"):
    
    df = get_historical_prices(token_id, days)
    
    S0 = df["price"].iloc[0]
    V0 = value_lp(S0, P_a, P_b, L)

    lp_values = []
    hodl_values = []
    fee_accumulator = 0

    # Assumptions
    daily_volume = 50_000_000
    fee_rate = 0.003
    liquidity_share = 0.001

    for price in df["price"]:
        
        # LP value
        lp_val = value_lp(price, P_a, P_b, L)

        # Fees
        daily_fees = daily_volume * fee_rate * liquidity_share
        fee_accumulator += daily_fees

        lp_val += fee_accumulator

        # HODL value
        hodl_val = (price / S0) * V0

        lp_values.append(lp_val)
        hodl_values.append(hodl_val)

    df["LP"] = lp_values
    df["HODL"] = hodl_values

    # -----------------------------
    # Plot
    # -----------------------------
    plt.figure(figsize=(10, 6))

    plt.plot(df["date"], df["LP"], label="LP Strategy")
    plt.plot(df["date"], df["HODL"], linestyle="--", label="HODL")

    plt.title("Historical Backtest: LP vs HODL")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid(True)

    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "backtest.png")
    plt.savefig(file_path)
    plt.close()

    print(f"📊 Backtest saved to {file_path}")

    return df