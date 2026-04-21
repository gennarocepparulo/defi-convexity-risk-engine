# Stopping Times and Rebalancing

## Definition

A stopping time τ is a random time such that:

{τ ≤ t} ∈ 𝔽_t

Meaning:
→ the decision to stop depends only on current information

---

## LP Rebalancing as Stopping Time

In this project:

Rebalancing occurs when:

price ∉ [lower_bound, upper_bound]

This defines a stopping time:

τ = inf { t : price exits range }

---

## Interpretation

Rebalancing is not arbitrary:

→ it is a **first exit time problem**

This introduces:

- path dependence
- regime switching behavior
- endogenous resets of IL

---

## Economic Meaning

Each rebalance:

- realizes accumulated IL
- resets the reference price
- restarts fee accumulation

This creates a **segmented PnL process**

---

## Trade-Off

Narrow ranges:

→ frequent stopping times  
→ high fees  
→ high costs

Wide ranges:

→ rare stopping times  
→ lower fees  
→ smoother exposure

---

## Connection to Optimization

The optimizer is effectively choosing:

→ a stopping time distribution

by controlling:

→ width of the range

---

## Takeaway

LP strategy design = **control of stopping times**

Width determines:

- how often you trade
- how IL is realized
- how convexity is monetized
