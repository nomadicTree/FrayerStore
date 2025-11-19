import re
import unicodedata


def _to_ascii(s: str) -> str:
    """Normalize accented characters to ASCII equivalents."""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def slugify(s: str) -> str:
    """
    Convert a string into a URL-friendly slug.

    Behaviour:
    - Input must be a non-empty string, otherwise a ValueError or TypeError is raised.
    - Leading/trailing whitespace is stripped.
    - Accented Latin characters are normalised to their ASCII equivalents (NFKD).
      Examples: 'Café' → 'cafe', 'naïve' → 'naive', 'Gödel' → 'godel'.
    - All remaining non-alphanumeric characters are replaced with hyphens.
    - Multiple separators collapse into a single hyphen.
    - Hyphens at the start or end are removed.
    - The final slug is always lowercase ASCII.

    Notes:
    - Characters outside the Latin alphabet (e.g., Greek, Cyrillic, CJK) do not
      transliterate and are removed. Example: 'Δelta' → 'elta'.
    - This function is deterministic and suitable for generating stable URLs.

    Returns:
        str: The normalised slug.

    Raises:
        TypeError: If input is not a string.
        ValueError: If the input string is empty or contains only whitespace.
    """
    if not isinstance(s, str):
        raise TypeError("Slugify requires a string")
    if not s.strip():
        raise ValueError("Cannot slugify empty string")

    s = _to_ascii(s)
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")
