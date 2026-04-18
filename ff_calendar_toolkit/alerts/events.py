import json
from datetime import datetime
from pathlib import Path

import pytz

from .models import AlertEvent


def event_identity(record: dict) -> str:
    parts = [
        record.get("date", ""),
        record.get("time", ""),
        record.get("currency", ""),
        record.get("event", ""),
        record.get("impact", ""),
    ]
    return "|".join(parts)


def load_alert_events(output_dir: Path) -> list[AlertEvent]:
    records = {}
    for path in sorted((output_dir / "monthly").glob("*.json")):
        for event in _events_from_file(path):
            records[event.event_id] = event
    for path in sorted((output_dir / "last_run").glob("*.json")):
        for event in _events_from_file(path):
            records[event.event_id] = event
    return sorted(records.values(), key=lambda event: event.event_time)


def _events_from_file(path: Path) -> list[AlertEvent]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    events = []
    for record in payload:
        try:
            event_time = _parse_event_time(record)
        except Exception:
            event_time = None
        if event_time is None:
            continue
        events.append(
            AlertEvent(
                event_id=event_identity(record),
                event_time=event_time,
                payload=record,
            )
        )
    return events


def _parse_event_time(record: dict) -> datetime | None:
    date_value = record.get("date", "").strip()
    time_value = record.get("time", "").strip()
    timezone_value = record.get("timezone", "").strip()

    if not date_value or not time_value or not timezone_value:
        return None
    if time_value.lower() in {"all day", "tentative"}:
        return None

    naive = datetime.strptime(f"{date_value} {time_value}", "%d/%m/%Y %H:%M")
    timezone = pytz.timezone(timezone_value)
    return timezone.localize(naive)
