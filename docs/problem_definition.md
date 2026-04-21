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
## Martingales, Convexity, and LP PnL Decomposition

The project studies liquidity provision in concentrated AMMs through the lens of stochastic processes, convexity, and discrete control.
The starting point is the martingale benchmark. Under the GBM specification used throughout the simulations, the underlying price is modeled as a stochastic process with no directional alpha. In this benchmark, the relevant comparison is not whether LP performs well in a subset of paths, but whether LP can systematically overcome the structural effect of its payoff geometry.
The key theoretical observation is that the LP payoff is concave relative to HODL. This concavity is the source of impermanent loss: when price evolves randomly around the entry point, the LP position underperforms the corresponding passive inventory because it is exposed to negative convexity. By Jensen’s inequality, a concave transform of a martingale has a negative expected drift. This provides the mathematical basis for interpreting LP − HODL as a supermartingale in the absence of fees.
This leads naturally to the following decomposition:
LP PnL≈fees−convexity drag−transaction costs\text{LP PnL} \approx \text{fees} - \text{convexity drag} - \text{transaction costs}LP PnL≈fees−convexity drag−transaction costs
or, equivalently,
LP≈θ−γ−costs.\text{LP} \approx \theta - \gamma - \text{costs}.LP≈θ−γ−costs.
In this interpretation:

Fees (θ\thetaθ) represent the positive carry earned from order flow and realized activity.
Convexity drag (γ\gammaγ) captures the Jensen gap associated with the concave LP payoff and is the economic content of impermanent loss.
Costs arise from discrete rebalancing, including gas expenditure, slippage, and other implementation frictions.

This decomposition unifies the main findings of the project. The LP position is not a passive yield strategy, but a controlled short-convexity position whose profitability depends on whether fee income can offset convexity losses and trading frictions. Width and rebalancing policies do not create alpha by themselves; they only modify the magnitude and timing of exposure to this trade-off.

## Notes

This document defines the conceptual scope before implementation.
It will evolve as assumptions are finalized and optimization experiments are added.
