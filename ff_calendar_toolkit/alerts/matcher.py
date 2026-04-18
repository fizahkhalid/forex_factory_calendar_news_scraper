from datetime import datetime, timedelta

from .models import AlertEvent, AlertPreview, AlertRule


def build_dedup_key(rule: AlertRule, event: AlertEvent) -> str:
    trigger_at = event.event_time - timedelta(
        minutes=int(rule.trigger.get("minutes_before", 10))
    )
    return f"{rule.rule_id}|{event.event_id}|{trigger_at.isoformat()}"


def event_matches_rule(rule: AlertRule, event: AlertEvent) -> bool:
    if not rule.enabled:
        return False

    payload = event.payload
    match = rule.match

    currencies = _lower_list(match.get("currencies"))
    impacts = _lower_list(match.get("impacts"))
    event_names = _lower_list(match.get("event_names"))
    event_keywords = _lower_list(match.get("event_keywords"))
    weekdays = _weekday_list(match.get("weekdays"))

    event_name = str(payload.get("event", "")).strip()
    event_name_lower = event_name.lower()

    if currencies and payload.get("currency", "").lower() not in currencies:
        return False
    if impacts and payload.get("impact", "").lower() not in impacts:
        return False
    if event_names and event_name_lower not in event_names:
        return False
    if event_keywords and not any(keyword in event_name_lower for keyword in event_keywords):
        return False
    if weekdays and event.event_time.strftime("%a") not in weekdays:
        return False
    return True


def event_should_trigger(
    rule: AlertRule, event: AlertEvent, now: datetime, check_interval_minutes: int
) -> bool:
    trigger_at = event.event_time - timedelta(
        minutes=int(rule.trigger.get("minutes_before", 10))
    )
    return trigger_at <= now < event.event_time


def preview_match(
    rule: AlertRule,
    event: AlertEvent,
    connector_id: str,
    status: str,
) -> AlertPreview:
    trigger_at = event.event_time - timedelta(
        minutes=int(rule.trigger.get("minutes_before", 10))
    )
    return AlertPreview(
        dedup_key=build_dedup_key(rule, event),
        rule_id=rule.rule_id,
        rule_name=rule.name,
        connector_id=connector_id,
        event_id=event.event_id,
        event_name=event.payload.get("event", ""),
        currency=event.payload.get("currency", ""),
        impact=event.payload.get("impact", ""),
        trigger_at=trigger_at,
        event_time=event.event_time,
        timezone=event.payload.get("timezone", ""),
        status=status,
    )


def _lower_list(value) -> list[str]:
    if not value:
        return []
    return [str(item).strip().lower() for item in value if str(item).strip()]


def _weekday_list(value) -> list[str]:
    if not value:
        return []
    return [str(item).strip().title()[:3] for item in value if str(item).strip()]
