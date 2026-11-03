# -*- encoding: utf-8 -*-
"""Tests for the rate history: storing each run and reading it back."""
import json
import sqlite3
from datetime import date

import pytest

import coti
import cotiapp
import history


def run(updated, **sources):
    """The JSON text create_json() would produce for one run."""
    return json.dumps({
        "dolarpy": {
            name: {"compra": compra, "venta": venta}
            for name, (compra, venta) in sources.items()
        },
        "updated": updated,
    })


@pytest.fixture
def db(tmp_path, monkeypatch):
    path = str(tmp_path / "history.sqlite3")
    monkeypatch.setenv(history.DB_PATH_ENV, path)
    return path


def stored(path):
    conn = sqlite3.connect(path)
    try:
        return conn.execute(
            "SELECT taken_at, source, compra, venta FROM rates ORDER BY source, taken_at"
        ).fetchall()
    finally:
        conn.close()


class TestRecord(object):
    def test_stores_every_source_of_a_run(self, db):
        count = history.record(run("2026-11-03 10:00:00", familiar=(7650, 7800), bcp=(7700.5, 7720.25)))

        assert count == 2
        assert stored(db) == [
            ("2026-11-03 10:00:00", "bcp", 7700.5, 7720.25),
            ("2026-11-03 10:00:00", "familiar", 7650.0, 7800.0),
        ]

    def test_a_source_that_returned_zeros_is_left_out(self, db):
        history.record(run("2026-11-03 10:00:00", familiar=(7650, 7800), cambioschaco=(0, 0)))
        assert [row[1] for row in stored(db)] == ["familiar"]

    def test_one_failed_side_is_stored_as_null(self, db):
        history.record(run("2026-11-03 10:00:00", set=(0, 7790)))
        assert stored(db) == [("2026-11-03 10:00:00", "set", None, 7790.0)]

    def test_the_same_run_twice_is_kept_once(self, db):
        payload = run("2026-11-03 10:00:00", familiar=(7650, 7800))
        history.record(payload)
        history.record(payload)
        assert len(stored(db)) == 1

    def test_extra_fields_like_the_bcp_reference_are_ignored(self, db):
        payload = json.dumps({
            "dolarpy": {"bcp": {"compra": 7700, "venta": 7720, "referencial_diario": 7710}},
            "updated": "2026-11-03 10:00:00",
        })
        history.record(payload)
        assert stored(db) == [("2026-11-03 10:00:00", "bcp", 7700.0, 7720.0)]

    def test_a_run_with_nothing_scraped_creates_no_file(self, db):
        assert history.record(run("2026-11-03 10:00:00", familiar=(0, 0))) == 0
        assert history.sources() == []


class TestQuery(object):
    @pytest.fixture
    def three_days(self, db):
        history.record(run("2026-11-01 09:00:00", familiar=(7600, 7750)))
        history.record(run("2026-11-01 18:50:00", familiar=(7610, 7760), maxicambios=(7620, 7740)))
        history.record(run("2026-11-02 12:00:00", familiar=(7640, 7790)))
        history.record(run("2026-11-03 09:00:00", familiar=(7650, 7800)))
        history.record(run("2026-11-03 09:10:00", familiar=(0, 7810)))
        return db

    def test_by_day_gives_the_last_rate_of_each_day(self, three_days):
        result = history.query(source="familiar", days=30, today=date(2026, 11, 3))
        assert result == {"familiar": [
            {"date": "2026-11-01", "compra": 7610.0, "venta": 7760.0},
            {"date": "2026-11-02", "compra": 7640.0, "venta": 7790.0},
            # compra failed in the 09:10 run: the day keeps 09:00's compra
            {"date": "2026-11-03", "compra": 7650.0, "venta": 7810.0},
        ]}

    def test_by_run_gives_every_stored_run(self, three_days):
        result = history.query(source="familiar", days=1, by="run", today=date(2026, 11, 3))
        assert result == {"familiar": [
            {"time": "2026-11-03 09:00:00", "compra": 7650.0, "venta": 7800.0},
            {"time": "2026-11-03 09:10:00", "compra": None, "venta": 7810.0},
        ]}

    def test_days_counts_today_and_goes_back(self, three_days):
        result = history.query(source="familiar", days=2, today=date(2026, 11, 3))
        assert [p["date"] for p in result["familiar"]] == ["2026-11-02", "2026-11-03"]

    def test_without_a_source_every_source_is_returned(self, three_days):
        result = history.query(days=30, today=date(2026, 11, 3))
        assert sorted(result) == ["familiar", "maxicambios"]

    def test_no_file_yet_means_no_history(self, db):
        assert history.query() == {}

    def test_rejects_an_unknown_grouping(self, db):
        with pytest.raises(ValueError):
            history.query(by="week")


class TestWriteOutputRecordsTheRun(object):
    @pytest.fixture
    def workdir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv(history.DB_PATH_ENV, raising=False)
        return tmp_path

    def test_each_run_lands_in_the_history_next_to_dolar_json(self, workdir, monkeypatch):
        monkeypatch.setattr(coti, "create_json", lambda: run("2026-11-03 10:00:00", ueno=(7660, 7790)))
        coti.write_output()
        assert stored(str(workdir / "history.sqlite3")) == [
            ("2026-11-03 10:00:00", "ueno", 7660.0, 7790.0)
        ]

    def test_dolar_json_is_written_even_if_the_history_fails(self, workdir, monkeypatch):
        monkeypatch.setattr(coti, "create_json", lambda: run("2026-11-03 10:00:00", ueno=(7660, 7790)))

        def broken(payload):
            raise sqlite3.OperationalError("disk I/O error")

        monkeypatch.setattr(history, "record", broken)
        coti.write_output()
        assert json.loads((workdir / "dolar.json").read_text())["dolarpy"]["ueno"]["compra"] == 7660


class TestHistoryApi(object):
    @pytest.fixture
    def client(self, db):
        history.record(run(date.today().strftime("%Y-%m-%d") + " 10:00:00", familiar=(7650, 7800)))
        cotiapp.app.config["TESTING"] = True
        with cotiapp.app.test_client() as client:
            yield client

    def test_returns_the_daily_history_of_a_source(self, client):
        response = client.get("/api/1.0/history/?source=familiar&days=7")

        assert response.status_code == 200
        assert response.mimetype == "application/json"
        body = json.loads(response.data)
        assert body["days"] == 7 and body["by"] == "day"
        assert body["history"]["familiar"][0]["compra"] == 7650.0

    def test_defaults_to_thirty_days_by_day_for_every_source(self, client):
        body = json.loads(client.get("/api/1.0/history/").data)
        assert (body["days"], body["by"], list(body["history"])) == (30, "day", ["familiar"])

    def test_by_run(self, client):
        body = json.loads(client.get("/api/1.0/history/?source=familiar&by=run").data)
        assert list(body["history"]["familiar"][0]) == ["time", "compra", "venta"]

    @pytest.mark.parametrize("query", ["days=0", "days=367", "days=abc", "by=week", "by=run&days=32"])
    def test_rejects_bad_parameters(self, client, query):
        response = client.get("/api/1.0/history/?" + query)
        assert response.status_code == 400
        assert "error" in json.loads(response.data)

    def test_unknown_source_is_404(self, client):
        assert client.get("/api/1.0/history/?source=nope").status_code == 404

    def test_allows_cross_origin_requests(self, client):
        response = client.get("/api/1.0/history/", headers={"Origin": "https://example.com"})
        assert response.headers["Access-Control-Allow-Origin"] == "https://example.com"
