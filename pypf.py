import matplotlib

matplotlib.use("Agg")  # headless: must be set before pyplot import

import os

import pandas as pd
from pypfopt import CLA, EfficientFrontier, expected_returns, plotting, risk_models
import matplotlib.pyplot as plt


def epf(df, static_dir="./static"):
    """Compute max-Sharpe allocations and save frontier plots.

    Returns (weights_dict, ef_perf, cla_perf) where perf tuples are
    (expected_return, volatility, sharpe).
    """
    if df is None or df.empty:
        raise ValueError("Empty price DataFrame.")
    df = df.sort_index().dropna(how="any")
    if df.shape[1] < 1 or len(df) < 2:
        raise ValueError("Need at least 1 asset and 2 overlapping price rows.")

    os.makedirs(static_dir, exist_ok=True)
    pie_path = os.path.join(static_dir, "plt.png")
    frontier_path = os.path.join(static_dir, "plt2.png")

    mu = expected_returns.mean_historical_return(df)
    s = risk_models.CovarianceShrinkage(df).ledoit_wolf()

    ef = EfficientFrontier(mu, s)
    raw_weights = ef.max_sharpe()
    ef_perf = ef.portfolio_performance(verbose=False)

    # Pie chart of max-Sharpe weights
    plt.figure()
    pd.Series(raw_weights).plot.pie(
        figsize=(5, 5), autopct=lambda p: f"{p:.2f}%"
    )
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(pie_path, dpi=200)
    plt.close()

    # CLA frontier (used for the efficient-frontier plot)
    cla = CLA(mu, s)
    cla.max_sharpe()
    cla_perf = cla.portfolio_performance(verbose=False)

    plt.figure()
    plotting.plot_efficient_frontier(cla, show_assets=False)
    plt.tight_layout()
    plt.savefig(frontier_path, dpi=200)
    plt.close()

    return cla.clean_weights(), ef_perf, cla_perf
