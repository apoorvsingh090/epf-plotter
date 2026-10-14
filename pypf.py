import matplotlib

matplotlib.use("Agg")  # headless: must be set before pyplot import

import os

import numpy as np
import pandas as pd
from pypfopt import CLA, EfficientFrontier, expected_returns, plotting, risk_models
import matplotlib.pyplot as plt


def epf(df, static_dir="./static"):
    """Compute max-Sharpe allocations and save frontier plots.

    Returns (weights_dict, ef_perf, cla_perf) where perf tuples are
    (expected_return, volatility, sharpe). A single asset has no frontier
    to trace: weights are {asset: 1.0} and cla_perf == ef_perf.
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
    ef.max_sharpe()
    ef_perf = ef.portfolio_performance(verbose=False)

    if df.shape[1] == 1:
        asset = df.columns[0]
        weights = {asset: 1.0}
        cla_perf = ef_perf
        single = True
    else:
        cla = CLA(mu, s)
        cla.max_sharpe()
        cla_perf = cla.portfolio_performance(verbose=False)
        weights = cla.clean_weights()
        single = False

    # The pie uses the same weights dict that is returned + printed,
    # so plot and table can never disagree.
    plt.figure()
    pd.Series(weights).plot.pie(
        figsize=(5, 5), autopct=lambda p: f"{p:.2f}%"
    )
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(pie_path, dpi=200)
    plt.close()

    plt.figure()
    if single:
        plt.scatter([float(np.sqrt(s.loc[asset, asset]))], [float(mu.loc[asset])],
                    s=120, label=asset)
        plt.xlabel("Volatility")
        plt.ylabel("Expected return")
        plt.title("Single asset — no frontier to trace")
        plt.legend()
    else:
        plotting.plot_efficient_frontier(cla, show_assets=False)
    plt.tight_layout()
    plt.savefig(frontier_path, dpi=200)
    plt.close()

    return weights, ef_perf, cla_perf
