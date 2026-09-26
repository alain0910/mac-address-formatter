"""MAC Address Formatter: parse, validate, and reformat MAC addresses.

Exports:
    format_mac: function to reformat a MAC address
    parse_mac:  function to normalize a MAC address to raw uppercase hex
    is_valid:   function to check whether a string is a valid MAC address
    MacFormat:  enum of supported output formats
    MacError:   exception raised on invalid input (for format_mac and parse_mac)
"""

from .core import format_mac, parse_mac, is_valid, MacFormat, MacError

__all__ = ["format_mac", "parse_mac", "is_valid", "MacFormat", "MacError"]
