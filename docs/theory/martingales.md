# Martingales and LP PnL

## Intuition

A stochastic process is a martingale if its expected future value,
given current information, equals its present value:

E[X_{t+1} | 𝔽_t] = X_t

In financial terms:
→ no predictable drift
→ no arbitrage under the chosen measure

---

## Application to LP Strategies

In our framework:

- Price follows GBM
- Under risk-neutral assumptions, price is a martingale (after discounting)

However:

LP PnL is **not a martingale**

Why?

Because it includes:

- fee income (positive drift)
- impermanent loss (convexity effect)
- rebalancing costs

---

## Key Insight

LP strategies introduce **non-martingale structure** via:

→ fees → positive drift  
→ convex payoff → path dependency  

This means:

LP ≠ passive exposure  
LP = **active transformation of price dynamics**

---

## Interpretation

If:

E[LP_t − HODL_t] > 0

then:

→ the LP strategy extracts value from volatility  
→ the process embeds a **statistical edge**

---

## Connection to This Project

The optimization framework explicitly searches for:

argmax E[Fees − IL − Costs]

This is equivalent to:

→ finding deviations from martingale behavior  
→ exploiting convexity + trading flow

---

## Takeaway

Uniswap v3 LP is not a neutral strategy.

It is a **structured deviation from martingale pricing**, driven by:

- convexity (IL)
- flow (fees)
- control (rebalancing)