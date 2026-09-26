"""Core implementation for MAC address parsing and reformatting.

Design decisions (documented because they are not obvious):

1. We support IEEE 802 MAC-48 addresses only: exactly 12 hex digits (6 octets).
    We deliberately reject EUI-64 (16 hex digits) and any other width.
    The README states this clearly so callers know the boundary.

2. The parser is lenient about the delimiter: we accept colon, hyphen, and
    dot separators, and we accept raw hex with no separators. We do NOT accept
    mixed delimiters in a single string (e.g. "AA:BB-CC:DD:EE:FF") because
    that is almost always a typo, and accepting it would mask user errors.
    This is a deliberate, opinionated choice.

3. For dotted notation we support the four-octet form used by Cisco and some
    BSD tools: e.g. "ffff.ffff.ffff" (three groups of four hex digits).
    We do NOT support "ff.ff.ff.ff.ff.ff" (six groups of two) as dotted,
    because that is ambiguous with colon notation semantically and is not a
    common real-world notation. If you want six groups, use colons.

4. Output is always uppercase hex. Uppercase is the conventional canonical
    form in IEEE documentation and in most network tooling (e.g. `ip` output
    on Linux). Lowercase can be produced by the caller with `.lower()` if needed.
"""

from __future__ import annotations

import re
from enum import Enum


class MacError(ValueError):
    """Raised when a string cannot be parsed as a MAC-48 address."""


class MacFormat(Enum):
    """Supported output formats for ``format_mac``.

    Members:
        COLON:  ``aa:bb:cc:dd:ee:ff``
        HYPHEN: ``aa-bb-cc-dd-ee-ff``
        DOT:    ``aabb.ccdd.eeff`` (Cisco-style four-digit grouping)
        RAW:    ``aabbccddeeff`` (no separators, uppercase)
    """

    COLON = "colon"
    HYPHEN = "hyphen"
    DOT = "dot"
    RAW = "raw"


# Precompiled patterns. Each pattern is anchored so partial matches are rejected.
# Using explicit character classes [0-9a-fA-F] rather than \h or re.IGNORECASE
# keeps the matching explicit and avoids any locale/unicode surprises.
_HEX = r"[0-9a-fA-F]"

_COLON_RE = re.compile(rf"^(?:{_HEX}{{2}}:){{5}}{_HEX}{{2}}$")
_HYPHEN_RE = re.compile(rf"^(?:{_HEX}{{2}}-){{5}}{_HEX}{{2}}$")
_DOT_RE = re.compile(rf"^(?:{_HEX}{{4}}\.){{2}}{_HEX}{{4}}$")
_RAW_RE = re.compile(rf"^{_HEX}{{12}}$")


def _clean(s: str) -> str:
    """Strip surrounding whitespace.

    We strip only leading/trailing whitespace, not internal whitespace, because
    internal whitespace in a MAC is always a user error and should be rejected
    rather than silently fixed.
    """
    return s.strip()


def parse_mac(value: str) -> str:
    """Parse a MAC-48 address and return normalized raw uppercase hex.

    Accepted input forms (delimiter must be consistent within the string):
        - ``aa:bb:cc:dd:ee:ff``  (colon, six groups of two)
        - ``aa-bb-cc-dd-ee-ff``  (hyphen, six groups of two)
        - ``aabb.ccdd.eeff``    (dot, three groups of four — Cisco style)
        - ``aabbccddeeff``       (raw, twelve hex digits)

    Returns:
        Twelve uppercase hex characters with no separators, e.g. ``"AABBCCDDEEFF"``.

    Raises:
        MacError: If the input is not a string, is empty, or does not match one
            of the accepted forms.
    """
    if not isinstance(value, str):
        raise MacError(f"expected str, got {type(value).__name__}")

    s = _clean(value)
    if not s:
        raise MacError("empty MAC address")

    # Reject mixed delimiters: if more than one delimiter type appears, it is a typo.
    # We check this before matching the strict patterns so the error message is clear.
    has_colon = ":" in s
    has_hyphen = "-" in s
    has_dot = "." in s
    if sum([has_colon, has_hyphen, has_dot]) > 1:
        raise MacError(f"mixed delimiters in MAC address: {value!r}")

    if _COLON_RE.match(s) or _HYPHEN_RE.match(s):
        raw = s.replace(":", "").replace("-", "")
    elif _DOT_RE.match(s):
        raw = s.replace(".", "")
    elif _RAW_RE.match(s):
        raw = s
    else:
        raise MacError(f"not a valid MAC-48 address: {value!r}")

    return raw.upper()


def is_valid(value: str) -> bool:
    """Return True if ``value`` is a parseable MAC-48 address, False otherwise.

    This is a convenience wrapper around ``parse_mac`` that swallows ``MacError``.
    It accepts any object (non-strings return False) so it is safe to call on
    untrusted input without a type check.
    """
    try:
        parse_mac(value)
    except MacError:
        return False
    return True


def format_mac(value: str, fmt: MacFormat = MacFormat.COLON) -> str:
    """Reformat a MAC-48 address into the chosen notation.

    Args:
        value: A MAC-48 address in any accepted input form (see ``parse_mac``).
        fmt:   Target format. Defaults to ``MacFormat.COLON``.

    Returns:
        The MAC address formatted according to ``fmt``, using uppercase hex.

    Raises:
        MacError: If ``value`` cannot be parsed as a MAC-48 address.
        TypeError: If ``fmt`` is not a ``MacFormat``.
    """
    if not isinstance(fmt, MacFormat):
        raise TypeError(f"fmt must be a MacFormat, got {type(fmt).__name__}")

    raw = parse_mac(value)

    if fmt is MacFormat.RAW:
        return raw
    if fmt is MacFormat.COLON:
        return ":".join(raw[i : i + 2] for i in range(0, 12, 2))
    if fmt is MacFormat.HYPHEN:
        return "-".join(raw[i : i + 2] for i in range(0, 12, 2))
    if fmt is MacFormat.DOT:
        # Cisco-style: group into three four-digit chunks.
        return ".".join(raw[i : i + 4] for i in range(0, 12, 4))

    # Unreachable: Enum exhausts the four members above.
    raise MacError(f"unsupported format: {fmt!r}")
