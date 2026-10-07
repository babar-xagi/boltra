"""End-to-end HTTP, OpenAPI, settings, and repeated-reload verification."""

from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from boltra.apps import add_app
from boltra.project.generator import create_project


@pytest.mark.integration
def test_dev_server_serves_routes(tmp_path: Path) -> None:
    """``boltra dev`` serves ``/`` and ``/docs`` (Phase 3 exit criteria)."""
    if shutil_which("uv") is None:
        pytest.skip("uv not installed")

    create_project("demo", cwd=tmp_path)
    project = tmp_path / "demo"
    add_app("students", cwd=project)
    add_app("courses", cwd=project)
    port = _unused_port()
    pyproject = project / "pyproject.toml"
    source = pyproject.read_text(encoding="utf-8")
    pyproject.write_text(
        source.replace("port = 8000", f"port = {port}"), encoding="utf-8"
    )
    (project / ".env").write_text(
        "API_TITLE=Integration API\nSECRET_KEY=integration-secret\nDEBUG=false\n",
        encoding="utf-8",
    )

    sync = subprocess.run(
        ["uv", "sync", "--python", sys.executable],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )
    assert sync.returncode == 0, f"uv sync failed: {sync.stderr}"

    command = [
        sys.executable,
        "-c",
        "from boltra.dev.server import run_dev_server; "
        "raise SystemExit(run_dev_server())",
    ]
    log_path = tmp_path / "server.log"
    server_log = log_path.open("w", encoding="utf-8")
    popen_kwargs: dict[str, object] = {
        "cwd": project,
        "stdout": server_log,
        "stderr": subprocess.STDOUT,
    }
    if sys.platform == "win32":
        # Uvicorn reload needs a console for CTRL_C_EVENT on Windows. Keep it
        # hidden and separate from pytest so reload signals cannot interrupt it.
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
        popen_kwargs["startupinfo"] = startupinfo
    else:
        popen_kwargs["start_new_session"] = True

    proc = subprocess.Popen(command, **popen_kwargs)

    try:
        _wait_for_url(f"http://127.0.0.1:{port}/", timeout=30.0)
        _wait_for_url(f"http://127.0.0.1:{port}/docs", timeout=5.0)
        _wait_for_json(
            f"http://127.0.0.1:{port}/",
            {"message": "Hello from FastAPI + Boltra Kit"},
        )
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/openapi.json"
        ) as response:
            schema = json.load(response)
        assert schema["info"]["title"] == "Integration API"
        assert "/" in schema["paths"]
        for name in ("students", "courses"):
            _wait_for_json(
                f"http://127.0.0.1:{port}/{name}/", {"app": name, "status": "ok"}
            )
            assert schema["paths"][f"/{name}/"]["get"]["tags"] == [name]

        # Adding an app while dev is running must reload into a reachable route.
        add_app("teachers", cwd=project)
        _wait_for_json(
            f"http://127.0.0.1:{port}/teachers/", {"app": "teachers", "status": "ok"}
        )

        main = project / "main.py"
        source = main.read_text(encoding="utf-8")
        for message in ["First reload verified", "Second reload verified"]:
            main.write_text(
                source.replace("Hello from FastAPI + Boltra Kit", message),
                encoding="utf-8",
            )
            _wait_for_json(f"http://127.0.0.1:{port}/", {"message": message})
    finally:
        _stop_process_tree(proc)
        server_log.close()
        print(log_path.read_text(encoding="utf-8", errors="replace"))


def shutil_which(cmd: str) -> str | None:
    """Thin wrapper to avoid importing shutil at module level in skip helper."""
    import shutil

    return shutil.which(cmd)


def _wait_for_url(url: str, *, timeout: float) -> None:
    """Poll ``url`` until HTTP 200 or timeout."""
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            time.sleep(0.5)
    msg = f"timed out waiting for {url}"
    if last_error is not None:
        msg = f"{msg}: {last_error}"
    raise AssertionError(msg)


def _unused_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_json(url: str, expected: dict[str, str]) -> None:
    """Wait for a specific response, including across Uvicorn reloads."""
    deadline = time.monotonic() + 15.0
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if json.load(response) == expected:
                    return
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(0.25)
    pytest.fail(f"{url} did not return {expected!r}")


def _stop_process_tree(proc: subprocess.Popen[bytes]) -> None:
    if proc.poll() is not None:
        return

    if sys.platform == "win32":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        os.killpg(proc.pid, signal.SIGTERM)

    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=10)
