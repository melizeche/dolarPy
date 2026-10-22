# -*- encoding: utf-8 -*-
"""Tests for the Flask webservice."""
import json

import pytest

import cotiapp


@pytest.fixture
def client(tmp_path, monkeypatch):
    """A test client running in a throwaway working directory."""
    monkeypatch.chdir(tmp_path)
    cotiapp.app.config["TESTING"] = True
    with cotiapp.app.test_client() as client:
        client.workdir = tmp_path
        yield client


class TestIndex(object):
    def test_renders_the_calculator_page(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert b"DolarPy" in response.data

    def test_serves_html(self, client):
        assert "text/html" in client.get("/").headers["Content-Type"]


class TestApi(object):
    def test_serves_the_cached_dolar_json(self, client):
        payload = {"dolarpy": {"bcp": {"compra": 7100.0}}, "updated": "2025-09-01 10:00:00"}
        (client.workdir / "dolar.json").write_text(json.dumps(payload))

        response = client.get("/api/1.0/")

        assert response.status_code == 200
        assert response.mimetype == "application/json"
        assert json.loads(response.data) == payload

    def test_allows_cross_origin_requests(self, client):
        (client.workdir / "dolar.json").write_text("{}")
        response = client.get("/api/1.0/", headers={"Origin": "https://example.com"})
        assert response.headers["Access-Control-Allow-Origin"] == "https://example.com"

    def test_scrapes_on_demand_when_the_cache_is_missing(self, client, monkeypatch):
        calls = []
        monkeypatch.setattr(cotiapp, "create_json", lambda: '{"dolarpy": {}}')
        monkeypatch.setattr(cotiapp, "write_output", lambda: calls.append("written"))

        response = client.get("/api/1.0/")

        assert response.status_code == 200
        assert json.loads(response.data) == {"dolarpy": {}}
        assert calls == ["written"], "the freshly built payload should be cached"

    def test_unknown_routes_return_404(self, client):
        assert client.get("/api/2.0/").status_code == 404
