"""Core audit logic.

Design principle (evidence-only): every finding cites the actual value
observed in the listing data. Fields that are absent are reported as
UNVERIFIED, never guessed or filled in.
"""
from __future__ import annotations

from dataclasses import dataclass, field

CRITICAL_AMENITIES = ["wifi", "kitchen"]
EXPECTED_AMENITIES = ["wifi", "kitchen", "washer", "heating", "air_conditioning", "workspace"]
SAFETY_EQUIPMENT = ["smoke_detector", "carbon_monoxide_detector", "fire_extinguisher"]

# Weights must sum to 100.
CATEGORY_WEIGHTS = {
    "title": 15,
    "description": 20,
    "photos": 25,
    "amenities_safety": 25,
    "settings": 15,
}


@dataclass
class Finding:
    category: str
    severity: str  # "error" | "warning" | "info"
    message: str
    evidence: str


@dataclass
class AuditResult:
    listing_id: str
    title: str
    findings: list[Finding] = field(default_factory=list)
    category_scores: dict[str, int] = field(default_factory=dict)

    @property
    def score(self) -> int:
        if not self.category_scores:
            return 0
        total = sum(CATEGORY_WEIGHTS[c] * s / 100 for c, s in self.category_scores.items())
        return round(total)

    def by_severity(self, severity: str) -> list[Finding]:
        return [f for f in self.findings if f.severity == severity]


def _penalised_score(findings: list[Finding]) -> int:
    score = 100
    for f in findings:
        if f.severity == "error":
            score -= 25
        elif f.severity == "warning":
            score -= 10
    return max(0, score)


def audit_listing(listing: dict) -> AuditResult:
    result = AuditResult(
        listing_id=str(listing.get("id", "UNVERIFIED")),
        title=str(listing.get("title", "UNVERIFIED")),
    )
    per_category: dict[str, list[Finding]] = {c: [] for c in CATEGORY_WEIGHTS}

    def add(category: str, severity: str, message: str, evidence) -> None:
        f = Finding(category, severity, message, str(evidence))
        result.findings.append(f)
        per_category[category].append(f)

    # --- Title ---------------------------------------------------------
    title = listing.get("title")
    if not title:
        add("title", "error", "Title is missing", "title=None")
    elif len(title) > 70:
        add("title", "warning", "Title is long and may be truncated in search results",
            f"title length={len(title)} chars")
    title_en = listing.get("title_en")
    if title_en is not None and len(title_en) > 50:
        add("title", "error", "English title exceeds 50 characters",
            f"title_en length={len(title_en)} chars")

    # --- Description ---------------------------------------------------
    desc = listing.get("description") or ""
    if not desc:
        add("description", "error", "Description is missing", "description=None")
    else:
        if desc.strip().count(".") <= 1 and len(desc) < 200:
            add("description", "error",
                "Description looks like a single sentence; guests cannot project themselves",
                f"description length={len(desc)} chars")
        elif len(desc) < 300:
            add("description", "warning", "Description is short (<300 characters)",
                f"description length={len(desc)} chars")

    # --- Photos --------------------------------------------------------
    photos = listing.get("photos") or []
    if len(photos) < 10:
        add("photos", "error", "Fewer than 10 photos", f"photos={len(photos)}")
    elif len(photos) < 20:
        add("photos", "warning", "Fewer than 20 photos; top listings usually show 20+",
            f"photos={len(photos)}")
    missing_captions = [p.get("number", "?") for p in photos if not (p.get("caption") or "").strip()]
    if missing_captions:
        add("photos", "warning", "Photos without captions (numbers as listed)",
            f"missing captions for photos n°{missing_captions}")
    first_five_rooms = {(p.get("room") or "").lower() for p in photos[:5]} - {""}
    if first_five_rooms and len(first_five_rooms) < 3:
        add("photos", "info",
            "First 5 photos show fewer than 3 different rooms; variety helps the cover sequence",
            f"first-5 rooms={sorted(first_five_rooms)}")

    # --- Amenities & safety --------------------------------------------
    amenities = {str(a).lower() for a in listing.get("amenities") or []}
    for a in CRITICAL_AMENITIES:
        if a not in amenities:
            add("amenities_safety", "error", f"Critical amenity not declared: {a}",
                f"amenities={sorted(amenities)}")
    for a in EXPECTED_AMENITIES:
        if a not in amenities:
            add("amenities_safety", "info", f"Amenity not declared (check if present but undeclared): {a}",
                f"amenities={sorted(amenities)}")
    safety = {str(s).lower() for s in listing.get("safety") or []}
    for s in SAFETY_EQUIPMENT:
        if s not in safety:
            sev = "error" if s in ("smoke_detector", "carbon_monoxide_detector") else "warning"
            add("amenities_safety", sev, f"Safety equipment not declared: {s}",
                f"safety={sorted(safety)}")

    # --- Settings --------------------------------------------------------
    settings = listing.get("settings") or {}
    if not settings:
        add("settings", "info", "Booking settings UNVERIFIED (not provided in input)", "settings={}")
    else:
        if settings.get("instant_book") is False:
            add("settings", "warning", "Instant Book is off; most competitors enable it",
                "instant_book=False")
        canc = str(settings.get("cancellation", "")).lower()
        if canc in ("strict", "ferme"):
            add("settings", "info",
                "Strict cancellation policy; compare with the competitor panel before keeping it",
                f"cancellation={canc}")

    for category, findings in per_category.items():
        result.category_scores[category] = _penalised_score(findings)
    return result
