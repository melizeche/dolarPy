# -*- encoding: utf-8 -*-
"""Shared pytest fixtures for the dolarPy test suite."""
import json
import sys
from pathlib import Path

import pytest
import requests

# Make the project modules (coti, cotiapp) importable no matter where pytest
# is invoked from.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class FakeResponse(object):
    """Minimal stand-in for a ``requests`` response object."""

    def __init__(self, text="", payload=None, status_code=200):
        if payload is not None and not text:
            text = json.dumps(payload)
        self.text = text
        self.content = text.encode("utf-8")
        self.status_code = status_code
        self._payload = payload

    def json(self):
        if self._payload is not None:
            return self._payload
        return json.loads(self.text)


@pytest.fixture
def fake_response():
    """Factory fixture so tests can build responses inline."""
    return FakeResponse


@pytest.fixture(autouse=True)
def block_network(request, monkeypatch):
    """Safety net: no offline test is allowed to reach the real internet.

    Tests marked ``live`` are exempt -- reaching the real sites is the point.

    The scrapers swallow every exception, so a leaked request would not blow
    up here; it would instead make the assertions on the scraped values fail,
    which is exactly the signal we want.
    """

    if "live" in request.keywords:
        # The live suite is meant to reach the real sites.
        return

    def _no_network(*args, **kwargs):
        raise RuntimeError(
            "A test tried to perform a real HTTP request. "
            "Patch coti.requests / coti.cloudscraper instead."
        )

    monkeypatch.setattr(requests.adapters.HTTPAdapter, "send", _no_network)
