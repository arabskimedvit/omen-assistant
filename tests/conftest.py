"""Run every test against a throwaway data folder, never your real Omen settings.

The folders live inside tests/_work (not the system temp folder) because Omen
deliberately blocks any path containing "AppData", and on Windows the temp
folder is inside AppData.
"""
import atexit
import os
import pathlib
import shutil
import sys
import tempfile

WORK = pathlib.Path(__file__).resolve().parent / "_work"
WORK.mkdir(exist_ok=True)
atexit.register(shutil.rmtree, str(WORK), ignore_errors=True)
os.environ["OMEN_HOME"] = tempfile.mkdtemp(prefix="data-", dir=WORK)
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402

import omen  # noqa: E402


@pytest.fixture(autouse=True)
def fresh(monkeypatch):
    home = pathlib.Path(tempfile.mkdtemp(prefix="home-", dir=WORK))
    omen.fails.update(n=0, strikes=0, until=0.0)
    omen.MEM.unlink(missing_ok=True)
    (home / "Desktop").mkdir()
    (home / "Downloads").mkdir()
    monkeypatch.setattr(omen, "HOME", home)
    monkeypatch.setattr(omen, "_start_apps", lambda: [{"Name": "Spotify", "AppID": "x"},
                                                      {"Name": "Microsoft Word", "AppID": "y"}])
    monkeypatch.setitem(omen.FEATURES, "camera", False)
    return home
