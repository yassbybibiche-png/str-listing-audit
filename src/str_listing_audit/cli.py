"""Command-line interface.

Usage:
    python -m str_listing_audit.cli examples/example_listing.json
    python -m str_listing_audit.cli examples/example_listing.json --output report.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .audit import audit_listing
from .report import to_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="str-listing-audit",
        description="Audit a short-term rental listing from a JSON export (evidence-only).",
    )
    parser.add_argument("input", help="Path to the listing JSON file")
    parser.add_argument("--output", "-o", help="Write the Markdown report to this file")
    args = parser.parse_args(argv)

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    listings = data if isinstance(data, list) else [data]

    reports = []
    worst = 100
    for listing in listings:
        result = audit_listing(listing)
        worst = min(worst, result.score)
        reports.append(to_markdown(result))
        print(f"{result.listing_id}: {result.score}/100 "
              f"({len(result.by_severity('error'))} errors, "
              f"{len(result.by_severity('warning'))} warnings)")

    full = "\n\n".join(reports)
    if args.output:
        Path(args.output).write_text(full, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print("\n" + full)
    return 0 if worst >= 50 else 1


if __name__ == "__main__":
    sys.exit(main())
