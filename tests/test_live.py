# -*- encoding: utf-8 -*-
"""Live checks against the real exchange sites.

These are the tests that actually answer "do the scrapers still scrape?".
They are excluded from the default run (see the ``-m "not live"`` in
pytest.ini) because they need network access and depend on twelve third
parties being up; run them on purpose:

    pytest -m live                  # every source
    pytest -m live -k maxi          # one source, while fixing it

A failure means either the source is down or it changed its markup and the
selector in coti.py needs updating. The nightly workflow
(.github/workflows/live-scrapers.yml) runs this and opens an issue when a
check fails twice in a row, so a single flaky night stays quiet.
"""
from decimal import Decimal

import pytest

import coti

pytestmark = pytest.mark.live

# The guaraní has traded between roughly 6.000 and 8.000 to the dollar for
# years. The bounds are deliberately wide: this is a "did we parse a price at
# all" check, not a forecast. A value outside them almost always means the
# selector picked up the wrong cell (a date, a percentage, a euro rate).
MIN_RATE = Decimal("3000")
MAX_RATE = Decimal("20000")

SOURCES = [
    ("cambioschaco", coti.chaco),
    ("maxicambios", coti.maxi),
    ("cambiosalberdi", coti.alberdi),
    ("bcp", coti.bcp),
    ("set", coti.setgov),
    ("eurocambios", coti.eurocambio),
    ("mydcambios", coti.myd),
    ("bonanza", coti.bonanza),
    ("familiar", coti.familiar),
    ("lamoneda", coti.lamoneda),
    ("gnbfusion", coti.bbva),
    ("mundialcambios", coti.mundial),
]


@pytest.fixture(scope="module")
def rates():
    """Scrape every source once, so the suite hits each site a single time."""
    return {name: scraper() for name, scraper in SOURCES}


@pytest.mark.parametrize("name", [n for n, _ in SOURCES])
def test_source_returns_a_rate(rates, name):
    compra, venta = rates[name][0], rates[name][1]
    assert compra != 0, (
        "%s returned 0 for compra -- the site is down, blocking us, or it "
        "changed its markup and the selector in coti.py needs updating" % name
    )
    assert venta != 0, "%s returned 0 for venta" % name


@pytest.mark.parametrize("name", [n for n, _ in SOURCES])
def test_rate_is_plausible(rates, name):
    compra, venta = rates[name][0], rates[name][1]
    for label, value in (("compra", compra), ("venta", venta)):
        assert MIN_RATE <= value <= MAX_RATE, (
            "%s %s = %s is outside %s-%s guaranies per dollar -- the selector "
            "is probably reading the wrong cell" % (name, label, value, MIN_RATE, MAX_RATE)
        )


# BCP publishes "POR CORTE HORARIO" compra/venta -- the average of the trades
# actually settled in that hour, not a counter quote -- and those two averages
# can legitimately cross (seen 2026-10-23: compra 5.774,54 / venta 5.766,62).
# Every other source here is somebody selling dollars over a counter, where a
# sell price below the buy price would mean losing money on every transaction,
# so an inverted spread there really does mean the columns got swapped.
NO_SPREAD_GUARANTEE = {"bcp"}

SPREAD_SOURCES = [n for n, _ in SOURCES if n not in NO_SPREAD_GUARANTEE]


@pytest.mark.parametrize("name", SPREAD_SOURCES)
def test_sell_price_is_not_below_buy_price(rates, name):
    """An inverted spread means the compra/venta columns got swapped."""
    compra, venta = rates[name][0], rates[name][1]
    assert venta >= compra, "%s: venta %s < compra %s" % (name, venta, compra)


def test_bcp_also_returns_the_daily_reference(rates):
    ref = rates["bcp"][2]
    assert ref != 0, "BCP referencial diario returned 0"
    assert MIN_RATE <= ref <= MAX_RATE
