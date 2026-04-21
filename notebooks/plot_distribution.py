import matplotlib.pyplot as plt
import numpy as np

def plot_lp_vs_hodl_distribution(lp_minus_hodl_list):

    plt.figure()

    plt.hist(lp_minus_hodl_list, bins=50)

    plt.axvline(0, linestyle="--")

    plt.title("Distribution of LP vs HODL Outcomes")
    plt.xlabel("LP - HODL")
    plt.ylabel("Frequency")

    plt.grid(True)

    plt.savefig("outputs/lp_vs_hodl_distribution.png")
    plt.close()