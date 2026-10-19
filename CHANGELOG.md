# Changelog

All notable changes to EPF Plotter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
