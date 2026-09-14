# -*- encoding: utf-8 -*-
"""Tests for the JSON document the API and the bots consume."""
import json
import re
from decimal import Decimal

import pytest

import coti

# Every scraper gets a distinct value so a wiring mistake (source A's value
# ending up under source B's key) shows up as a failure.
STUBS = {
    "chaco": (Decimal("7101"), Decimal("7201")),
    "maxi": (Decimal("7102"), Decimal("7202")),
    "alberdi": (Decimal("7103"), Decimal("7203")),
    "setgov": (Decimal("7104"), Decimal("7204")),
    "eurocambio": (Decimal("7105"), Decimal("7205")),
    "myd": (Decimal("7106"), Decimal("7206")),
    "bbva": (Decimal("7107"), Decimal("7207")),
    "familiar": (Decimal("7108"), Decimal("7208")),
    "mundial": (Decimal("7109"), Decimal("7209")),
    "bonanza": (Decimal("7110"), Decimal("7210")),
    "lamoneda": (Decimal("7111"), Decimal("7211")),
    "bcp": (Decimal("7112"), Decimal("7212"), Decimal("7312")),
}

SOURCE_TO_KEY = {
    "chaco": "cambioschaco",
    "maxi": "maxicambios",
    "alberdi": "cambiosalberdi",
    "setgov": "set",
    "eurocambio": "eurocambios",
    "myd": "mydcambios",
    "bbva": "gnbfusion",
    "familiar": "familiar",
    "mundial": "mundialcambios",
    "bonanza": "bonanza",
    "lamoneda": "lamoneda",
    "bcp": "bcp",
}


@pytest.fixture
def stubbed_scrapers(monkeypatch):
    """Replace every scraper with a constant so create_json is deterministic."""
    for name, value in STUBS.items():
        monkeypatch.setattr(coti, name, (lambda v: (lambda: v))(value))
    return STUBS


@pytest.fixture
def payload(stubbed_scrapers):
    return json.loads(coti.create_json())


class TestCreateJson(object):
    def test_returns_a_json_string(self, stubbed_scrapers):
        raw = coti.create_json()
        assert isinstance(raw, str)
        json.loads(raw)

    def test_has_the_documented_top_level_shape(self, payload):
        assert sorted(payload.keys()) == ["dolarpy", "updated"]

    def test_lists_every_active_source(self, payload):
        assert sorted(payload["dolarpy"].keys()) == sorted(SOURCE_TO_KEY.values())

    def test_disabled_sources_are_not_published(self, payload):
        assert "interfisa" not in payload["dolarpy"]
        assert "amambay" not in payload["dolarpy"]

    @pytest.mark.parametrize("source, key", sorted(SOURCE_TO_KEY.items()))
    def test_each_source_lands_under_its_own_key(self, payload, source, key):
        compra, venta = STUBS[source][0], STUBS[source][1]
        assert payload["dolarpy"][key]["compra"] == float(compra)
        assert payload["dolarpy"][key]["venta"] == float(venta)

    def test_bcp_also_publishes_the_daily_reference(self, payload):
        assert payload["dolarpy"]["bcp"]["referencial_diario"] == float(
            STUBS["bcp"][2]
        )

    def test_bcp_is_the_only_source_with_three_values(self, payload):
        for key, quote in payload["dolarpy"].items():
            expected = ["compra", "referencial_diario", "venta"] if key == "bcp" \
                else ["compra", "venta"]
            assert sorted(quote.keys()) == expected

    def test_decimals_are_serialised_as_numbers_not_strings(self, payload):
        for quote in payload["dolarpy"].values():
            for value in quote.values():
                assert isinstance(value, float)

    def test_updated_uses_the_documented_timestamp_format(self, payload):
        assert re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", payload["updated"])

    def test_keys_are_sorted_and_indented_for_humans(self, stubbed_scrapers):
        raw = coti.create_json()
        assert raw.startswith("{\n    ")
        assert raw.index('"dolarpy"') < raw.index('"updated"')

    def test_a_failing_source_is_published_as_zeros(self, monkeypatch, stubbed_scrapers):
        monkeypatch.setattr(coti, "maxi", lambda: (0, 0))
        payload = json.loads(coti.create_json())
        assert payload["dolarpy"]["maxicambios"] == {"compra": 0, "venta": 0}

    def test_output_covers_what_the_tweet_bot_reads(self, payload):
        """single_tweet_bot.py indexes these keys directly."""
        for key in ["cambioschaco", "mundialcambios", "mydcambios", "maxicambios"]:
            assert {"compra", "venta"} <= set(payload["dolarpy"][key])
        for key in ["bcp", "set"]:
            assert {"compra", "venta"} <= set(payload["dolarpy"][key])
        assert payload["updated"]
