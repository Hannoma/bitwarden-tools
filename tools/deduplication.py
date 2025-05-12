from typing import Generator, Any

from data.bitwarden import BitwardenEntry
from utils.logger import logger
from utils.url import normalise_domain, shorten_uri


def iter_login_keys(item: BitwardenEntry) -> Generator[tuple[str, str, str], Any, None]:
    """Yield (domain, username, password) tuples for every URI in a BW item."""
    login = item.login
    for uri_entry in login.uris:
        if uri_entry.uri:
            yield normalise_domain(uri_entry.uri), login.username, login.password


def deduplicate_items(items: list[BitwardenEntry]) -> list[BitwardenEntry]:
    """Merge duplicates inside a Bitwarden *items* list (dict‑based)."""
    seen: dict[tuple[str, str, str], BitwardenEntry] = {}
    result: list[BitwardenEntry] = []

    for item in items:
        login = item.type == 1
        if not login:  # secure notes / cards etc – keep as‑is
            result.append(item)
            continue

        # Remember whether we've merged this item into an existing one
        merged_into_existing = False
        for key in iter_login_keys(item):
            if key in seen:
                # Duplicate: merge extra URIs into the original item
                seen[key].merge(item)
                merged_into_existing = True
                break

        if merged_into_existing:
            continue

        # Not a duplicate: normalize its URIs, add to results and mark seen
        for uri_obj in item.login.uris:
            uri_obj.uri = shorten_uri(uri_obj.uri)
        result.append(item)
        for key in iter_login_keys(item):
            seen[key] = item

    logger.info(f"Found {len(seen)} unique items in {len(items)} total items")

    return result