# str-listing-audit

**Evidence-based audit toolkit for short-term rental listings** (Airbnb, Booking.com, Vrbo).

Built by a professional property manager running ~30 listings, from the audit
method actually used in production — not from theory.

Most listing "checkers" give generic advice. This one gives a **score and
findings backed by evidence**: every problem cites the actual value observed
in your listing data, and anything missing is marked `UNVERIFIED` — never
guessed, never invented.

## What it checks

| Category | Weight | Examples |
|---|---|---|
| Title | 15 | Length, English title ≤ 50 characters |
| Description | 20 | One-sentence descriptions, too-short copy |
| Photos | 25 | Count (<10 / <20), missing captions, variety in the first 5 |
| Amenities & safety | 25 | WiFi, kitchen, smoke / CO detectors, fire extinguisher, present-but-undeclared amenities |
| Booking settings | 15 | Instant Book off, strict cancellation vs. competitors |

## Quick start

No dependencies — Python 3.10+ only.

```bash
git clone https://github.com/yassbybibiche-png/str-listing-audit.git
cd str-listing-audit
PYTHONPATH=src python -m str_listing_audit.cli examples/example_listing.json
PYTHONPATH=src python -m str_listing_audit.cli examples/example_listing_poor.json --output report.md
```

Or install it:

```bash
pip install -e .
str-listing-audit examples/example_listing.json
```

## Input format

A JSON export of a listing (a single object, or a list for a whole portfolio):

```json
{
  "id": "my-listing-1",
  "title": "Bright flat · King bed · Fast WiFi",
  "title_en": "Bright flat · King bed · Fast WiFi",
  "description": "…at least a few real sentences…",
  "guests": 4, "bedrooms": 1,
  "photos": [{"number": 1, "room": "living_room", "caption": "Living room with balcony"}],
  "amenities": ["wifi", "kitchen", "washer"],
  "safety": ["smoke_detector", "carbon_monoxide_detector"],
  "settings": {"instant_book": true, "cancellation": "flexible", "min_nights": 2}
}
```

See `examples/` for a complete good example (100/100) and a poor one (58/100).

## Sample output

```text
example-poor-002: 58/100 (6 errors, 4 warnings)
- ❌ [amenities_safety] Critical amenity not declared: wifi — evidence: `amenities=['kitchen']`
- ❌ [amenities_safety] Safety equipment not declared: smoke_detector — evidence: `safety=[]`
- ⚠️ [photos] Photos without captions (numbers as listed) — evidence: `missing captions for photos n°[1, 2, 4, 5]`
```

## Why this project exists

Cleanliness complaints, missing safety declarations and one-sentence
descriptions are the top recurring problems found when auditing real
portfolios. This tool turns that recurring manual audit into a repeatable,
shareable check — for independent hosts and concierge services alike.

## Roadmap

- [ ] CSV / channel-manager export importers (SuperHote, Lodgify, Hostaway)
- [ ] Competitor panel comparison (median price, cancellation, fees)
- [ ] Photo-caption fidelity helper (captions must describe only what is visible)
- [ ] Portfolio mode: rank all listings by score, export a prioritised fix list
- [ ] French rule pack (registration number, Paris-specific requirements)

See [docs/ROADMAP.md](docs/ROADMAP.md).

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
New checks must follow the evidence-only rule: cite the observed value,
mark the unverifiable as `UNVERIFIED`.

## License

MIT — see [LICENSE](LICENSE).
