# -*- encoding: utf-8 -*-
"""Rate history: every scraper run is kept in a small SQLite file, so the API
and the website can show how each source moved over time.

``dolar.json`` is still the live snapshot that the API and the bots read; this
module only adds a record of each run next to it. It uses ``sqlite3`` from the
standard library, so there is nothing new to install or to run.
"""
import json
import os
import sqlite3
from datetime import datetime, timedelta

DEFAULT_DB_PATH = "history.sqlite3"
DB_PATH_ENV = "DOLARPY_HISTORY_DB"

DEFAULT_DAYS = 30
MAX_DAYS = 366
MAX_RUN_DAYS = 31

SCHEMA = """
CREATE TABLE IF NOT EXISTS rates (
    taken_at TEXT NOT NULL,  -- the run's "updated" time, 'YYYY-MM-DD HH:MM:SS'
    source   TEXT NOT NULL,  -- the key in dolar.json, e.g. 'familiar'
    compra   REAL,           -- NULL when that side of the scraper failed
    venta    REAL,
    PRIMARY KEY (source, taken_at)
);
CREATE INDEX IF NOT EXISTS rates_by_time ON rates (taken_at);
"""


def db_path():
    """Where the history lives: ``$DOLARPY_HISTORY_DB`` or next to dolar.json."""
    return os.environ.get(DB_PATH_ENV) or DEFAULT_DB_PATH


def _connect(path):
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


def _rate(value):
    """A scraper that fails returns 0; keep that out of the history as NULL."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def record(payload, path=None):
    """Store one run, given the JSON text that ``create_json()`` produced.

    Returns the number of sources stored. A source whose compra and venta are
    both 0 (down, blocking us, or redesigned) is skipped, so a broken scraper
    leaves a gap instead of a drop to zero.
    """
    data = json.loads(payload)
    sources = data.get("dolarpy") or {}
    taken_at = data.get("updated") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows = []
    for source, rates in sorted(sources.items()):
        if not isinstance(rates, dict):
            continue
        compra, venta = _rate(rates.get("compra")), _rate(rates.get("venta"))
        if compra is None and venta is None:
            continue
        rows.append((taken_at, source, compra, venta))

    if not rows:
        return 0

    conn = _connect(path or db_path())
    try:
        with conn:
            # The same run stored twice (the API rebuilding a missing
            # dolar.json in the same second as the cron) is kept once.
            conn.executemany(
                "INSERT OR IGNORE INTO rates (taken_at, source, compra, venta) "
                "VALUES (?, ?, ?, ?)",
                rows,
            )
    finally:
        conn.close()
    return len(rows)


def sources(path=None):
    """Every source that has at least one stored run, sorted."""
    path = path or db_path()
    if not os.path.exists(path):
        return []
    conn = _connect(path)
    try:
        return [r[0] for r in conn.execute("SELECT DISTINCT source FROM rates ORDER BY source")]
    finally:
        conn.close()


def query(source=None, days=DEFAULT_DAYS, by="day", path=None, today=None):
    """The history of the last ``days`` days (today included), per source.

    ``by="day"`` gives one point per day: the last compra and the last venta
    stored that day, which is the rate a person saw when the day closed. ``by="run"`` gives every stored
    run, to see at what time a source moved.

    Returns ``{source: [{"date" or "time": ..., "compra": ..., "venta": ...}]}``
    with the points in chronological order.
    """
    if by not in ("day", "run"):
        raise ValueError("by must be 'day' or 'run'")

    path = path or db_path()
    if not os.path.exists(path):
        return {}

    today = today or datetime.now().date()
    since = (today - timedelta(days=days - 1)).strftime("%Y-%m-%d")

    where = "taken_at >= ?"
    params = [since]
    if source is not None:
        where += " AND source = ?"
        params.append(source)

    sql = (
        "SELECT source, taken_at, compra, venta FROM rates "
        "WHERE " + where + " ORDER BY source, taken_at"
    )

    conn = _connect(path)
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()

    history = {}
    for name, taken_at, compra, venta in rows:
        points = history.setdefault(name, [])
        if by == "run":
            points.append({"time": taken_at, "compra": compra, "venta": venta})
            continue
        day = taken_at[:10]
        if not points or points[-1]["date"] != day:
            points.append({"date": day, "compra": None, "venta": None})
        # The day's close is the last rate seen on each side; a run where only
        # one side failed does not erase the other side's last good value.
        if compra is not None:
            points[-1]["compra"] = compra
        if venta is not None:
            points[-1]["venta"] = venta
    return history
