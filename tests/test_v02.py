from pathlib import Path

from str_listing_audit.audit import audit_listing
from str_listing_audit.csv_import import load_csv, row_to_listing
from str_listing_audit.portfolio import portfolio_markdown

EXAMPLES = Path(__file__).parent.parent / "examples"


def test_csv_import_builds_listings():
    listings = load_csv(EXAMPLES / "example_portfolio.csv")
    assert len(listings) == 3
    family = next(l for l in listings if l["id"] == "family-flat")
    assert len(family["photos"]) == 24
    assert "wifi" in family["amenities"]
    assert family["settings"]["instant_book"] is True


def test_csv_import_flags_missing_safety():
    listings = load_csv(EXAMPLES / "example_portfolio.csv")
    old = next(l for l in listings if l["id"] == "old-listing")
    result = audit_listing(old)
    assert any("smoke_detector" in f.message for f in result.findings)


def test_csv_rows_skip_room_diversity_check():
    row = {
        "id": "x1", "title": "T", "description": "A real description with several sentences. " * 5,
        "photos_count": "12", "photos_without_captions": "0",
        "amenities": "wifi;kitchen", "safety": "smoke_detector;carbon_monoxide_detector",
    }
    result = audit_listing(row_to_listing(row))
    assert not any("First 5 photos" in f.message for f in result.findings)


def test_portfolio_ranking_worst_first():
    listings = load_csv(EXAMPLES / "example_portfolio.csv")
    results = [audit_listing(l) for l in listings]
    md = portfolio_markdown(results)
    assert "Portfolio ranking" in md
    assert md.index("old-listing") < md.index("family-flat")
    assert "Prioritised fix list" in md
