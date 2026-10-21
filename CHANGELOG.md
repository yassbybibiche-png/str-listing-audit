# Changelog

## 0.2.0 — 2026-10-21

- CSV importer: audit a whole channel-manager export (see `examples/example_portfolio.csv` for the expected columns).
- Portfolio mode: when several listings are audited together, the report now ends with a ranking (worst first) and a prioritised fix list of every error.
- Demo: a generated portfolio report is committed at `docs/demo-portfolio-report.md`.
- Photo room-diversity check is now skipped when room data is absent (e.g. CSV imports) instead of guessing.

## 0.1.0 — 2026-10-21

- First public release.
- Evidence-only audit engine: title, description, photos, amenities & safety, booking settings.
- Weighted score out of 100, per-category scores, Markdown report.
- CLI with portfolio mode (single listing or list of listings in one JSON file).
- Two bundled examples: a complete listing (100/100) and a poor listing (58/100).
- Test suite and GitHub Actions CI (Python 3.10–3.12).
