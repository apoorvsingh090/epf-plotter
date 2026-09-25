import os

import pandas as pd
from flask import Flask, flash, render_template, request
from werkzeug.utils import secure_filename

from forms import dropdown
from make_dataframe import make_dataframe
from pypf import epf

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "5ecc8f8cfc9b7281c14faab192f57ca9"
)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB uploads

STATIC_DIR = os.path.join(app.root_path, "static")


def _parse_ticker_string(raw):
    if not raw:
        return []
    if isinstance(raw, (list, tuple)):
        return [str(s).strip().upper() for s in raw if str(s).strip()]
    parts = [p.strip().upper() for p in str(raw).replace(";", ",").split(",")]
    return [p for p in parts if p]


def _csv_to_series(file_storage):
    """Read an uploaded CSV (Date + Close) into a single-column DataFrame.

    Column is named after the sanitised filename stem so each upload
    becomes one asset. File is read in-memory; nothing is saved to disk.
    """
    filename = secure_filename(file_storage.filename or "")
    if not filename:
        raise ValueError("Empty upload filename.")
    stem, _ = os.path.splitext(filename)
    asset = stem.upper() or "UPLOAD"

    try:
        data = pd.read_csv(file_storage.stream, parse_dates=["Date"])
    except Exception:
        # Retry case-insensitive: some CSVs use 'date'/'close'
        file_storage.stream.seek(0)
        data = pd.read_csv(file_storage.stream)
        cols = {c.lower(): c for c in data.columns}
        if "date" not in cols:
            raise ValueError(f"{filename}: need a 'Date' column.")
        date_col = cols["date"]
        data = data.rename(columns={date_col: "Date"})
        data["Date"] = pd.to_datetime(data["Date"])

    cols_lower = {c.lower(): c for c in data.columns}
    if "close" in cols_lower:
        close_col = cols_lower["close"]
    elif "adj close" in cols_lower:
        close_col = cols_lower["adj close"]
    else:
        # Fall back to first numeric column
        numeric = data.select_dtypes(include="number").columns
        if len(numeric) == 0:
            raise ValueError(f"{filename}: need a 'Close' column.")
        close_col = numeric[0]

    out = pd.DataFrame({"Date": pd.to_datetime(data["Date"]), asset: data[close_col]})
    out = out.dropna().sort_values("Date")
    if out.empty:
        raise ValueError(f"{filename}: no valid rows.")
    # Deduplicate asset name if two files share a stem
    return out, asset


@app.route("/", methods=["GET", "POST"])
def hello():
    form = dropdown(request.form)
    if request.method == "POST":
        tickers = _parse_ticker_string(form.ticker.data)
        uploads = [f for f in request.files.getlist("upload") if f and f.filename]

        if not tickers and not uploads:
            flash("Enter yfinance tickers and/or upload CSVs.")
            return render_template("about.html", title="EPF", form=form)

        try:
            df = None
            if tickers:
                df = make_dataframe(tickers)

            for f in uploads:
                series_df, _asset = _csv_to_series(f)
                df = (
                    series_df
                    if df is None
                    else df.reset_index().merge(series_df, on="Date", how="outer")
                )
                if isinstance(df, pd.DataFrame) and "Date" in df.columns:
                    df["Date"] = pd.to_datetime(df["Date"])
                    df = df.sort_values("Date").set_index("Date")

            df.index = pd.to_datetime(df.index)
            try:
                df.index = df.index.tz_localize(None)
            except Exception:
                pass
            df = df.sort_index().dropna(how="any")
            if df.empty or len(df) < 2:
                raise ValueError("Not enough overlapping dates across tickers/CSVs.")

            weights, ef_perf, cla_perf = epf(df, static_dir=STATIC_DIR)
            return render_template(
                "results.html", data=weights, ef_perf=ef_perf, cla_perf=cla_perf
            )
        except Exception as exc:
            flash(f"Error: {exc}")
            return render_template("about.html", title="EPF", form=form), 400

    return render_template("about.html", title="EPF", form=form)


@app.route("/reference")
def reference():
    return render_template("dropdown.html")


if __name__ == "__main__":
    app.run(debug=True)
