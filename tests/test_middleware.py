from __future__ import annotations

import re

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from structlog.contextvars import get_contextvars

from app.middleware import CorrelationIdMiddleware


def _make_app() -> FastAPI:
    test_app = FastAPI()
    test_app.add_middleware(CorrelationIdMiddleware)

    @test_app.get("/context")
    async def context(request: Request) -> dict[str, str]:
        values = get_contextvars()
        return {
            "request_state": request.state.correlation_id,
            "contextvar": values["correlation_id"],
        }

    @test_app.get("/context-after")
    async def context_after() -> dict[str, bool]:
        return {"has_correlation_id": "correlation_id" in get_contextvars()}

    return test_app


def test_middleware_preserves_request_id_and_returns_timing_header() -> None:
    with TestClient(_make_app()) as client:
        response = client.get("/context", headers={"x-request-id": "req-client-123"})

    assert response.status_code == 200
    assert response.json() == {
        "request_state": "req-client-123",
        "contextvar": "req-client-123",
    }
    assert response.headers["x-request-id"] == "req-client-123"
    assert float(response.headers["x-response-time-ms"]) >= 0


def test_middleware_generates_request_id_and_clears_context_between_requests() -> None:
    with TestClient(_make_app()) as client:
        first = client.get("/context")
        second = client.get("/context-after")

    assert re.fullmatch(r"req-[0-9a-f]{8}", first.json()["contextvar"])
    assert first.headers["x-request-id"] == first.json()["contextvar"]
    assert second.json() == {"has_correlation_id": True}
    assert "correlation_id" not in get_contextvars()
