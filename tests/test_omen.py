import io

import pytest

import omen


# ---- instant commands -------------------------------------------------------
def test_open_known_app():
    assert omen._fast_path("open spotify") == ("open_app", {"name": "spotify"})


def test_unknown_app_goes_to_the_model():
    assert omen._fast_path("open the file report") is None


def test_open_and_close_folder():
    assert omen._fast_path("open downloads folder") == ("open_path", {"path": "downloads"})
    assert omen._fast_path("close the downloads folder") == ("close_folder", {"name": "downloads"})


def test_close_app():
    assert omen._fast_path("close notepad") == ("close_app", {"name": "notepad"})


def test_reminder_commands_keep_capitals():
    assert omen._fast_path("Remind me in 30 minutes to call Sam") == \
        ("set_reminder", {"message": "call Sam", "minutes_from_now": 30.0})
    assert omen._fast_path("remind me in 2 hours that Tea is ready")[1]["minutes_from_now"] == 120.0
    assert omen._fast_path("remind me at 8:30 to leave") == ("set_reminder", {"message": "leave", "at": "8:30"})


def test_camera_commands_are_off_by_default_and_work_when_enabled(monkeypatch):
    assert omen._fast_path("take a photo") is None
    monkeypatch.setitem(omen.FEATURES, "camera", True)
    assert omen._fast_path("take a photo") == ("camera_snapshot", {})


def test_small_talk_is_not_a_command():
    assert omen._fast_path("tell me a joke") is None
    assert omen._fast_path("what is open") is None


def test_camera_tools_are_not_registered_by_default():
    assert "camera_snapshot" not in omen.RISKY and "watch_start" not in omen.RISKY


# ---- files and blocked places ----------------------------------------------
def test_system_folders_are_blocked(fresh):
    for p in ("AppData/Local", "Windows/System32", "Program Files/x"):
        with pytest.raises(PermissionError):
            omen.resolve(str(fresh / p))


def test_own_settings_are_blocked_but_reports_are_open():
    with pytest.raises(PermissionError):
        omen.resolve(str(omen.BASE / "config.json"))
    omen.resolve(str(omen.REPORTS))


def test_pick_file_exact_match_and_ambiguity(fresh):
    d = fresh / "Desktop"
    (d / "plapla photo.jpg").write_bytes(b"x")
    (d / "plapla notes.txt").write_text("a")
    assert omen._pick_file("plapla photo").name == "plapla photo.jpg"
    with pytest.raises(ValueError):
        omen._pick_file("plapla")


def test_sensitive_files_are_never_sent(fresh):
    d = fresh / "Desktop"
    (d / "my passwords.txt").write_text("a")
    (d / "server.pem").write_text("a")
    for name in ("passwords", "server"):
        with pytest.raises(FileNotFoundError):
            omen._pick_file(name)


def test_send_file_makes_a_share_link(fresh):
    f = fresh / "Desktop" / "a.txt"
    f.write_text("hello")
    out = omen.send_file(str(f))
    assert out.startswith("SHARE|")
    assert omen.shares[out.split("|")[1]][0] == f.resolve()


# ---- reminders and notes ----------------------------------------------------
def test_reminder_roundtrip():
    rid = omen.set_reminder("call Sam", minutes_from_now=5).split()[1]
    assert "call Sam" in omen.list_reminders()
    assert omen.cancel_reminder(rid) == "Cancelled."
    assert "No pending" in omen.list_reminders()


def test_reminder_rejects_bad_times():
    with pytest.raises(ValueError):
        omen.set_reminder("x", at="2020-01-01 10:00")
    with pytest.raises(ValueError):
        omen.set_reminder("x")


def test_notes_reach_the_prompt_and_can_be_forgotten():
    omen.remember("zebra-note-123")
    assert "zebra-note-123" in omen._sys()
    omen.forget_note("zebra-note")
    assert "zebra-note-123" not in omen._sys()


# ---- other logic ------------------------------------------------------------
def test_markdown_to_word():
    from docx import Document
    data = omen._md_to_docx("# Title\n\nHello **bold**\n\n## Part\n- one\n")
    styles = [p.style.name for p in Document(io.BytesIO(data)).paragraphs]
    assert {"Title", "Heading 2", "List Bullet"} <= set(styles)


def test_history_compaction_drops_tool_noise(monkeypatch):
    h = [{"role": "system", "content": "S"}]
    monkeypatch.setattr(omen, "history", h)
    for i in range(7):
        h += [{"role": "user", "content": f"u{i}"},
              {"role": "assistant", "content": "", "tool_calls": [1]},
              {"role": "tool", "content": "x"},
              {"role": "assistant", "content": f"a{i}"}]
        omen._compact()
    assert all(m["role"] in ("system", "user", "assistant") and not m.get("tool_calls") for m in h)
    assert len(h) <= 11


def test_only_relevant_tools_are_sent_to_the_model():
    assert omen._pick_tools("hi, how are you") is None
    assert "open_app" in [f.__name__ for f in omen._pick_tools("open chrome")]


def test_topic_cleaning():
    assert omen._topic("Write a short report on the latest news about electric cars") == \
        "the latest news about electric cars"
