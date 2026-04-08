from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class GBMConfig:
    s0: float
    mu: float
    sigma: float
    t_horizon: float
    n_steps: int
    n_paths: int
    seed: Optional[int] = None


@dataclass
class OUConfig:
    x0: float
    theta: float      # long-run mean
    kappa: float      # mean reversion speed
    sigma: float
    t_horizon: float
    n_steps: int
    n_paths: int
    seed: Optional[int] = None


def simulate_gbm_paths(config: GBMConfig) -> np.ndarray:
    """
    Simulate geometric Brownian motion price paths.

    Returns
    -------
    np.ndarray
        Shape: (n_steps + 1, n_paths)
    """
    if config.seed is not None:
        np.random.seed(config.seed)

    dt = config.t_horizon / config.n_steps
    paths = np.zeros((config.n_steps + 1, config.n_paths))
    paths[0, :] = config.s0

    for t in range(1, config.n_steps + 1):
        z = np.random.standard_normal(config.n_paths)
        paths[t, :] = paths[t - 1, :] * np.exp(
            (config.mu - 0.5 * config.sigma**2) * dt + config.sigma * np.sqrt(dt) * z
        )

    return paths


def simulate_ou_paths(config: OUConfig, positive: bool = True) -> np.ndarray:
    """
    Simulate a mean-reverting process.
    If positive=True, interprets x as log-price and returns exp(x).
    """
    if config.seed is not None:
        np.random.seed(config.seed)

    dt = config.t_horizon / config.n_steps
    x = np.zeros((config.n_steps + 1, config.n_paths))
    x[0, :] = config.x0

    for t in range(1, config.n_steps + 1):
        z = np.random.standard_normal(config.n_paths)
        x[t, :] = (
            x[t - 1, :]
            + config.kappa * (config.theta - x[t - 1, :]) * dt
            + config.sigma * np.sqrt(dt) * z
        )

    if positive:
        return np.exp(x)

    return x