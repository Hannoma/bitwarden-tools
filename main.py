#!/usr/bin/env python3
"""Bitwarden cleanup and Chrome merge utility

This module provides:
1. **Data‑class representations** (`BitwardenEntry`, `LoginData`, `UriEntry`) for
   type‑safe work with Bitwarden JSON.
2. CLI helpers to de‑duplicate a Bitwarden vault export and merge Google Chrome
   passwords while ensuring no duplicates are introduced.

Example usage::

    # Deduplicate Bitwarden export only
    python bw_cleanup.py vault_export.json -o cleaned.json

    # Deduplicate + merge Chrome passwords
    python bw_cleanup.py vault_export.json -c chrome_passwords.csv -o cleaned.json

The output (`cleaned.json`) keeps the canonical Bitwarden export structure so it
can be imported straight back into Bitwarden.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from tools.common_credentials import handle_common_credentials
from tools.deduplication import deduplicate_items
from wrapper.bitwarden import BitwardenWrapper
from wrapper.chrome import chrome_csv_to_items



def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Clean a Bitwarden JSON export and optionally merge Chrome passwords."
    )
    parser.add_argument("bitwarden_json", type=Path, help="Path to Bitwarden .json export")
    parser.add_argument(
        "-c",
        "--chrome-csv",
        type=Path,
        help="Path to Chrome passwords CSV export (optional)",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default="cleaned.json",
        required=True,
        help="Where to write the cleaned JSON"
    )

    args = parser.parse_args(argv)

    bitwarden = BitwardenWrapper()
    parsed_entries = bitwarden.load(args.bitwarden_json)

    parsed_items = deduplicate_items(parsed_entries)

    # 2. Optionally merge Chrome entries
    if args.chrome_csv:
        chrome_items = chrome_csv_to_items(args.chrome_csv)
        combined = deduplicate_items(parsed_items + chrome_items)
        parsed_items = combined

    # 3. Handle common credentials
    parsed_items = handle_common_credentials(parsed_items)

    bitwarden.save(args.output, parsed_items)

if __name__ == "__main__":  # pragma: no cover
    main()
