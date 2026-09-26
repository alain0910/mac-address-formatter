# MAC Address Formatter

Parse, validate, and reformat MAC-48 addresses between colon, hyphen, dot (Cisco), and raw hex notations. Standard library only, no dependencies.

```python
from mac_address_formatter import format_mac, parse_mac, is_valid, MacFormat, MacError

print(format_mac("aa:bb:cc:dd:ee:ff", MacFormat.DOT))   # AABB.CCDD.EEFF
print(format_mac("aabb.ccdd.eeff", MacFormat.HYPHEN))    # AA-BB-CC-DD-EE-FF
print(parse_mac("AA-BB-CC-DD-EE-FF"))                    # AABBCCDDEEFF
print(is_valid("aabbccddeeff"))                          # True
print(is_valid("not a mac"))                             # False

try:
    format_mac("gg:bb:cc:dd:ee:ff")
except MacError as e:
    print(e)  # not a valid MAC-48 address: 'gg:bb:cc:dd:ee:ff'
```

## Why this exists

Network tooling produces and consumes MAC addresses in several incompatible notations: Linux `ip` uses colons, Cisco IOS uses dotted four-digit groups, and configuration files often store raw hex. Converting between these by hand is trivial but error-prone — a misplaced separator silently corrupts the address. This library does one job: parse any common form, validate it, and emit the form you need.

The trade-off: we support MAC-48 only (12 hex digits). EUI-64 and other widths are rejected. If you need EUI-64, this is the wrong library.

## Edge cases you will hit

- **Mixed delimiters** (`aa:bb-cc:dd:ee:ff`) are rejected, not silently fixed. This is deliberate; a mixed-delimiter MAC is almost always a typo.
- **Dotted notation** means the Cisco three-group form (`aabb.ccdd.eeff`), not six dotted pairs. If you want six pairs, use colons.
- Output is always **uppercase**, the IEEE canonical form. Call `.lower()` on the result if you need lowercase.
- Input may have surrounding whitespace; internal whitespace is rejected.

## API

| Name | Description |
|------|-------------|
| `format_mac(value, fmt=MacFormat.COLON) -> str` | Reformat a MAC into the chosen notation. Raises `MacError` on bad input, `TypeError` if `fmt` is not a `MacFormat`. |
| `parse_mac(value) -> str` | Return 12 uppercase hex digits. Raises `MacError` on bad input. |
| `is_valid(value) -> bool` | Safe predicate; returns `False` for any non-string or unparseable input. |
| `MacFormat` | Enum: `COLON`, `HYPHEN`, `DOT`, `RAW`. |
| `MacError` | Subclass of `ValueError`, raised on parse failures. |

## Running the tests

```
PYTHONPATH=src python -m unittest discover -s tests
```
