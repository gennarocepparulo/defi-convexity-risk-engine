# DeFi Convexity Risk Engine

## Overview

This project models the risk profile of Uniswap v3 liquidity provision using a quantitative finance framework.

It analyzes LP positions as nonlinear financial instruments and evaluates their sensitivities (Delta, Gamma), convexity exposure, and jump risk under different market scenarios.

The model integrates real-time market data and provides a structured way to assess whether fee income compensates for risk.

---

## Key Insight

> Providing liquidity in Uniswap v3 is economically equivalent to selling a volatility strangle.

LPs earn fees (premium) but are exposed to losses during large price movements due to negative convexity.

---

## Core Idea

Providing liquidity in concentrated AMMs can be interpreted as **selling convexity (short gamma)**:

- LPs continuously rebalance inventory as price moves  
- This creates nonlinear exposure to price changes  
- Losses occur during high volatility regimes  

> LPing is not passive yield — it is a short volatility strategy.

---

## What I Built

- Piecewise valuation model for Uniswap v3 LP positions  
- Analytical Delta and Gamma computation across price ranges  
- Scenario-based PnL engine (bear / base / bull)  
- Jump-risk estimation via Poisson arrival process  
- Risk/Reward metric comparing expected loss vs fee income  
- Real-time ETH price integration via CoinGecko API  

---

## Risk Visualization

The following chart shows the local Delta and Gamma across price levels:

![Risk Curves](outputs/risk_curves.png)

### Interpretation

- **Delta** decreases as price increases due to inventory rebalancing  
- **Gamma** is negative within the active range → LP is short convexity  
- Outside the range, Gamma approaches zero as liquidity becomes inactive  

---

## Example Output

The engine produces a convexity dashboard across market scenarios:

| Scenario | Price | Value | Delta | Gamma | Expected Loss | Fees | Risk/Reward |
|----------|------|------|------|------|---------------|------|-------------|
| Bear     | ↓    | ↓    | ↑    | -    | High Loss     | Low  | High        |
| Base     | →    | →    | Mid  | -    | Medium Loss   | Low  | Medium      |
| Bull     | ↑    | →    | 0    | 0    | Low Loss      | Low  | Low         |

---

## Methodology

The LP position is modeled using Uniswap v3 liquidity mechanics:

- Token0 / token1 decomposition of LP value  
- Delta = ∂V/∂P  
- Gamma = ∂²V/∂P²  
- Scenario PnL under price shocks  
- Jump risk modeled via Poisson arrival probability  
- Expected loss compared against estimated fee income  

---

## Why It Matters

DeFi yield is often presented as passive income.

This model shows that LP returns are primarily driven by:

- price path  
- volatility  
- convexity exposure  

> Risk, not yield, is the dominant driver of LP outcomes.

---

## Future Work

* Historical backtesting with real price data
* Dynamic rebalancing strategies
* Integration with on-chain data (Dune, APIs)
* Streamlit dashboard for real-time monitoring

## Convexity Profile of a Uniswap v3 LP

The following chart illustrates the local Delta and Gamma of a concentrated liquidity position.

![Risk Curves](outputs/risk_curves.png)

Key observations:
- Delta decreases with price due to inventory rebalancing
- Gamma is strictly negative within the active range
- The LP is effectively short volatility

---
## Convexity Cost (Impermanent Loss)

![Convexity Cost](outputs/convexity_cost.png)

The difference between LP and HODL payoffs isolates the convexity effect embedded in liquidity provision.

- Near the initial price, LP and HODL perform similarly  
- As price moves away, LP increasingly underperforms  
- Losses grow nonlinearly with price deviation  

> The quantity LP − HODL represents the cost of being short convexity.

This confirms that LPs systematically give up performance in trending markets in exchange for fee income.

## LP vs HODL Comparison

![PnL Comparison](outputs/pnl_comparison.png)

### Interpretation

- HODL exhibits linear exposure to price  
- LP value is concave due to inventory rebalancing  
- LP underperforms in trending markets  
- The difference represents **impermanent loss**

> LP positions sacrifice upside and downside to earn fees.

## Simulation: LP vs HODL Outcomes

![Simulation](outputs/simulation_distribution.png)

### Interpretation

- HODL exhibits higher variance and higher upside potential  
- LP outcomes are more concentrated due to truncated exposure  
- LP sacrifices extreme gains in exchange for fee income  

> LP positions reduce variance but introduce convexity-driven underperformance in trending markets.
## Fee vs Convexity Trade-off

Simulation results show that LP profitability depends on the balance between:

- fee income (positive carry)
- convexity cost (negative PnL in trends)

When volatility is high and price trends strongly, convexity losses dominate.

When volume is high and price remains range-bound, fees can compensate losses.

> LP is effectively a volatility-selling strategy that requires sufficient flow to be profitable.
## Limitations
- simplified jump specification
- no full calibration to market data yet
- no on-chain data pipeline yet

### 📊 Mechanism: Fee Concentration vs Width

![Fee Income](outputs/fee_income_vs_width.png)

Fee generation decreases monotonically as width increases.

Key observations:

- Narrower ranges significantly increase fee density  
- Higher volatility shifts the entire fee curve upward  
- The marginal benefit of narrowing the range diminishes at very low widths  

This confirms that **fee concentration is the primary driver of LP returns**.

---

### 📊 Strategy Outcome: Performance vs Volatility

![Performance](outputs/performance_vs_volatility.png)

LP strategies benefit strongly from higher volatility:

- Mean LP outperformance vs HODL increases with σ  
- Higher volatility leads to more trading activity and fee accrual  

This demonstrates that LP positions act as **volatility-harvesting strategies**.

---

### 📊 Decision Rule: Optimal Width vs Volatility

![Optimal Width](outputs/optimal_width_vs_volatility.png)

The optimal width remains within a stable interior range:

- No corner solutions (neither very narrow nor very wide)  
- Only mild variation across volatility regimes  

This suggests that:

> Optimal LP positioning is robust to volatility changes, provided rebalancing is active.

### Robustness: Transaction Cost Sensitivity

We test robustness of the optimal LP width under varying transaction costs.
As gas and slippage increase, the optimizer selects wider LP ranges:

| Gas | Slippage | Optimal Width |
|-----|----------|---------------|
| Low | Low | ~14% |
| Baseline | Medium | ~20% |
| High | High | ~30% |

This confirms that operational friction pushes LP strategies toward wider,
more passive ranges, even under identical price dynamics.
## Roadmap
- historical backtesting
- dynamic rebalancing strategies
- on-chain data integration
- Streamlit dashboard

## Author

DeFi Quant Analyst focused on AMM risk, convexity, and yield modeling.
