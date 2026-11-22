"""Run every test against a throwaway data folder, never your real Omen settings."""
import os
import pathlib
import sys
import tempfile

os.environ["OMEN_HOME"] = tempfile.mkdtemp(prefix="omen-test-")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402

import omen  # noqa: E402


@pytest.fixture(autouse=True)
def fresh(monkeypatch, tmp_path):
    omen.fails.update(n=0, strikes=0, until=0.0)
    omen.MEM.unlink(missing_ok=True)
    (tmp_path / "Desktop").mkdir()
    (tmp_path / "Downloads").mkdir()
    monkeypatch.setattr(omen, "HOME", tmp_path)
    monkeypatch.setattr(omen, "_start_apps", lambda: [{"Name": "Spotify", "AppID": "x"},
                                                      {"Name": "Microsoft Word", "AppID": "y"}])
    monkeypatch.setitem(omen.FEATURES, "camera", False)
    return tmp_path
