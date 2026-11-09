"""EPF calculation: max-Sharpe allocations + frontier plots.

Plots are written with per-request UUID names (never a shared file), so two
simultaneous requests can never show each other's chart. Files older than a
day are cleaned up opportunistically on each write.
"""
import matplotlib

matplotlib.use("Agg")  # headless: must be set before pyplot import

import os
import time
import uuid

import numpy as np
import pandas as pd
from pypfopt import CLA, expected_returns, plotting, risk_models
import matplotlib.pyplot as plt

# Keep at most ~2 days of chart artifacts; the folder is git-ignored.
PLOT_TTL_SECONDS = 2 * 86400


def _plot_path(static_dir, prefix):
    return os.path.join(static_dir, f"{prefix}_{uuid.uuid4().hex[:12]}.png")


def _cleanup_old_plots(static_dir):
    try:
        cutoff = time.time() - PLOT_TTL_SECONDS
        for name in os.listdir(static_dir):
            if (name.startswith("pie_") or name.startswith("frontier_")) and name.endswith(".png"):
                try:
                    if os.path.getmtime(os.path.join(static_dir, name)) < cutoff:
                        os.remove(os.path.join(static_dir, name))
                except OSError:
                    pass
    except OSError:
        pass


def epf(df, static_dir="./static"):
    """Compute max-Sharpe allocations and save frontier plots.

    Returns (weights_dict, cla_perf, pie_name, frontier_name) where perf is
    (expected_return, volatility, sharpe). A single asset has no frontier to
    trace: weights are {asset: 1.0}.
    """
    if df is None or df.empty:
        raise ValueError("Empty price DataFrame.")
    df = df.sort_index().dropna(how="any")
    if df.shape[1] < 1 or len(df) < 2:
        raise ValueError("Need at least 1 asset and 2 overlapping price rows.")

    os.makedirs(static_dir, exist_ok=True)
    _cleanup_old_plots(static_dir)
    pie_name = f"pie_{uuid.uuid4().hex[:12]}.png"
    frontier_name = f"frontier_{uuid.uuid4().hex[:12]}.png"
    pie_path = os.path.join(static_dir, pie_name)
    frontier_path = os.path.join(static_dir, frontier_name)

    mu = expected_returns.mean_historical_return(df)
    s = risk_models.CovarianceShrinkage(df).ledoit_wolf()

    if df.shape[1] == 1:
        asset = df.columns[0]
        mu_a, var_a = float(mu.loc[asset]), float(s.loc[asset, asset])
        sharpe = mu_a / (var_a ** 0.5) if var_a > 0 else 0.0
        cla_perf = (mu_a, var_a ** 0.5, sharpe)
        weights = {asset: 1.0}
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

    return weights, cla_perf, pie_name, frontier_name
