import os
os.makedirs("outputs", exist_ok=True)
from src.lp_model import value_lp, delta_gamma_lp
from src.risk_metrics import expected_jump_loss, gamma_exposure
from src.scenarios import build_dashboard
from src.visualizer import generate_risk_curves
from src.scenarios import build_dashboard
from src.price_fetcher import get_coingecko_price

if __name__ == "__main__":
    print("\n🔄 Fetching real-time price data...\n")
    
    # Get live price
    price = get_coingecko_price("ethereum")
    
    # Build dashboard
    df = build_dashboard(use_real_price=True, token_id="ethereum")
    
    print("\n--- CONVEXITY DASHBOARD ---")
    print(df)

    # Save output
    df.to_csv("outputs/sample_dashboard.csv")

    # Generate plots
    generate_risk_curves(
        P_a=1800,
        P_b=2200,
        L=1000,
        current_price=price
    )

    # --- Interpretation layer ---
    print("\n--- RISK INTERPRETATION ---")
    for idx, row in df.iterrows():
        if row["Risk/Reward"] is not None:
            if row["Risk/Reward"] > 3:
                print(f"⚠️ {idx}: Risk too high vs fees")
            else:
                print(f"✅ {idx}: Acceptable risk level")
