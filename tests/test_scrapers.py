# -*- encoding: utf-8 -*-
"""Tests for every exchange-rate scraper in coti.py.

Each source is covered three ways:

* the happy path, against a trimmed copy of the real markup/JSON;
* a ``requests.ConnectionError``, which must degrade to zeros;
* an unexpected page shape, which must also degrade to zeros instead of
  raising -- a broken source must never take the whole run down.
"""
from decimal import Decimal

import pytest
import requests

import coti
import sample_pages as pages


class RecordingGet(object):
    """Callable that replaces ``requests.get`` / ``requests.post``."""

    def __init__(self, response):
        self.response = response
        self.calls = []

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        if isinstance(self.response, BaseException):
            raise self.response
        return self.response

    @property
    def url(self):
        return self.calls[0][0][0]

    @property
    def kwargs(self):
        return self.calls[0][1]


@pytest.fixture
def patch_get(monkeypatch, fake_response):
    """Patch ``coti.requests.get`` and hand back the recorder."""

    def _patch(text="", payload=None):
        recorder = RecordingGet(fake_response(text=text, payload=payload))
        monkeypatch.setattr(coti.requests, "get", recorder)
        return recorder

    return _patch


@pytest.fixture
def patch_post(monkeypatch, fake_response):
    def _patch(text="", payload=None):
        recorder = RecordingGet(fake_response(text=text, payload=payload))
        monkeypatch.setattr(coti.requests, "post", recorder)
        return recorder

    return _patch


@pytest.fixture
def patch_scraper(monkeypatch, fake_response):
    """Patch ``cloudscraper.create_scraper`` for the BCP scraper."""

    def _patch(*pages_text):
        responses = [fake_response(text=t) for t in pages_text]

        class FakeScraper(object):
            def __init__(self):
                self.calls = []

            def get(self, url, **kwargs):
                self.calls.append((url, kwargs))
                index = min(len(self.calls) - 1, len(responses) - 1)
                return responses[index]

        scraper = FakeScraper()
        monkeypatch.setattr(coti.cloudscraper, "create_scraper", lambda *a, **k: scraper)
        return scraper

    return _patch


class TestChaco(object):
    def test_parses_the_first_item_of_the_api(self, patch_get):
        import json

        get = patch_get(text=json.dumps(pages.CHACO_JSON))
        assert coti.chaco() == (Decimal("7180"), Decimal("7280"))
        assert "cambioschaco.com.py" in get.url
        assert get.kwargs["timeout"] == 10

    def test_invalid_json_returns_zeros(self, patch_get):
        patch_get(text="<html>not json</html>")
        assert coti.chaco() == (0, 0)


class TestMaxi(object):
    def test_parses_the_first_row_of_the_fixed_plugin_table(self, patch_get):
        get = patch_get(text=pages.MAXI_HTML)
        assert coti.maxi() == (Decimal("7150"), Decimal("7250"))
        assert get.url == "https://www.maxicambios.com.py/"

    def test_missing_table_returns_zeros(self, patch_get):
        patch_get(text="<html><body>maintenance</body></html>")
        assert coti.maxi() == (0, 0)


class TestAlberdi(object):
    def test_picks_the_dollar_row_and_not_the_first_one(self, patch_get):
        patch_get(text=pages.ALBERDI_HTML)
        assert coti.alberdi() == (Decimal("7190"), Decimal("7290"))

    def test_without_a_dollar_row_returns_zeros(self, patch_get):
        patch_get(text=pages.ALBERDI_HTML_NO_DOLLAR)
        assert coti.alberdi() == (0, 0)

    def test_missing_table_returns_zeros(self, patch_get):
        patch_get(text="<html><body>nothing here</body></html>")
        assert coti.alberdi() == (0, 0)


class TestBcp(object):
    def test_parses_referencial_and_last_fluctuante_row(self, patch_scraper):
        scraper = patch_scraper(
            pages.BCP_REFERENCIAL_HTML, pages.BCP_FLUCTUANTE_HTML
        )
        compra, venta, ref = coti.bcp()
        assert (compra, venta, ref) == (
            Decimal("7150.50"),
            Decimal("7250.50"),
            Decimal("7222.33"),
        )
        assert [url for url, _ in scraper.calls] == [
            "https://www.bcp.gov.py/webapps/web/cotizacion/monedas",
            "https://www.bcp.gov.py/webapps/web/cotizacion/referencial-fluctuante",
        ]

    def test_sends_a_browser_user_agent(self, patch_scraper):
        scraper = patch_scraper(
            pages.BCP_REFERENCIAL_HTML, pages.BCP_FLUCTUANTE_HTML
        )
        coti.bcp()
        assert "Mozilla" in scraper.calls[0][1]["headers"]["User-Agent"]

    def test_unexpected_markup_returns_three_zeros(self, patch_scraper):
        patch_scraper("<html></html>", "<html></html>")
        assert coti.bcp() == (0, 0, 0)


class TestSetGov(object):
    def test_parses_the_last_row_of_the_first_table(self, patch_get):
        get = patch_get(text=pages.SET_HTML)
        assert coti.setgov() == (Decimal("7160"), Decimal("7260"))
        assert "dnit.gov.py" in get.url

    def test_missing_table_returns_zeros(self, patch_get):
        patch_get(text="<html><body>down</body></html>")
        assert coti.setgov() == (0, 0)


class TestEurocambio(object):
    def test_posts_the_expected_payload_and_parses_the_answer(self, patch_post):
        post = patch_post(payload=pages.EUROCAMBIO_JSON)
        assert coti.eurocambio() == (Decimal("7170"), Decimal("7270"))
        args, kwargs = post.calls[0]
        assert args[0] == "https://eurocambios.com.py/v2/sgi/utilsDto.php"
        assert args[1] == {
            "param": "getCotizacionesbySucursal",
            "sucursal": "1",
        }
        assert kwargs["timeout"] == 10

    def test_empty_payload_returns_zeros(self, patch_post):
        patch_post(payload=[])
        assert coti.eurocambio() == (0, 0)


class TestMyd(object):
    def test_parses_the_second_banner_list(self, patch_get):
        patch_get(text=pages.MYD_HTML)
        assert coti.myd() == (Decimal("7140"), Decimal("7240"))

    def test_missing_banner_returns_zeros(self, patch_get):
        patch_get(text="<html><body></body></html>")
        assert coti.myd() == (0, 0)


class TestBonanza(object):
    def test_parses_the_pricing_table(self, patch_get):
        get = patch_get(text=pages.BONANZA_HTML)
        assert coti.bonanza() == (Decimal("7130"), Decimal("7230"))
        assert get.url == "https://bonanzacambios.com.py/"

    def test_missing_table_returns_zeros(self, patch_get):
        patch_get(text="<html><body></body></html>")
        assert coti.bonanza() == (0, 0)


class TestFamiliar(object):
    def test_parses_the_third_and_fourth_content_items(self, patch_get):
        get = patch_get(text=pages.FAMILIAR_HTML)
        assert coti.familiar() == (Decimal("7110"), Decimal("7210"))
        assert get.url == "https://www.familiar.com.py/"

    def test_fewer_items_than_expected_returns_zeros(self, patch_get):
        patch_get(
            text='<div class="content-item flex-between horizontal-between">'
            '<span class="text-m">Euro</span><span class="text-m">7800</span></div>'
        )
        assert coti.familiar() == (0, 0)


class TestLamoneda(object):
    def test_parses_the_first_row_of_the_first_table(self, patch_get):
        patch_get(text=pages.LAMONEDA_HTML)
        assert coti.lamoneda() == (Decimal("7120"), Decimal("7220"))

    def test_missing_table_returns_zeros(self, patch_get):
        patch_get(text="<html><body></body></html>")
        assert coti.lamoneda() == (0, 0)


class TestBbva(object):
    def test_parses_the_first_exchange_rate(self, patch_get):
        get = patch_get(payload=pages.BBVA_JSON)
        assert coti.bbva() == (Decimal("7160"), Decimal("7260"))
        assert "bancognb.com.py" in get.url

    def test_missing_key_returns_zeros(self, patch_get):
        patch_get(payload={"exchangeRates": []})
        assert coti.bbva() == (0, 0)


class TestMundial(object):
    def test_parses_and_normalises_the_first_row(self, patch_get):
        get = patch_get(text=pages.MUNDIAL_HTML)
        assert coti.mundial() == (Decimal("7170"), Decimal("7270"))
        assert "mundialcambios.com.py" in get.url
        assert get.kwargs["timeout"] == 20

    def test_missing_cells_returns_zeros(self, patch_get):
        patch_get(text="<html><body></body></html>")
        assert coti.mundial() == (0, 0)


# --- cross-cutting guarantees -------------------------------------------------

SCRAPERS = [
    coti.chaco,
    coti.maxi,
    coti.alberdi,
    coti.bcp,
    coti.setgov,
    coti.eurocambio,
    coti.myd,
    coti.bonanza,
    coti.familiar,
    coti.lamoneda,
    coti.bbva,
    coti.mundial,
]


@pytest.fixture
def everything_offline(monkeypatch):
    def _boom(*args, **kwargs):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(coti.requests, "get", _boom)
    monkeypatch.setattr(coti.requests, "post", _boom)
    monkeypatch.setattr(coti.cloudscraper, "create_scraper", _boom)


@pytest.mark.parametrize("scraper", SCRAPERS, ids=lambda f: f.__name__)
def test_connection_errors_degrade_to_zeros(scraper, everything_offline):
    result = scraper()
    assert all(value == 0 for value in result)


@pytest.mark.parametrize("scraper", SCRAPERS, ids=lambda f: f.__name__)
def test_results_are_always_a_tuple_of_decimals(scraper, everything_offline):
    result = scraper()
    expected_length = 3 if scraper.__name__ == "bcp" else 2
    assert isinstance(result, tuple)
    assert len(result) == expected_length


@pytest.mark.parametrize("scraper", SCRAPERS, ids=lambda f: f.__name__)
def test_unexpected_responses_never_raise(scraper, monkeypatch, fake_response):
    """A redesigned page or an error page must not break the whole run."""
    garbage = fake_response(text="<html><body>503 Service Unavailable</body></html>")
    monkeypatch.setattr(coti.requests, "get", lambda *a, **k: garbage)
    monkeypatch.setattr(coti.requests, "post", lambda *a, **k: garbage)

    class FakeScraper(object):
        def get(self, *a, **k):
            return garbage

    monkeypatch.setattr(coti.cloudscraper, "create_scraper", lambda *a, **k: FakeScraper())

    result = scraper()
    assert all(value == 0 for value in result)
