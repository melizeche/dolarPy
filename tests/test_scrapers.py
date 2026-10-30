# -*- encoding: utf-8 -*-
"""Offline tests for the scrapers in coti.py.

These deliberately do NOT assert that a given CSS selector finds a rate in a
saved copy of a page: saved markup goes stale the moment a site is redesigned,
and keeping it current costs a fixture update on every scraper fix. Checking
that the selectors really work is the job of the live suite
(``pytest -m live``, see tests/test_live.py), which asks the real sites.

What is tested here is the part that must hold regardless of how any site
looks: each source is fetched from the right endpoint, and a source that is
offline, blocked or redesigned degrades to zeros instead of raising and
taking the other eleven down with it.
"""
from decimal import Decimal

import pytest
import requests

import coti

# A page that parses fine as HTML but contains none of the elements any of the
# scrapers look for -- what a redesign, an error page or a block page looks
# like from the scraper's point of view.
UNEXPECTED_PAGE = "<html><body><h1>503 Service Unavailable</h1></body></html>"


class RecordingGet(object):
    """Callable that replaces ``requests.get`` / ``requests.post``."""

    def __init__(self, response):
        self.response = response
        self.calls = []

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.response

    @property
    def url(self):
        return self.calls[0][0][0]

    @property
    def kwargs(self):
        return self.calls[0][1]


@pytest.fixture
def patch_get(monkeypatch, fake_response):
    def _patch(text=UNEXPECTED_PAGE, payload=None):
        recorder = RecordingGet(fake_response(text=text, payload=payload))
        monkeypatch.setattr(coti.requests, "get", recorder)
        return recorder

    return _patch


@pytest.fixture
def patch_post(monkeypatch, fake_response):
    def _patch(text=UNEXPECTED_PAGE, payload=None):
        recorder = RecordingGet(fake_response(text=text, payload=payload))
        monkeypatch.setattr(coti.requests, "post", recorder)
        return recorder

    return _patch


@pytest.fixture
def patch_scraper(monkeypatch, fake_response):
    """Patch ``cloudscraper.create_scraper`` for the BCP scraper."""

    def _patch(*pages_text):
        pages_text = pages_text or (UNEXPECTED_PAGE,)
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


# --- endpoints ----------------------------------------------------------------
#
# Where each source is fetched from, and with what timeout. Unlike a CSS
# selector, this only changes when somebody edits coti.py on purpose, so
# pinning it is cheap and catches an accidental edit.

GET_ENDPOINTS = [
    ("chaco", "https://www.cambioschaco.com.py/api/branch_office/1/exchange", 10),
    ("maxi", "https://www.maxicambios.com.py/", 10),
    (
        "alberdi",
        "https://www.cambiosalberdi.com/langes/index.php#sectionCotizacion",
        10,
    ),
    ("setgov", "https://www.dnit.gov.py/en/web/portal-institucional/cotizaciones", 10),
    ("myd", "https://www.mydcambios.com.py/", 10),
    ("bonanza", "https://bonanzacambios.com.py/api/board", 10),
    ("familiar", "https://www.familiar.com.py/", 10),
    ("lamoneda", "http://www.lamoneda.com.py/", 10),
    ("bbva", "https://www.bancognb.com.py/public/currency_quotations", 10),
    ("mundial", "http://www.mundialcambios.com.py/?branch=6", 20),
    ("ueno", "https://www.ueno.com.py/en/currency-exchange/", 10),
]


@pytest.mark.parametrize("source, url, timeout", GET_ENDPOINTS, ids=lambda v: v if isinstance(v, str) and "/" not in v else None)
def test_source_is_fetched_from_its_endpoint(patch_get, source, url, timeout):
    get = patch_get()
    getattr(coti, source)()
    assert get.url == url
    assert get.kwargs["timeout"] == timeout


def test_eurocambio_posts_the_expected_payload(patch_post):
    post = patch_post(payload=[])
    coti.eurocambio()
    args, kwargs = post.calls[0]
    assert args[0] == "https://eurocambios.com.py/v2/sgi/utilsDto.php"
    assert args[1] == {"param": "getCotizacionesbySucursal", "sucursal": "1"}
    assert kwargs["timeout"] == 10


def test_continental_gets_a_token_and_sends_it_to_the_rates_endpoint(patch_get, patch_post):
    post = patch_post(payload={"access_token": "tok"})
    get = patch_get(payload=[])
    coti.continental()

    assert post.url == (
        "https://apibanking-gw.bancontinental.com.py/autenticarServicio/v1/realms/interno"
    )
    assert post.kwargs["timeout"] == 10
    assert post.kwargs["headers"]["Grant-Type"] == "client_credentials"
    assert get.url == (
        "https://apibanking-gw.bancontinental.com.py/divisas/v1/api/monedas/cotizaciones"
    )
    assert get.kwargs["timeout"] == 10
    assert get.kwargs["headers"]["Authorization"] == "Bearer tok"


def test_bcp_starts_from_the_referencial_page(patch_scraper):
    """The fluctuante page is only fetched once the first one parses, so a
    stubbed run reaches exactly this one endpoint."""
    scraper = patch_scraper()
    coti.bcp()
    assert scraper.calls[0][0] == (
        "https://www.bcp.gov.py/webapps/web/cotizacion/monedas"
    )


def test_bcp_sends_a_browser_user_agent(patch_scraper):
    """BCP is behind Cloudflare; a default requests UA gets blocked."""
    scraper = patch_scraper()
    coti.bcp()
    assert "Mozilla" in scraper.calls[0][1]["headers"]["User-Agent"]


# --- degradation --------------------------------------------------------------

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
    coti.ueno,
    coti.continental,
]


@pytest.fixture
def everything_offline(monkeypatch):
    def _boom(*args, **kwargs):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(coti.requests, "get", _boom)
    monkeypatch.setattr(coti.requests, "post", _boom)
    monkeypatch.setattr(coti.cloudscraper, "create_scraper", _boom)


@pytest.fixture
def everything_unexpected(monkeypatch, fake_response):
    """Every source answers with a page that has none of the expected elements."""
    garbage = fake_response(text=UNEXPECTED_PAGE)
    monkeypatch.setattr(coti.requests, "get", lambda *a, **k: garbage)
    monkeypatch.setattr(coti.requests, "post", lambda *a, **k: garbage)

    class FakeScraper(object):
        def get(self, *a, **k):
            return garbage

    monkeypatch.setattr(
        coti.cloudscraper, "create_scraper", lambda *a, **k: FakeScraper()
    )


@pytest.mark.parametrize("scraper", SCRAPERS, ids=lambda f: f.__name__)
def test_connection_errors_degrade_to_zeros(scraper, everything_offline):
    assert all(value == 0 for value in scraper())


@pytest.mark.parametrize("scraper", SCRAPERS, ids=lambda f: f.__name__)
def test_redesigned_pages_degrade_to_zeros(scraper, everything_unexpected):
    """A source that changed its markup must not raise -- it reports zeros."""
    assert all(value == 0 for value in scraper())


@pytest.mark.parametrize("scraper", SCRAPERS, ids=lambda f: f.__name__)
def test_json_sources_survive_an_html_error_page(scraper, everything_unexpected):
    """chaco/bbva/eurocambios parse JSON; an HTML error page must not raise."""
    result = scraper()
    assert isinstance(result, tuple)
    assert all(isinstance(value, (Decimal, int)) for value in result)


@pytest.mark.parametrize("scraper", SCRAPERS, ids=lambda f: f.__name__)
def test_result_arity_is_stable(scraper, everything_offline):
    """create_json unpacks these tuples positionally."""
    expected = 3 if scraper.__name__ == "bcp" else 2
    assert len(scraper()) == expected
