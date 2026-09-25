"""Build a price DataFrame from yfinance tickers.

Replaces the old MongoDB/investpy lookup. Returns a DataFrame indexed
by Date with one column per ticker containing daily Close prices.
"""
import pandas as pd
import yfinance as yf


def _parse_tickers(stocks):
    if stocks is None:
        return []
    if isinstance(stocks, str):
        # "AAPL, MSFT, RELIANCE.NS" -> ["AAPL", "MSFT", "RELIANCE.NS"]
        parts = [p.strip().upper() for p in stocks.replace(";", ",").split(",")]
        return [p for p in parts if p]
    # list / tuple from older SelectMultipleField usage
    return [str(s).strip().upper() for s in stocks if str(s).strip()]


def make_dataframe(stocks, period="5y", interval="1d"):
    tickers = _parse_tickers(stocks)
    if not tickers:
        raise ValueError("No tickers provided.")

    # yfinance handles single ticker and multi-ticker differently,
    # so normalise both to a {ticker: Close series} frame.
    data = yf.download(
        tickers,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
        threads=True,
    )
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
