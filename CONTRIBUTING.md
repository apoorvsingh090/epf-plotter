# Contributing

Thanks for helping improve EPF Plotter.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export SECRET_KEY=anything-random-locally   # required: signs form CSRF tokens
python basic.py
```

Open http://127.0.0.1:5000.

## Notes for contributors

- NumPy floor is now >=2.5 (PyPortfolioOpt 1.6 fixed the NumPy 2 CLA crash that
  the old `<2` pin guarded against). If you touch the optimizer, re-run the
  3-asset CLA path on NumPy 2 to confirm.
- Plots are written to `static/` per request (known shared-file limitation;
  per-session filenames are a welcome contribution).
- This is an educational tool; do not add advice-like features (signals,
  "buy now", predictions).

## Pull requests

- Branch from `main`: `feature/<short-description>` or `fix/<short-description>`.
- Conventional commits (`feat:` / `fix:` / `docs:`), one logical change per commit.
- CI runs a compile check; keep modules import-clean and syntax-valid.

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
