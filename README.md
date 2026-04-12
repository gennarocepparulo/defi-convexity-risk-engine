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

## New: Uniswap v3 LP Strategy Optimization

This module extends the risk engine from **risk measurement** to **strategy design** for Uniswap v3 liquidity provision.

It introduces:

- dynamic liquidity provision strategies  
- trigger-based and rule-based rebalancing  
- optimization of LP range width  
- explicit modeling of gas and slippage costs  

The goal is to determine the liquidity range and rebalancing policy that maximize expected net LP returns under stochastic price dynamics.

See: [`docs/problem_definition.md`](docs/problem_definition.md)

Uniswap v3 LP Strategy Optimization
Objective

This project studies how a liquidity provider (LP) should choose the width of a liquidity range and apply dynamic rebalancing in Uniswap v3 under stochastic price dynamics.

The goal is to identify LP strategies that maximize expected excess returns relative to HODL, accounting explicitly for:

trading fee income
price exposure through the AMM mechanism
impermanent loss (IL)
rebalancing costs (gas + execution slippage)
🧠 Methodology
Price Dynamics

The spot price is modeled as a Geometric Brownian Motion (GBM):

Drift: μ
Volatility: σ ∈ {0.2, 0.4, 0.6, 0.8}

For each volatility regime, we run Monte Carlo simulations to capture the distribution of LP outcomes under price uncertainty.

LP Strategy Specification

For each simulated price path, we evaluate LP strategies across a grid of log-symmetric range widths (5% → 30%), centered on the current price.

Each strategy includes:

Dynamic rebalancing (threshold-based)
Range recentering when price exits the active interval
Segment-based IL realization (reset at each rebalance)
Explicit transaction costs (gas + slippage proxy)
Rebalancing Rule (Explicit)

A rebalance is triggered when:

|P_t - P_center| / P_center ≥ threshold

At each rebalance:

The LP range is recentered at current price
Impermanent loss is realized locally
Fee accumulation is reset
A transaction cost is applied
Impermanent Loss Modeling (Clarified)

Impermanent loss is not computed globally from initial entry.

Instead:

IL is computed relative to the last rebalance price
Each rebalance creates a new segment
This makes IL an endogenous outcome of the strategy

This is a critical modeling improvement:
IL now depends on strategy behavior, not just the price path.

Optimization Objective

For each strategy θ:

Objective(θ)=E[Fees(θ)−IL(θ)−Rebalancing Costs(θ)]
Objective(θ)=E[Fees(θ)−IL(θ)−Rebalancing Costs(θ)]

This formulation:

avoids double-counting price exposure
ensures IL is strategy-dependent
captures the true LP vs HODL trade-off
📈 Key Result: Stable Interior Band

Across volatility regimes, the optimizer identifies a stable interior band of optimal widths, rather than corner solutions.

Volatility (σ)	Optimal Width
0.2	~20%
0.4	~16%
0.6	~20%
0.8	~18%
Key Observation

The optimal LP width lies consistently in the:

🎯 15% – 22% range

with only mild variation across volatility levels.

📊 Fee Decomposition

Narrow ranges → higher fees
Wide ranges → lower capital efficiency
But narrow ranges also trigger:
more rebalances
more IL realization
higher costs
📊 Performance vs Volatility

Key result:

LP performance increases with volatility
Higher σ → more trading → more fees

This confirms:

🧠 LP strategies are volatility-harvesting mechanisms

📊 Risk Profile

A non-trivial result:

Probability of underperforming HODL decreases with volatility
σ	Prob(LP < HODL)
0.2	~48%
0.4	~42%
0.6	~39%
0.8	~35%
📊 Risk-Adjusted Performance

Peak risk-adjusted performance occurs in the same interior band
Confirms robustness of the optimal width
🔍 Economic Interpretation

The interior optimal width emerges from a three-way trade-off:

1. Fee Concentration
Narrow ranges → higher fee density
2. Volatility-Induced Turnover
Narrow ranges exit more often → more rebalancing
3. Realized Impermanent Loss
Rebalancing realizes IL locally
Prevents large drift, but increases turnover cost
Core Mechanism

Dynamic rebalancing transforms IL from a passive loss into an active cost process.

🧠 Key Insight

Optimal Uniswap v3 liquidity provision is governed by a balance between:

fee concentration and volatility-induced turnover

Under dynamic rebalancing, this leads to a:

🎯 stable interior optimal width (~15–22%)

🚀 Practical Implications

For a real-world LP strategy (e.g. €5k actively managed position):

Avoid:
❌ Very narrow (<10%) → excessive churn, high costs
❌ Very wide (>30–40%) → diluted fee generation
Target:
✅ Moderate width (~15–22%)

This balances:

fee generation
operational efficiency
risk control
📌 Scope and Limitations
Current Model
Single-range LP strategies
Threshold-based rebalancing
GBM price dynamics
Exogenous volume proxy
Limitations
No endogenous order flow modeling
No Uniswap v3 exact liquidity math (approximation used)
Fixed fee tier
No multi-range allocation
Future Extensions
Multi-range LP strategies
Adaptive (state-dependent) rebalancing
Order flow / volume modeling
Fee tier optimization
Full Uniswap v3 valuation engine

## Roadmap
- historical backtesting
- dynamic rebalancing strategies
- on-chain data integration
- Streamlit dashboard

## Author

DeFi Quant Analyst focused on AMM risk, convexity, and yield modeling.


[def]: docs/problem_definition.md
