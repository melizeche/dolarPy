# -*- encoding: utf-8 -*-
"""Health check against the published API.

This is what tells us whether the scrapers are actually working, and it asks
the only machine whose answer matters: the server that runs coti.py from the
crontab. Several sources (cambioschaco, continental) serve a block page to
datacenter IPs, so scraping them from a CI runner says nothing about whether
production captured them -- while this reads the document production really
published, from whatever IP, and so judges the thing consumers see.

Excluded from the default run; the nightly workflow runs it:

    pytest -m published

Set DOLARPY_API_URL to point it at a staging deployment.
"""
import json
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
import requests

pytestmark = pytest.mark.published

API_URL = os.environ.get(
    "DOLARPY_API_URL", "https://dolar.melizeche.com/api/1.0/"
)

# Sources the API is expected to keep publishing. A source added to coti.py
# needs no change here (it gets value-checked like the rest); retiring one is
# a deliberate change to the published contract, so it has to be removed here
# too -- which is the point.
EXPECTED_SOURCES = {
    "bcp",
    "bonanza",
    "cambiosalberdi",
    "cambioschaco",
    "continental",
    "eurocambios",
    "familiar",
    "gnbfusion",
    "lamoneda",
    "maxicambios",
    "mundialcambios",
    "mydcambios",
    "set",
    "ueno",
}

MIN_RATE = Decimal("3000")
MAX_RATE = Decimal("20000")

# BCP's "POR CORTE HORARIO" pair are averages of the trades settled in that
# hour rather than counter quotes, so they can legitimately cross.
NO_SPREAD_GUARANTEE = {"bcp"}

# coti.py stamps `updated` with datetime.now() and no offset, so it is the
# server's local time -- Asunción. The crontab scrapes every 10 minutes
# between 06:00 and 20:00 on weekdays, so inside that window anything older
# than this means the cron has stopped running.
MAX_AGE = timedelta(minutes=int(os.environ.get("DOLARPY_MAX_AGE_MINUTES", "60")))


def _asuncion():
    """Paraguay dropped DST in 2024, but prefer real tz data where present."""
    try:
        from zoneinfo import ZoneInfo

        return ZoneInfo("America/Asuncion")
    except Exception:
        return timezone(timedelta(hours=-3))


@pytest.fixture(scope="module")
def response():
    return requests.get(API_URL, timeout=30)


@pytest.fixture(scope="module")
def payload(response):
    return json.loads(response.text)


@pytest.fixture(scope="module")
def quotes(payload):
    return payload["dolarpy"]


class TestTheApiAnswers(object):
    def test_responds_with_200(self, response):
        assert response.status_code == 200, "%s returned %s" % (
            API_URL,
            response.status_code,
        )

    def test_serves_json(self, response):
        assert "json" in response.headers.get("Content-Type", "")
        json.loads(response.text)

    def test_has_the_documented_shape(self, payload):
        assert sorted(payload.keys()) == ["dolarpy", "updated"]


class TestTheDataIsFresh(object):
    def test_updated_is_parseable(self, payload):
        datetime.strptime(payload["updated"], "%Y-%m-%d %H:%M:%S")

    def test_the_cron_is_still_running(self, payload):
        stamped = datetime.strptime(
            payload["updated"], "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=_asuncion())
        age = datetime.now(timezone.utc) - stamped
        assert age <= MAX_AGE, (
            "dolar.json was last written %s (Asuncion), %d minutes ago -- the "
            "crontab on the server has stopped scraping, or this check ran "
            "outside its 06:00-20:00 weekday window"
            % (payload["updated"], age.total_seconds() // 60)
        )


class TestEverySourceIsPublished(object):
    def test_no_source_disappeared(self, quotes):
        missing = sorted(EXPECTED_SOURCES - set(quotes))
        assert not missing, "no longer published: %s" % ", ".join(missing)

    def test_every_source_has_both_prices(self, quotes):
        incomplete = sorted(
            name
            for name, quote in quotes.items()
            if "compra" not in quote or "venta" not in quote
        )
        assert not incomplete, "missing compra/venta: %s" % ", ".join(incomplete)


class TestEverySourceHasARate(object):
    def test_no_source_is_zeroed(self, quotes):
        """The headline failure: a scraper that stopped working."""
        zeroed = sorted(
            name
            for name, quote in quotes.items()
            if not quote.get("compra") or not quote.get("venta")
        )
        assert not zeroed, (
            "returning zero: %s -- the site changed its markup, started "
            "blocking the server, or (for ueno) the SOCKS proxy is down"
            % ", ".join(zeroed)
        )

    def test_every_rate_is_plausible(self, quotes):
        implausible = []
        for name, quote in sorted(quotes.items()):
            for label in ("compra", "venta"):
                value = Decimal(str(quote.get(label, 0)))
                if value and not (MIN_RATE <= value <= MAX_RATE):
                    implausible.append("%s %s=%s" % (name, label, value))
        assert not implausible, (
            "outside %s-%s guaranies per dollar, so the selector is reading "
            "the wrong cell: %s" % (MIN_RATE, MAX_RATE, ", ".join(implausible))
        )

    def test_no_spread_is_inverted(self, quotes):
        inverted = []
        for name, quote in sorted(quotes.items()):
            if name in NO_SPREAD_GUARANTEE:
                continue
            compra = Decimal(str(quote.get("compra", 0)))
            venta = Decimal(str(quote.get("venta", 0)))
            if compra and venta and venta < compra:
                inverted.append("%s venta=%s < compra=%s" % (name, venta, compra))
        assert not inverted, (
            "sell price below buy price, so the columns got swapped: %s"
            % ", ".join(inverted)
        )
