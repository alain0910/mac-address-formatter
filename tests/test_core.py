"""Tests for the MAC address formatter core.

Covers the happy path for every input/output form, plus the edge cases that
the implementation explicitly handles: mixed delimiters, wrong width,
non-hex characters, non-string input, and unknown format.
"""

import unittest

from mac_address_formatter import format_mac, parse_mac, is_valid, MacFormat, MacError


class TestParseMac(unittest.TestCase):
    def test_parses_colon_form(self):
        self.assertEqual(parse_mac("aa:bb:cc:dd:ee:ff"), "AABBCCDDEEFF")

    def test_parses_hyphen_form(self):
        self.assertEqual(parse_mac("aa-bb-cc-dd-ee-ff"), "AABBCCDDEEFF")

    def test_parses_dot_form_cisco(self):
        self.assertEqual(parse_mac("aabb.ccdd.eeff"), "AABBCCDDEEFF")

    def test_parses_raw_form(self):
        self.assertEqual(parse_mac("aabbccddeeff"), "AABBCCDDEEFF")

    def test_uppercase_input_is_accepted(self):
        self.assertEqual(parse_mac("AA:BB:CC:DD:EE:FF"), "AABBCCDDEEFF")

    def test_mixed_case_input_is_accepted(self):
        self.assertEqual(parse_mac("Aa:Bb:cC:dD:Ee:fF"), "AABBCCDDEEFF")

    def test_whitespace_is_stripped(self):
        self.assertEqual(parse_mac("  aa:bb:cc:dd:ee:ff  "), "AABBCCDDEEFF")

    def test_mixed_delimiters_rejected(self):
        with self.assertRaises(MacError):
            parse_mac("aa:bb-cc:dd:ee:ff")

    def test_too_short_rejected(self):
        with self.assertRaises(MacError):
            parse_mac("aa:bb:cc:dd:ee")

    def test_too_long_rejected(self):
        with self.assertRaises(MacError):
            parse_mac("aa:bb:cc:dd:ee:ff:11")

    def test_non_hex_rejected(self):
        with self.assertRaises(MacError):
            parse_mac("gg:bb:cc:dd:ee:ff")

    def test_empty_string_rejected(self):
        with self.assertRaises(MacError):
            parse_mac("")

    def test_non_string_rejected(self):
        with self.assertRaises(MacError):
            parse_mac(0xAABBCCDDEEFF)  # int, not str

    def test_eui64_rejected(self):
        # 16 hex digits is EUI-64, not MAC-48 — we do not support it.
        with self.assertRaises(MacError):
            parse_mac("aa:bb:cc:dd:ee:ff:00:11")


class TestIsValid(unittest.TestCase):
    def test_valid_returns_true(self):
        self.assertTrue(is_valid("aa:bb:cc:dd:ee:ff"))

    def test_invalid_returns_false(self):
        self.assertFalse(is_valid("not a mac"))

    def test_non_string_returns_false(self):
        self.assertFalse(is_valid(None))
        self.assertFalse(is_valid(12345))


class TestFormatMac(unittest.TestCase):
    def test_colon_to_colon(self):
        self.assertEqual(format_mac("aa:bb:cc:dd:ee:ff", MacFormat.COLON), "AA:BB:CC:DD:EE:FF")

    def test_raw_to_colon_default(self):
        # Default format is COLON.
        self.assertEqual(format_mac("aabbccddeeff"), "AA:BB:CC:DD:EE:FF")

    def test_colon_to_hyphen(self):
        self.assertEqual(format_mac("aa:bb:cc:dd:ee:ff", MacFormat.HYPHEN), "AA-BB-CC-DD-EE-FF")

    def test_colon_to_dot(self):
        self.assertEqual(format_mac("aa:bb:cc:dd:ee:ff", MacFormat.DOT), "AABB.CCDD.EEFF")

    def test_colon_to_raw(self):
        self.assertEqual(format_mac("aa:bb:cc:dd:ee:ff", MacFormat.RAW), "AABBCCDDEEFF")

    def test_dot_to_colon(self):
        self.assertEqual(format_mac("aabb.ccdd.eeff", MacFormat.COLON), "AA:BB:CC:DD:EE:FF")

    def test_hyphen_to_dot(self):
        self.assertEqual(format_mac("aa-bb-cc-dd-ee-ff", MacFormat.DOT), "AABB.CCDD.EEFF")

    def test_invalid_input_raises(self):
        with self.assertRaises(MacError):
            format_mac("nope", MacFormat.COLON)

    def test_invalid_format_type_raises(self):
        with self.assertRaises(TypeError):
            format_mac("aa:bb:cc:dd:ee:ff", "colon")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
