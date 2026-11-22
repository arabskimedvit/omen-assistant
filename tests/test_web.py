"""Web app tests: login, sessions, headers, report pages, shared files."""
import pytest

import omen

testclient = pytest.importorskip("fastapi.testclient")
pytest.importorskip("httpx")


@pytest.fixture
def client():
    return testclient.TestClient(omen.app)


def log_in(c):
    assert c.post("/login", json={"text": omen.PIN}).status_code == 200


def test_anonymous_visitors_are_locked_out(client):
    assert "PIN" in client.get("/").text
    assert client.post("/chat", json={"text": "hi"}).status_code == 401
    assert client.get("/report/x.md").status_code == 200  # shows the PIN screen, not the report
    assert "PIN" in client.get("/report/x.md").text


def test_login_logout_and_session_storage(client):
    assert client.post("/login", json={"text": "wrong-pin"}).status_code == 401
    log_in(client)
    token = client.cookies.get("omen")
    assert token and token != omen.PIN
    assert omen._hash(token) in omen.sessions and token not in omen.SESS_FILE.read_text()
    assert 'id="stage"' in client.get("/").text
    client.post("/logout")
    assert client.post("/chat", json={"text": "hi"}).status_code == 401


def test_repeated_wrong_pins_lock_the_login(client):
    for _ in range(5):
        client.post("/login", json={"text": "bad"})
    assert client.post("/login", json={"text": omen.PIN}).status_code == 429


def test_security_headers(client):
    r = client.get("/")
    assert r.headers["X-Frame-Options"] == "DENY" and "Content-Security-Policy" in r.headers


def test_camera_is_refused_when_disabled(client):
    log_in(client)
    assert "off" in client.post("/action", json={"tool": "camera_snapshot"}).json()["body"]
    assert ".cam{display:none}" in client.get("/").text


def test_report_pages_and_path_traversal(client):
    (omen.REPORTS / "20260101-000000.md").write_text("# Title\n\nHello", encoding="utf-8")
    log_in(client)
    assert client.get("/report/20260101-000000.md").status_code == 200
    assert client.get("/report/20260101-000000.md/docx").status_code in (200, 501)
    assert client.get("/report/..%2Fconfig.json").status_code == 404
    assert client.get("/report/config.json").status_code == 404


def test_shared_file_links(client, fresh):
    f = fresh / "Desktop" / "a.txt"
    f.write_text("hello")
    tok = omen.send_file(str(f)).split("|")[1]
    assert "PIN" in client.get(f"/file/{tok}").text  # locked until login
    log_in(client)
    assert client.get(f"/file/{tok}").content == b"hello"
    assert client.get("/file/not-a-real-token").status_code == 404
