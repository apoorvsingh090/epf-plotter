"""Tests for EPF-plotter. No network: yfinance is mocked with fixtures."""
import io
import os

import numpy as np
import pandas as pd
import pytest

os.environ.setdefault("SECRET_KEY", "test-secret")

import make_dataframe
import pypf
import basic


# ---------- fixture frames ----------

def _fixture_close(seed=7, days=600, tickers=("AAA", "BBB")):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2022-01-03", periods=days, freq="B")
    data = {}
    for t in tickers:
        returns = rng.normal(0.0005, 0.02, days)
        data[t] = 100 * np.cumprod(1 + returns)
    return pd.DataFrame(data, index=idx)


def _fixture_multiindex_download(tickers=("AAA", "BBB"), days=300):
    close = _fixture_close(tickers=tickers, days=days)
    return pd.concat([close, close * 1.01], axis=1, keys=["Close", "High"])


# ---------- make_dataframe._parse_tickers ----------

def test_parse_tickers_csv_string():
    assert make_dataframe._parse_tickers("AAPL, MSFT;RELIANCE.NS") == ["AAPL", "MSFT", "RELIANCE.NS"]
    assert make_dataframe._parse_tickers("aapl,AAPL") == ["AAPL"]  # dedupe, keep order


def test_parse_tickers_list_and_none():
    assert make_dataframe._parse_tickers(["a", " b ", "A"]) == ["A", "B"]
    assert make_dataframe._parse_tickers(None) == []
    assert make_dataframe._parse_tickers("") == []


# ---------- make_dataframe ----------

def _mock_download(df_or_none, monkeypatch, tickers=2):
    monkeypatch.setattr(make_dataframe.yf, "download", lambda *a, **k: df_or_none)
    make_dataframe._download.cache_clear()


def test_make_dataframe_multi_ticker(monkeypatch):
    _mock_download(_fixture_multiindex_download(), monkeypatch)
    df = make_dataframe.make_dataframe("AAA,BBB")
    assert list(df.columns) == ["AAA", "BBB"]
    assert len(df) > 100
    assert df.index.name == "Date"


def test_make_dataframe_single_ticker(monkeypatch):
    close = _fixture_close(tickers=("AAA",))["AAA"]
    single = pd.DataFrame({"Close": close}, index=close.index)
    monkeypatch.setattr(make_dataframe.yf, "download", lambda *a, **k: single)
    make_dataframe._download.cache_clear()
    df = make_dataframe.make_dataframe("AAA")
    assert list(df.columns) == ["AAA"]


def test_make_dataframe_no_data(monkeypatch):
    _mock_download(None, monkeypatch)
    with pytest.raises(ValueError, match="no data"):
        make_dataframe.make_dataframe("ZZZ")


# ---------- _csv_to_series ----------

class _FakeFile:
    def __init__(self, name, content):
        self.filename = name
        self.stream = io.BytesIO(content.encode() if isinstance(content, str) else content)


def test_csv_to_series_happy_path():
    csv_text = "Date,Close\n2026-01-01,100\n2026-01-02,101\n2026-01-03,102\n"
    out, asset = basic._csv_to_series(_FakeFile("myasset.csv", csv_text), set())
    assert asset == "MYASSET"
    assert list(out.columns) == ["Date", asset]
    assert len(out) == 3


def test_csv_to_series_duplicate_stems():
    csv_text = "Date,Close\n2026-01-01,100\n2026-01-02,101\n"
    taken = {"MYASSET"}
    out, asset = basic._csv_to_series(_FakeFile("myasset.csv", csv_text), taken)
    assert asset == "MYASSET-2"


def test_csv_to_series_missing_date_raises():
    with pytest.raises(ValueError, match="Date"):
        basic._csv_to_series(_FakeFile("bad.csv", "foo,bar\n1,2\n"), set())


# ---------- pypf.epf ----------

def test_epf_two_assets_weights_and_plots(tmp_path):
    df = _fixture_close(days=400)
    weights, cla_perf, pie_name, frontier_name = pypf.epf(df, static_dir=str(tmp_path))
    assert abs(sum(weights.values()) - 1.0) < 1e-6
    assert len(cla_perf) == 3
    assert (tmp_path / pie_name).stat().st_size > 0
    assert (tmp_path / frontier_name).stat().st_size > 0
    assert pie_name != frontier_name


def test_epf_single_asset(tmp_path):
    df = _fixture_close(tickers=("AAA",), days=200)
    weights, cla_perf, pie_name, frontier_name = pypf.epf(df, static_dir=str(tmp_path))
    assert weights == {"AAA": 1.0}
    assert np.isfinite(list(cla_perf)).all()


# ---------- flask smoke ----------

@pytest.fixture
def client(tmp_path):
    basic.app.config["TESTING"] = True
    basic.app.config["SECRET_KEY"] = "test"
    basic.STATIC_DIR = str(tmp_path / "static")
    basic.epf = pypf.epf
    with basic.app.test_client() as c:
        yield c


def test_get_root_renders_200(client):
    r = client.get("/")
    assert r.status_code == 200


def test_post_with_tickers_mocked(client, monkeypatch, tmp_path):
    df = _fixture_close(days=500)

    def fake_make_dataframe(tickers, period="5y", interval="1d"):
        return df.copy()

    monkeypatch.setattr(basic, "make_dataframe", fake_make_dataframe)
    r = client.post("/", data={"ticker": "AAA,BBB"}, content_type="multipart/form-data")
    assert r.status_code == 200
    assert b"Sharpe" in r.data


def test_post_empty_shows_flash(client):
    r = client.post("/", data={"ticker": ""}, content_type="multipart/form-data")
    assert r.status_code == 200
    assert b"Enter yfinance tickers" in r.data
