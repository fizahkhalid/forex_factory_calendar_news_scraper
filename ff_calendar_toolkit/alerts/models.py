from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AlertRule:
    rule_id: str
    name: str
    enabled: bool
    match: dict
    trigger: dict
    deliver: list[str]
    path: str


@dataclass(frozen=True)
class AlertEvent:
    event_id: str
    event_time: datetime
    payload: dict


@dataclass(frozen=True)
class AlertPreview:
    dedup_key: str
    rule_id: str
    rule_name: str
    connector_id: str
    event_id: str
    event_name: str
    currency: str
    impact: str
    trigger_at: datetime
    event_time: datetime
    timezone: str
    status: str
