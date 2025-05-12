from urllib.parse import urlparse, urlunparse


def _normalise_netloc(netloc: str) -> str:
    """Canonical *netloc* – lowercase, strip leading *www.* and default ports."""
    if netloc.startswith("www."):
        netloc = netloc[4:]
    if ":" in netloc:
        host, _, port = netloc.partition(":")
        if port in {"80", "443"}:
            netloc = host
    return netloc.lower()


def normalise_domain(uri: str) -> str:
    """Extract canonical domain from any URI (scheme ignored)."""
    try:
        p = urlparse(uri, "https")
    except ValueError:
        return uri.lower().strip()
    return _normalise_netloc(p.netloc or p.path.split("/")[0])


def shorten_uri(uri: str, max_len: int = 128) -> str:
    """Return a cleaned‑up URI with query params/fragments removed.

    * Always strips **query parameters** and **fragments**.
    * If the remaining URI still exceeds *max_len*, it collapses to just
      `scheme://domain` (no path).
    """
    p = urlparse(uri, "https")
    scheme = p.scheme
    netloc = _normalise_netloc(p.netloc or p.path.split("/")[0])
    path = p.path

    # First candidate without query/fragment
    candidate = urlunparse((scheme, netloc, path, "", "", ""))

    # If still too long, drop the path as well
    if len(candidate) > max_len:
        candidate = urlunparse((scheme, netloc, "", "", "", ""))

    return candidate