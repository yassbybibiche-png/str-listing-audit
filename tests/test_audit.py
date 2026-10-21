import json
from pathlib import Path

from str_listing_audit.audit import audit_listing
from str_listing_audit.report import to_markdown

EXAMPLES = Path(__file__).parent.parent / "examples"


def _load(name):
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def test_good_listing_scores_high():
    result = audit_listing(_load("example_listing.json"))
    assert result.score >= 80
    assert result.by_severity("error") == []


def test_poor_listing_scores_low_and_flags_safety():
    result = audit_listing(_load("example_listing_poor.json"))
    assert result.score < 70
    assert len(result.by_severity("error")) >= 5
    messages = " ".join(f.message for f in result.findings)
    assert "smoke_detector" in messages
    assert "wifi" in messages


def test_english_title_limit_is_50_chars():
    listing = _load("example_listing.json")
    listing["title_en"] = "x" * 51
    result = audit_listing(listing)
    assert any("50 characters" in f.message for f in result.findings)


def test_missing_fields_are_unverified_not_invented():
    result = audit_listing({"id": "empty-1"})
    md = to_markdown(result)
    assert "UNVERIFIED" in md or "missing" in md.lower()


def test_report_contains_evidence():
    result = audit_listing(_load("example_listing_poor.json"))
    md = to_markdown(result)
    assert "evidence:" in md
    assert "/100" in md
