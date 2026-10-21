"""Command-line interface.

Usage:
    python -m str_listing_audit.cli examples/example_listing.json
    python -m str_listing_audit.cli examples/example_listing.json --output report.md
    python -m str_listing_audit.cli examples/example_portfolio.csv
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .audit import audit_listing
from .csv_import import load_csv
from .portfolio import portfolio_markdown
from .report import to_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="str-listing-audit",
        description="Audit short-term rental listings from a JSON or CSV export (evidence-only).",
    )
    parser.add_argument("input", help="Path to the listing file (.json or .csv)")
    parser.add_argument("--output", "-o", help="Write the Markdown report to this file")
    args = parser.parse_args(argv)

    path = Path(args.input)
    if path.suffix.lower() == ".csv":
        listings = load_csv(path)
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
        listings = data if isinstance(data, list) else [data]

    results = []
    worst = 100
    for listing in listings:
        result = audit_listing(listing)
        results.append(result)
        worst = min(worst, result.score)
        print(f"{result.listing_id}: {result.score}/100 "
              f"({len(result.by_severity('error'))} errors, "
              f"{len(result.by_severity('warning'))} warnings)")

    reports = [to_markdown(r) for r in results]
    if len(results) > 1:
        reports.append(portfolio_markdown(results))
    full = "\n\n".join(reports)

    if args.output:
        Path(args.output).write_text(full, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print("\n" + full)
    return 0 if worst >= 50 else 1


if __name__ == "__main__":
    sys.exit(main())
