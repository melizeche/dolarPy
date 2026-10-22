# -*- encoding: utf-8 -*-
"""Tests for reading and writing dolar.json."""
import json

import pytest

import coti


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    """Run inside a throwaway directory so no real dolar.json is touched."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestWriteOutput(object):
    def test_creates_dolar_json_with_the_generated_payload(self, workdir, monkeypatch):
        monkeypatch.setattr(coti, "create_json", lambda: '{"dolarpy": {}}')
        coti.write_output()
        assert (workdir / "dolar.json").read_text() == '{"dolarpy": {}}'

    def test_overwrites_a_previous_run(self, workdir, monkeypatch):
        (workdir / "dolar.json").write_text("stale content that is much longer")
        monkeypatch.setattr(coti, "create_json", lambda: '{"new": true}')
        coti.write_output()
        assert json.loads((workdir / "dolar.json").read_text()) == {"new": True}


class TestGetOutput(object):
    def test_reads_dolar_json_back_verbatim(self, workdir):
        (workdir / "dolar.json").write_text('{"dolarpy": {"bcp": {}}}')
        assert coti.get_output() == '{"dolarpy": {"bcp": {}}}'

    def test_raises_when_the_file_does_not_exist(self, workdir):
        with pytest.raises(IOError):
            coti.get_output()

    def test_round_trips_what_write_output_produced(self, workdir, monkeypatch):
        monkeypatch.setattr(coti, "create_json", lambda: '{"updated": "now"}')
        coti.write_output()
        assert json.loads(coti.get_output()) == {"updated": "now"}


def test_importing_coti_does_not_hit_the_network_or_write_files(workdir):
    """The scrape only runs when coti.py is executed as a script (crontab)."""
    import subprocess
    import sys
    from pathlib import Path

    root = Path(coti.__file__).resolve().parent
    subprocess.check_call(
        [sys.executable, "-c", "import coti"],
        cwd=str(workdir),
        env={"PYTHONPATH": str(root), "PATH": "/usr/bin:/bin"},
    )
    assert not (workdir / "dolar.json").exists()
