# Changelog

All notable changes to EPF Plotter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Tests run under bare `pytest` again (repo-root `pytest.ini` with
  `pythonpath`), so CI's collection error is gone
- Unknown/delisted yfinance tickers fail loudly instead of being silently
  dropped from the optimisation; tickers capped at 30 per request, and
  total assets (tickers + CSV uploads) capped the same way
- CSVs with duplicated dates keep the last row per date instead of
  injecting spurious zero-return rows
- Single-asset Sharpe now uses the same risk-free rate as the CLA path
  (explicit `RISK_FREE_RATE = 0.0`; CLA's tangency solve hardcodes rf=0)
- Procfile bind fixed to `0.0.0.0:$PORT` (was an empty port)

### Changed

- Dependency floors raised via Dependabot group PR #1: Flask 3.1, pandas 3,
  NumPy 2 (PyPortfolioOpt 1.6 verified on NumPy 2 — CLA max-Sharpe + frontier
  plots), yfinance 1.7, and others; stale NumPy comment in `requirements.txt`
  updated to match.

### Added

- GitHub Actions CI
- CodeQL code scanning (Python)
- Community files: `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`,
  `CHANGELOG.md`
- Issue forms (bug report, feature request) and pull request template
- `dependabot.yml` (weekly grouped GitHub Actions + pip updates)
- README status badges and contributing/security sections
