"""Build a price DataFrame from yfinance tickers.

Returns a DataFrame indexed by Date with one column per ticker containing
daily Close prices. Downloads are cached in-process so repeated requests
(e.g. the same tickers re-queried) don't re-hit Yahoo.
"""
from functools import lru_cache

import pandas as pd
import yfinance as yf


def _parse_tickers(stocks):
    if stocks is None:
        return []
    if isinstance(stocks, str):
        # "AAPL, MSFT, RELIANCE.NS" -> ["AAPL", "MSFT", "RELIANCE.NS"]
        parts = [p.strip().upper() for p in stocks.replace(";", ",").split(",")]
        return _dedupe([p for p in parts if p])
    # list / tuple from older SelectMultipleField usage
    return _dedupe([str(s).strip().upper() for s in stocks if str(s).strip()])


def _dedupe(tickers):
    # "AAPL,AAPL" -> "AAPL" (preserve first-seen order); duplicates would
    # otherwise yield duplicate price columns and corrupt the optimisation.
    return list(dict.fromkeys(tickers))


@lru_cache(maxsize=32)
def _download(tickers, period, interval):
    return yf.download(
        list(tickers),
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
        threads=True,
    )


def make_dataframe(stocks, period="5y", interval="1d"):
    tickers = _parse_tickers(stocks)
    if not tickers:
        raise ValueError("No tickers provided.")

    data = _download(tuple(tickers), period, interval)
    if data is None or data.empty:
        raise ValueError(f"yfinance returned no data for: {', '.join(tickers)}")

    if isinstance(data.columns, pd.MultiIndex):
        # yfinance >=0.2 returns MultiIndex (Price x Ticker) even for 1 ticker
        level0 = list(data.columns.get_level_values(0).unique())
        price_level = "Close" if "Close" in level0 else ("Adj Close" if "Adj Close" in level0 else level0[0])
        df = data[price_level].copy()
        if isinstance(df, pd.Series):
            df = df.to_frame(tickers[0])
        # yfinance may return columns in any order; reindex to requested tickers
        df = df.reindex(columns=[t for t in tickers if t in df.columns])
    elif len(tickers) == 1:
        col = "Close" if "Close" in data.columns else data.columns[0]
        series = data[col]
        if isinstance(series, pd.DataFrame):
            series = series.iloc[:, 0]
        df = pd.DataFrame({tickers[0]: series})
    else:
        df = data.copy()

    if df.empty:
        raise ValueError(f"yfinance returned no price columns for: {', '.join(tickers)}")

    df.index = pd.to_datetime(df.index)
    # Drop tz to allow merging with naive CSV dates
    try:
        df.index = df.index.tz_localize(None)
    except Exception:
        pass
    df.index.name = "Date"
    df = df.sort_index()
    # pypfopt cannot handle NaNs -> keep only overlapping history
    df = df.dropna(how="any")
    if df.empty or len(df) < 2:
        raise ValueError("Not enough overlapping history after dropping NaNs.")
    return df
