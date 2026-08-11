from __future__ import annotations

import json
import asyncio
from pathlib import Path

from starlette.requests import Request
from fastapi.testclient import TestClient

from app import logging_config
from app.main import app, generic_exception_handler


def test_chat_response_log_exposes_quality_for_dashboard(
    monkeypatch, tmp_path: Path
) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={
                "user_id": "student-01",
                "session_id": "session-01",
                "feature": "qa",
                "message": "Explain observability",
            },
        )

    assert response.status_code == 200
    events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    response_event = next(event for event in events if event["event"] == "response_sent")
    assert response_event["quality_score"] == response.json()["quality_score"]


def test_generic_exception_handler_returns_correlation_id_header() -> None:
    request = Request({"type": "http", "method": "GET", "path": "/boom", "headers": []})
    request.state.correlation_id = "req-test-500"

    response = asyncio.run(generic_exception_handler(request, RuntimeError("boom")))

    assert response.status_code == 500
    assert response.headers["x-request-id"] == "req-test-500"
    assert response.body == b'{"detail":"RuntimeError"}'
