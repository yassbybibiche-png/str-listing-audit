"""Import listings from a CSV file (e.g. a channel-manager export).

Expected columns (header row required):
    id, title, title_en, description, guests, bedrooms,
    photos_count, photos_without_captions,
    amenities, safety, instant_book, cancellation, min_nights, cleaning_fee

- ``amenities`` and ``safety`` are semicolon-separated lists.
- ``photos_count`` / ``photos_without_captions`` expand into photo entries
  without room information, so room-based checks are skipped for CSV imports
  (evidence-only: what the CSV does not say stays UNVERIFIED).
"""
from __future__ import annotations

import csv
from pathlib import Path


def _split_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip().lower() for item in value.split(";") if item.strip()]


def _to_bool(value: str | None) -> bool | None:
    if value is None or value.strip() == "":
        return None
    return value.strip().lower() in ("true", "1", "yes", "y", "oui")


def _to_int(value: str | None) -> int | None:
    try:
        return int(value) if value not in (None, "") else None
    except ValueError:
        return None


def row_to_listing(row: dict) -> dict:
    photos_count = _to_int(row.get("photos_count")) or 0
    without_captions = _to_int(row.get("photos_without_captions")) or 0
    photos = [
        {
            "number": i + 1,
            "room": "",
            "caption": "" if i < without_captions else "caption provided in export",
        }
        for i in range(photos_count)
    ]

    settings: dict = {}
    instant = _to_bool(row.get("instant_book"))
    if instant is not None:
        settings["instant_book"] = instant
    if row.get("cancellation"):
        settings["cancellation"] = row["cancellation"].strip()
    min_nights = _to_int(row.get("min_nights"))
    if min_nights is not None:
        settings["min_nights"] = min_nights
    cleaning_fee = _to_int(row.get("cleaning_fee"))
    if cleaning_fee is not None:
        settings["cleaning_fee"] = cleaning_fee

    listing: dict = {
        "id": (row.get("id") or "UNVERIFIED").strip(),
        "title": (row.get("title") or "").strip(),
        "description": (row.get("description") or "").strip(),
        "photos": photos,
        "amenities": _split_list(row.get("amenities")),
        "safety": _split_list(row.get("safety")),
        "settings": settings,
    }
    if row.get("title_en"):
        listing["title_en"] = row["title_en"].strip()
    for key in ("guests", "bedrooms"):
        value = _to_int(row.get(key))
        if value is not None:
            listing[key] = value
    return listing


def load_csv(path: str | Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            return []
        return [row_to_listing(row) for row in reader if any((v or "").strip() for v in row.values())]
