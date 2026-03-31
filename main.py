from src.lp_model import value_lp, delta_gamma_lp
from src.risk_metrics import expected_jump_loss, gamma_exposure
from src.scenarios import build_dashboard

if __name__ == "__main__":
    df = build_dashboard()
    print("\n--- CONVEXITY DASHBOARD ---")
    print(df)
