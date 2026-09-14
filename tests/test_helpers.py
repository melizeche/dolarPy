# -*- encoding: utf-8 -*-
"""Tests for the small pure helpers in coti.py."""
from decimal import Decimal

import pytest

import coti


class TestDecimalDefault(object):
    def test_converts_decimal_to_float(self):
        assert coti.decimal_default(Decimal("7250.50")) == 7250.5
        assert isinstance(coti.decimal_default(Decimal("7250")), float)

    def test_keeps_integer_decimals_exact(self):
        assert coti.decimal_default(Decimal("7250")) == 7250.0

    @pytest.mark.parametrize("value", ["7250", 7250, 7250.0, None, [Decimal("1")]])
    def test_raises_type_error_on_anything_else(self, value):
        with pytest.raises(TypeError):
            coti.decimal_default(value)

    def test_is_usable_as_json_default(self):
        import json

        dumped = json.dumps({"compra": Decimal("7250")}, default=coti.decimal_default)
        assert json.loads(dumped) == {"compra": 7250.0}


class TestFormatDecimal(object):
    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("7.250,50", "7250.50"),
            ("7.250", "7250"),
            ("1.234.567,89", "1234567.89"),
            ("7250", "7250"),
            (",5", ".5"),
            ("", ""),
        ],
    )
    def test_converts_spanish_notation_to_decimal_notation(self, raw, expected):
        assert coti.format_decimal(raw) == expected

    def test_result_is_parseable_by_decimal(self):
        assert Decimal(coti.format_decimal("7.250,50")) == Decimal("7250.50")

    def test_accepts_non_string_input(self):
        assert coti.format_decimal(7250) == "7250"
