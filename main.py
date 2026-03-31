from src.lp_model import value_lp, delta_gamma_lp
from src.risk_metrics import expected_jump_loss, gamma_exposure
from src.scenarios import build_dashboard

if __name__ == "__main__":
    print("\n🔄 Fetching real-time price data...\n")
    
    # Build dashboard with real ETH price
    df = build_dashboard(use_real_price=True, token_id="ethereum")
    
    print("\n--- CONVEXITY DASHBOARD ---")
    print(df)
    df.to_csv("outputs/sample_dashboard.csv")
