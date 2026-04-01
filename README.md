# DeFi Convexity Risk Engine

## Overview

This project models and quantifies risk exposures in Uniswap v3 liquidity provision using a quantitative finance framework.

It focuses on understanding how LP positions behave under price movements, volatility, and jump risk.

## Key Insight

Providing liquidity in AMMs is structurally equivalent to **selling convexity (short gamma)**.

LPs earn fees, but are exposed to:

* nonlinear losses (impermanent loss)
* volatility risk
* jump (tail) risk

This project builds a simple risk engine to measure these effects.

## Features

* Piecewise Uniswap v3 LP valuation
* Analytical Delta and Gamma computation
* Scenario-based PnL analysis
* Jump risk modeling (Poisson process)
* Expected loss estimation
* Fee vs risk comparison

## Example Output

| Scenario | Value | Delta | Gamma | Expected Jump Loss | Fees |
| -------- | ----- | ----- | ----- | ------------------ | ---- |
| Bear     | ...   | ...   | ...   | ...                | ...  |

## Methodology

The LP position is modeled using Uniswap v3 liquidity math:

* Value derived from token0/token1 decomposition
* Delta = ∂V/∂P
* Gamma = ∂²V/∂P²

Jump risk is approximated using a Poisson arrival model:

* P(jump) = 1 - exp(-λT)

## Why This Matters

DeFi yields are often misunderstood as deterministic.

In reality:

* LP returns depend on volatility and price path
* fees must compensate for convexity risk

This framework helps evaluate:

> “Am I being paid enough to be short gamma?”

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

## Author

DeFi Quant Analyst focused on AMM risk, convexity, and yield modeling.
