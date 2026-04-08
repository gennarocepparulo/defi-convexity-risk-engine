# Problem Definition — Uniswap v3 LP Strategy Optimization

## Objective

Determine the optimal Uniswap v3 liquidity provision strategy under stochastic price dynamics.

The primary decision variable is the **liquidity range width**, with optional extensions to include:

- rebalancing frequency
- trigger-based repositioning
- capital allocation across multiple ranges

The strategy should maximize **expected net LP returns** while accounting for:

- fee income
- impermanent loss (IL)
- transaction costs (gas + slippage)

---

## Research Question

Given a stochastic price process for the underlying asset, what liquidity range width and rebalancing policy maximize the LP’s expected net performance?

---

## Model Components

### 1. Price Process
Candidate assumptions:
- Geometric Brownian Motion (GBM)
- Mean-reverting dynamics
- Jump-diffusion extension

### 2. LP Payoff Components
The LP net outcome combines:

- **Fee income**
- **Impermanent loss**
- **Transaction costs**
  - gas costs
  - slippage
  - optional repositioning costs

### 3. Rebalancing Logic
Possible policies:
- no rebalancing
- threshold-based rebalancing
- time-based rebalancing

---

## Objective Function

Candidate optimization targets:

1. **Expected net return**
2. **Sharpe ratio**
3. **Fee income vs IL trade-off**
4. **Risk-adjusted expected return**

Baseline formulation:

\[
\max_{\theta} \; \mathbb{E}[\text{Fees} - \text{IL} - \text{Transaction Costs}]
\]

where \(\theta\) includes:
- range width
- rebalancing rule
- optional capital split

---

## Constraints

The optimization is subject to:

- capital allocation constraints
- lower/upper bounds on range width
- gas cost inclusion
- rebalancing feasibility constraints

---

## Initial Scope

The first implementation focuses on:

- single LP position
- one asset pair
- one range-width parameter
- simple stochastic price paths
- explicit fee, IL, and transaction cost decomposition

---

## Planned Output

The model should produce:

- optimal range width
- expected fee income
- expected impermanent loss
- expected transaction costs
- net PnL distribution
- comparison versus passive LP and HODL

---

## Notes

This document defines the conceptual scope before implementation.
It will evolve as assumptions are finalized and optimization experiments are added.
