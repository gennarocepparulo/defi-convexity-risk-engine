# DeFi Convexity Risk Engine

## Overview

This project studies Uniswap v3 liquidity provision as a convexity-selling strategy and develops a Monte Carlo framework to optimize LP range width under stochastic price dynamics.

It combines:

- convexity and impermanent loss (IL) analysis
- simulation-based LP vs HODL comparison
- dynamic rebalancing with transaction costs
- risk-adjusted strategy optimization

The project evolves from risk measurement to strategy design, with the final objective of identifying robust liquidity provision strategies rather than analyzing LP risk in isolation.

---

## Key Insight

Providing liquidity in Uniswap v3 is economically equivalent to selling a volatility strangle.

LPs earn fees (premium) but are exposed to nonlinear losses during large price movements due to negative convexity.

---

## Core Economic Idea

Providing liquidity in concentrated AMMs can be interpreted as selling convexity (short gamma):

- LP inventory is continuously rebalanced as price moves
- this creates nonlinear exposure to price changes
- losses materialize in high-volatility or trending regimes

LPing is not passive yield — it is a short-volatility strategy.

---

## Risk Engine: Convexity and Impermanent Loss

### Convexity Profile of a Uniswap v3 LP

The following chart illustrates the local Delta and Gamma of a concentrated liquidity position:

outputs/risk_curves.png

Key observations:

- Delta decreases as price moves due to inventory rebalancing
- Gamma is strictly negative within the active range
- Outside the range, Gamma approaches zero as liquidity becomes inactive

This confirms that LP positions are structurally short convexity.

---

### Convexity Cost (Impermanent Loss)

outputs/convexity_cost.png

The difference between LP and HODL payoffs isolates the convexity cost embedded in liquidity provision:

- Near the initial price, LP and HODL perform similarly
- As price moves away, LP increasingly underperforms
- Losses grow nonlinearly with price deviation

LP minus HODL quantifies the cost of being short convexity.

---

### LP vs HODL Payoff Comparison

outputs/pnl_comparison.png

Interpretation:

- HODL has linear exposure to price
- LP value is concave due to inventory rebalancing
- LP underperforms in trending markets

LP positions sacrifice upside and downside to earn fees.

---

### Simulation: Distribution of Outcomes

outputs/simulation_distribution.png

Interpretation:

- HODL exhibits higher variance and higher upside potential
- LP outcomes are more concentrated
- LP reduces variance but introduces convexity-driven underperformance

LPing trades tail exposure for fee income.

---

## Fee vs Convexity Trade-off

Simulation results show that LP profitability depends on the balance between:

- fee income (positive carry)
- convexity cost (negative PnL in trends)

When volatility is high and price trends strongly, convexity losses dominate.
When volume is high and price remains range-bound, fees can compensate losses.

LP is a volatility-harvesting strategy that requires sufficient flow to be profitable.

---

## What This Project Builds

### Core Risk Engine

- piecewise valuation model for Uniswap v3 LP positions
- analytical Delta and Gamma across price ranges
- scenario-based PnL analysis
- jump-risk approximation (Poisson process)
- LP vs HODL convexity attribution

---

## Uniswap v3 LP Strategy Optimization (Main Contribution)

This module extends the project from risk analysis to strategy optimization.

### Objective

Determine how a liquidity provider should choose:

- the width of the liquidity range
- a dynamic rebalancing policy

to maximize risk-adjusted excess returns relative to HODL under stochastic price dynamics.

---

## Price Dynamics

The spot price is modeled as a Geometric Brownian Motion (GBM):

- drift: mu
- volatility: sigma in {0.2, 0.4, 0.6, 0.8}

For each volatility regime, Monte Carlo simulations are used to evaluate the full distribution of LP outcomes.

---

## Strategy Specification

For each simulated price path, LP strategies are evaluated across a grid of log-symmetric range widths (5% to 30%), centered on the current price.

Each strategy includes:

- dynamic rebalancing when price exits the active range
- range recentering at each rebalance
- segment-based IL realization
- explicit transaction costs

---

## Transaction Cost Model

Rebalancing costs include:

- gas (fixed component)
- execution slippage, modeled as:

slippage proportional to capital divided by width

This makes narrow ranges more expensive to maintain, reflecting real operational frictions.

---

## Impermanent Loss Modeling (Critical Improvement)

Impermanent loss is not computed globally from the initial entry price.

Instead:

- IL is measured relative to the last rebalance price
- each rebalance creates a new segment
- IL becomes an endogenous outcome of the strategy

This avoids treating IL as a purely path-based artifact and makes it strategy-dependent.

---

## Optimization Objective

For each strategy theta:

Expected value of [Fees(theta) - IL(theta) - Rebalancing Costs(theta)]

Strategies are ranked using a risk-adjusted (Sharpe-like) metric:

mean(PnL) divided by std(PnL)

This prioritizes robustness rather than raw expected returns.

---

## Monte Carlo Results: Volatility Sweep

Across volatility regimes, the optimizer identifies a stable interior band of optimal widths.

| Volatility (sigma) | Optimal Width |
|-------------------|---------------|
| 0.2 | ~20% |
| 0.4 | ~16–20% |
| 0.6 | ~20% |
| 0.8 | ~18–22% |

### Key Observation

The optimal LP width lies consistently in the 15%–22% range, with only mild variation across volatility levels.

---

## Economic Interpretation

The interior optimum emerges from a three-way trade-off:

1. Fee concentration  
   Narrow ranges lead to higher fee density.

2. Volatility-induced turnover  
   Narrow ranges exit more often, triggering more rebalancing.

3. Realized impermanent loss  
   Rebalancing realizes IL locally and increases operational costs.

Dynamic rebalancing transforms IL from a passive loss into an active cost process.

---

## Practical Implications

For a real-world actively managed LP position:

Avoid:
- very narrow (<10%): excessive churn and high costs
- very wide (>30–40%): diluted fee generation

Target:
- moderate width (approximately 15–22%)

This balances fee generation, operational efficiency, and downside risk.

---
## Final Strategy Selection

Based on optimization, volatility sweeps, and robustness analysis, we select a log-symmetric Uniswap v3 LP strategy with a 20% width centered on the current price and rebalancing upon range exit.

This strategy lies at the center of a robust optimal band (15–25%) and remains stable across volatility regimes, random seeds, transaction costs, and investment horizons. Narrower ranges generate higher fees but suffer from excessive turnover, while wider ranges dilute fee capture.

An end-to-end execution of the selected strategy (`run_strategy.py`) confirms the expected risk profile: the strategy outperforms HODL in a majority of paths but exhibits high variance, with mean performance sensitive to volatility and realization. This behavior is consistent with LP strategies as volatility-harvesting mechanisms rather than guaranteed outperformers.

The selected configuration is therefore recommended as a defensible, decision-grade LP strategy under realistic market frictions.

## Scope and Limitations

Current model:

- single-range LP strategies
- threshold-based rebalancing
- GBM price dynamics
- exogenous volume proxy

Limitations:

- no endogenous order-flow modeling
- approximate Uniswap v3 liquidity math
- fixed fee tier

---

## Future Extensions

- finer grid and adaptive width selection
- sensitivity analysis to transaction cost assumptions
- multi-range LP strategies
- order-flow-driven volume modeling
- full Uniswap v3 valuation engine
- historical backtesting with on-chain data

---

## Author

Gennaro Cepparulo  
Quantitative research focused on AMM risk, convexity, and LP strategy design.
