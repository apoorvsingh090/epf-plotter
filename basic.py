import os
import logging

import pandas as pd
from flask import Flask, flash, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename

from forms import dropdown
from make_dataframe import make_dataframe, _parse_tickers
from pypf import epf

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
_secret = os.environ.get("SECRET_KEY")
if not _secret:
    raise RuntimeError(
        "SECRET_KEY env var is required (it signs form CSRF tokens). "
        'Set it locally, e.g. $env:SECRET_KEY = "anything-random-locally"; '
        "Render generates one via render.yaml. Refusing to start with a "
        "public fallback key."
    )
app.config["SECRET_KEY"] = _secret
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB uploads
app.config["SESSION_COOKIE_SECURE"] = True

STATIC_DIR = os.path.join(app.root_path, "static")

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)


def _unique_stem(stem, taken):
    """Make an asset column name unique against already-used names."""
    candidate = stem or "UPLOAD"
    if candidate not in taken:
        return candidate
    i = 2
    while f"{candidate}-{i}" in taken:
        i += 1
    return f"{candidate}-{i}"


def _csv_to_series(file_storage, taken):
    """Read an uploaded CSV (Date + Close) into a single-column DataFrame.

    Column is named after the sanitised filename stem so each upload
    becomes one asset. File is read in-memory; nothing is saved to disk.
    The asset name is de-duplicated against names already in play.
    """
    filename = secure_filename(file_storage.filename or "")
    if not filename:
        raise ValueError("Empty upload filename.")
    stem, _ = os.path.splitext(filename)
    asset = _unique_stem(stem.upper(), taken)
    taken.add(asset)

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
    return out, asset


@app.route("/", methods=["GET", "POST"])
@limiter.limit("20 per minute")
def hello():
    form = dropdown(request.form)
    if request.method == "POST":
        tickers = _parse_tickers(form.ticker.data)
        uploads = [f for f in request.files.getlist("upload") if f and f.filename]

        if not tickers and not uploads:
            flash("Enter yfinance tickers and/or upload CSVs.")
            return render_template("about.html", title="EPF", form=form)

        try:
            df = None
            if tickers:
                df = make_dataframe(tickers)

            taken = set(tickers)
            for f in uploads:
                series_df, _asset = _csv_to_series(f, taken)
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

            weights, cla_perf, pie_name, frontier_name = epf(df, static_dir=STATIC_DIR)
            return render_template(
                "results.html", data=weights,
                cla_perf=cla_perf, pie_name=pie_name, frontier_name=frontier_name,
            )
        except Exception:
            app.logger.exception("EPF request failed")
            flash("That didn't compute. Check the CSVs/tickers and try again.")
            return render_template("about.html", title="EPF", form=form), 400

    return render_template("about.html", title="EPF", form=form)


@app.route("/reference")
def reference():
    return render_template("dropdown.html")


if __name__ == "__main__":
    # Production (gunicorn, see Procfile/render.yaml) imports `app` without
    # running this block. The debugger stays off unless explicitly enabled.
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
