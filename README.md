![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Status](https://img.shields.io/badge/status-research-green)

# DeFi Convexity Risk Engine

## Overview

This project studies **Uniswap v3 liquidity provision as a convexity-selling strategy** and builds a **Monte Carlo framework for LP strategy optimization**.

It combines:

- convexity and impermanent loss (IL) analysis  
- LP vs HODL simulation  
- dynamic rebalancing with transaction costs  
- risk-adjusted optimization of LP range width  

The project evolves from **risk measurement → strategy design**, with the goal of identifying **robust, decision-grade LP strategies**.

---

## Key Insight

> Providing liquidity in Uniswap v3 is economically equivalent to selling a volatility strangle.

LPs earn fees (premium) but are exposed to nonlinear losses during large price movements due to **negative convexity**.

---

## Core Economic Idea

Providing liquidity in concentrated AMMs can be interpreted as **selling convexity (short gamma)**:

- LP inventory is continuously rebalanced as price moves  
- this creates nonlinear exposure to price changes  
- losses materialize in trending or high-volatility regimes  

> LPing is not passive yield — it is a **short-volatility strategy**.

---

## Convexity & Impermanent Loss

### Convexity Profile

![Risk Curves](outputs/risk_curves.png)

- Delta decreases as price moves due to inventory rebalancing  
- Gamma is strictly negative within the active range  
- Outside the range, Gamma → 0 (inactive liquidity)  

---

### Convexity Cost (LP − HODL)

![Convexity Cost](outputs/convexity_cost.png)

- Near entry: LP ≈ HODL  
- Large moves: LP underperforms nonlinearly  
- Loss grows with price deviation  

> **LP − HODL = cost of short convexity**

---

### LP vs HODL Payoff

![PnL Comparison](outputs/pnl_comparison.png)

- HODL → linear payoff  
- LP → concave payoff  
- Underperformance in trends  

---

### Simulation: Distribution of Outcomes

![Simulation](outputs/simulation_distribution.png)

- HODL → higher variance + upside  
- LP → compressed distribution  
- LP trades tail risk for fee income  

---

## Fee vs Convexity Trade-off

LP profitability depends on:

- **Fee income (positive carry)**  
- **Convexity cost (negative drift)**  

| Market Regime | Outcome |
|--------------|--------|
| Range-bound + high volume | LP profitable |
| Trending / high volatility | LP underperforms |

> LP is a **volatility-harvesting strategy**.

---

## Strategy Optimization (Main Contribution)

We extend the framework from risk analysis to **strategy design**.

### Objective

Optimize:

- LP range width  
- rebalancing policy  

to maximize:

> **Expected (Fees − IL − Costs)**

under stochastic price dynamics.

---

## Model Setup

### Price Process

- Geometric Brownian Motion (GBM)  
- σ ∈ {0.2, 0.4, 0.6, 0.8}  
- Monte Carlo simulation  

---

### Strategy Specification

- log-symmetric LP ranges (5% → 30%)  
- dynamic rebalancing (out-of-range trigger)  
- segment-based IL realization  
- explicit gas + slippage costs  

---

### Transaction Costs

- fixed gas cost  
- slippage ∝ capital / width  

→ narrow ranges are more expensive to maintain  

---

### Impermanent Loss (Key Improvement)

IL is modeled **locally**:

- measured vs last rebalance price  
- resets at each rebalance  
- becomes **strategy-dependent**

---

## Optimization Results

### Optimal Width vs Volatility

![Optimal Width](outputs/optimal_width_vs_volatility.png)

| Volatility (σ) | Optimal Width |
|----------------|--------------|
| 0.2 | ~20% |
| 0.4 | ~16–20% |
| 0.6 | ~20% |
| 0.8 | ~18–22% |

> Optimal width lies in a **stable 15–22% band**

---

### Performance vs Volatility

![Performance](outputs/performance_vs_volatility.png)

- LP outperformance increases with volatility  
- driven by higher fee generation  

---

### Fee vs Width

![Fee Income](outputs/fee_income_vs_width.png)

- narrower ranges → higher fee density  
- diminishing returns at extreme narrow widths  

---

## Robustness Analysis

### Transaction Costs

| Gas | Slippage | Optimal Width |
|-----|----------|---------------|
| Low | Low | ~14% |
| Medium | Medium | ~20% |
| High | High | ~30% |

→ higher friction → wider optimal ranges  

---

### Stability

Strategy remains robust across:

- volatility regimes  
- random seeds  
- time horizons  

---

## Martingale Insight (Key Theoretical Result)

Under zero fees:

> **LP − HODL is a supermartingale**

- negative expected drift  
- driven by concavity (short gamma)  

With fees:

- a positive drift term is introduced  
- profitability depends on:
  - volatility  
  - costs  
  - rebalancing  

> Strategy design = **controlling convexity so drift ≥ 0**

---

## Final Strategy

We select:

- **Width:** ~20%  
- **Rebalance:** out-of-range  
- **Capital:** fixed  
- **Costs:** explicit  

### Result

- Outperforms HODL in majority of paths  
- High variance  
- Sensitive to volatility  

> LP is a **risk-managed volatility harvesting strategy**, not a guaranteed outperformer.

---

## Project Structure
src/
├── stochastic/ # price, fees, LP simulation
├── strategy/ # Uniswap v3 strategy logic
├── optimization/ # grid search & objective
├── analysis/ # LP − HODL, martingale tests

---

## Limitations

- GBM price model  
- simplified liquidity math  
- no endogenous order flow  
- fixed fee tier  

---

## Future Work

- historical backtesting  
- multi-range LP strategies  
- order-flow driven volume  
- on-chain data integration  
- dashboard / API layer  

---

## Author

Gennaro Cepparulo  
Quantitative research on AMM risk, convexity, and LP strategy design


---

If you want, next step we can:

👉 :contentReference[oaicite:0]{index=0}  
👉 or :contentReference[oaicite:1]{index=1}  

