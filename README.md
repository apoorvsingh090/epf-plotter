# EPF Plotter

Pick stocks, get the **max-Sharpe portfolio**: weights, expected return, volatility, and the efficient frontier — as a pie chart and a frontier plot.

**Live demo:** https://epf-plotter.onrender.com/ *(free tier — first load can take ~a minute while it wakes up)*

## What it does

1. You enter **yfinance tickers** (e.g. `AAPL, MSFT, RELIANCE.NS`) and/or **upload CSVs** with `Date` + `Close` columns — each upload becomes one asset. The two inputs can be mixed.
2. The app pulls 5 years of daily closes, aligns them to overlapping dates, and runs mean-variance optimization.
3. The results page shows **% allocation per asset**, annualised return / volatility / Sharpe, plus two plots: allocation pie and efficient frontier.

## How it works

| Step | Detail |
|---|---|
| Prices | `yfinance.download(..., period="5y", interval="1d")`, Close prices, NaNs dropped to overlapping history |
| Expected returns | Mean historical return (`pypfopt.expected_returns`) |
| Risk model | Ledoit-Wolf covariance shrinkage (`pypfopt.risk_models`) |
| Optimizer | Max Sharpe via `EfficientFrontier`; frontier curve via `CLA` |
| Output | `cla.clean_weights()` allocations; the headline return/vol/Sharpe are the **average of the EF and CLA estimates** |

Stack: Flask + Flask-WTF forms, pandas, PyPortfolioOpt, matplotlib (Agg backend), gunicorn. Uploads are parsed in memory (16 MB cap) — nothing is saved except the two rendered plots.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:SECRET_KEY = "anything-random-locally"   # needed for form CSRF
python basic.py
```

Open http://127.0.0.1:5000. Production runs `gunicorn basic:app` (see `Procfile` / `render.yaml`).

## CSV format

```csv
Date,Close
2023-01-02,184.40
2023-01-03,186.12
...
```

`Date` is parsed flexibly (case-insensitive); the price column falls back from `Close` → `Adj Close` → first numeric column. The asset is named after the uploaded filename.

## Repo layout

```
basic.py           # Flask app: form → dataframe → optimize → results page
forms.py           # ticker text field + multi-file upload (WTForms)
make_dataframe.py  # yfinance tickers → Date-indexed Close-price DataFrame
pypf.py            # epf(): max-Sharpe weights + pie/frontier PNGs into static/
templates/         # about (input), results (allocations + plots), dropdown (ticker help)
static/            # rendered plt.png (pie) + plt2.png (frontier), overwritten per request
render.yaml / Procfile / requirements.txt / .python-version   # Render deploy config
```

## Limitations (honest ones)

- **Past returns don't predict future returns.** Max-Sharpe on historical means often concentrates hard (a synthetic test put 100% in one asset) — treat output as a starting point, not advice.
- `static/plt.png` and `plt2.png` are **overwritten on every request**, so concurrent users can see each other's plots. Fine for a demo; per-session filenames would fix it.
- yfinance rate-limits aggressive use; obscure tickers (especially non-US without the right suffix like `.NS`) return no data and the app reports it as an error.
- This is an educational project, not financial advice.
