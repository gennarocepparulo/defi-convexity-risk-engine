import matplotlib.pyplot as plt

df = simulate_lp_minus_hodl(...)

plt.figure(figsize=(8, 4))
plt.plot(df["step"], df["lp_minus_hodl"])
plt.axhline(0.0, color="black", linewidth=1, linestyle="--")
plt.xlabel("Step")
plt.ylabel("LP - HODL")
plt.title("LP - HODL Over Time")
plt.grid(True)
plt.tight_layout()
plt.show()