#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from types import SimpleNamespace

import uvicorn
from fastapi import FastAPI, Query, Request

from ff_calendar_toolkit.alerts.events import load_alert_events
from ff_calendar_toolkit.alerts.service import preview_alerts
from ff_calendar_toolkit.runtime import (
    build_alert_options,
    build_view_options,
    load_env_file,
    resolve_config_path,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local FastAPI for Forex Factory Toolkit data")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", type=int, default=8765, help="Bind port")
    parser.add_argument("--config", help="Path to config.yaml")
    return parser


def build_context(config_value: str | None):
    config_path = resolve_config_path(config_value)
    load_env_file(config_path)
    args = SimpleNamespace(
        config=str(config_path),
        output_dir=None,
        rules_dir=None,
        state_dir=None,
        host=None,
        port=None,
    )
    return {
        "config_path": config_path,
        "view_options": build_view_options(args),
        "alert_options": build_alert_options(args),
    }


def build_app(config_value: str | None = None) -> FastAPI:
    context = build_context(config_value)
    app = FastAPI(title="Forex Factory Toolkit Local API", version="1.0.0")
    webhook_store = context["view_options"].output_dir.parent / "state" / "local_api"
    webhook_store.mkdir(parents=True, exist_ok=True)
    webhook_log_path = webhook_store / "webhook_requests.json"

    def append_webhook_record(record: dict) -> None:
        if webhook_log_path.exists():
            payload = json.loads(webhook_log_path.read_text(encoding="utf-8"))
        else:
            payload = []
        payload.append(record)
        webhook_log_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/datasets")
    def datasets():
        output_dir = context["view_options"].output_dir
        return {
            "last_run": [path.name for path in sorted((output_dir / "last_run").glob("*.json"))],
            "monthly": [path.name for path in sorted((output_dir / "monthly").glob("*.json"))],
            "history": [
                str(path.relative_to(output_dir))
                for path in sorted((output_dir / "history").rglob("*.json"))
            ],
        }

    @app.get("/events")
    def events(
        currency: str | None = None,
        impact: str | None = None,
        keyword: str | None = None,
        day: str | None = None,
        month: str | None = None,
        limit: int = Query(default=100, ge=1, le=5000),
    ):
        filtered = _upcoming_events(context["view_options"].output_dir, 5000)
        if month:
            filtered = [
                event
                for event in filtered
                if event.get("date", "").endswith(f"/{month[5:7]}/{month[:4]}")
            ]
        if currency:
            filtered = [
                event for event in filtered if event.get("currency", "").upper() == currency.upper()
            ]
        if impact:
            filtered = [
                event for event in filtered if event.get("impact", "").lower() == impact.lower()
            ]
        if keyword:
            filtered = [
                event for event in filtered if keyword.lower() in event.get("event", "").lower()
            ]
        if day:
            filtered = [event for event in filtered if event.get("day", "").lower() == day[:3].lower()]
        return filtered[:limit]

    @app.get("/events/upcoming")
    def events_upcoming(limit: int = Query(default=20, ge=1, le=5000)):
        return _upcoming_events(context["view_options"].output_dir, limit)

    @app.get("/alerts/preview")
    def alerts_preview():
        return preview_alerts(context["alert_options"])

    @app.post("/webhook-test")
    async def webhook_test(request: Request):
        body = await request.json()
        record = {
            "headers": dict(request.headers),
            "body": body,
        }
        append_webhook_record(record)
        return {"status": "received", "saved_to": str(webhook_log_path)}

    @app.get("/webhook-test/received")
    def webhook_test_received():
        if not webhook_log_path.exists():
            return []
        return json.loads(webhook_log_path.read_text(encoding="utf-8"))

    return app


def _upcoming_events(output_dir: Path, limit: int) -> list[dict]:
    events = []
    for event in load_alert_events(output_dir):
        payload = dict(event.payload)
        payload["event_time"] = event.event_time.isoformat()
        payload["event_id"] = event.event_id
        events.append(payload)
    return events[:limit]


def main():
    args = build_parser().parse_args()
    app = build_app(args.config)
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
