# Contributing

Thanks for helping improve str-listing-audit!

## Ground rules

1. **Evidence-only.** Every new check must cite the observed value in its
   finding, and mark anything it cannot verify as `UNVERIFIED`.
   No invented amenities, no guessed metrics.
2. **No dependencies** in the core package (standard library only),
   so hosts can run it anywhere Python 3.10+ exists.
3. **Tests for every check.** Add or update a test in `tests/` for any
   behaviour change.

## Development

```bash
pip install -e .
pip install pytest
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m str_listing_audit.cli examples/example_listing.json
```

## Proposing a new check

Open an issue first and describe: the real listing problem it catches,
an example (anonymised) listing that triggers it, and the evidence the
finding will cite. Checks born from real audits are prioritised.
