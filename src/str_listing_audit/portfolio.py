"""Portfolio view: rank every listing by score and prioritise the fixes."""
from __future__ import annotations

from .audit import AuditResult


def _top_priority(result: AuditResult) -> str:
    for severity in ("error", "warning"):
        items = result.by_severity(severity)
        if items:
            return items[0].message
    return "—"


def portfolio_markdown(results: list[AuditResult]) -> str:
    ranked = sorted(results, key=lambda r: (r.score, r.listing_id))
    lines = [
        "## Portfolio ranking (worst first)",
        "",
        "| # | Listing | Score | Errors | Warnings | Top priority |",
        "|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(ranked, start=1):
        lines.append(
            f"| {i} | {r.listing_id} | {r.score}/100 | {len(r.by_severity('error'))} "
            f"| {len(r.by_severity('warning'))} | {_top_priority(r)} |"
        )
    errors = [(r.listing_id, f.message) for r in ranked for f in r.by_severity("error")]
    lines += ["", "## Prioritised fix list (all errors, worst listings first)", ""]
    if not errors:
        lines.append("No errors across the portfolio.")
    for listing_id, message in errors:
        lines.append(f"- **{listing_id}** — {message}")
    lines.append("")
    return "\n".join(lines)
