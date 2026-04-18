from datetime import datetime, timezone

from ff_calendar_toolkit.console import AppConsole
from ff_calendar_toolkit.models import AlertOptions

from .events import load_alert_events
from .matcher import build_dedup_key, event_matches_rule, event_should_trigger, preview_match
from .notifiers import NotificationError, NotifierFactory
from .rules import load_rules
from .state import AlertStateStore


class AlertService:
    def __init__(self, console: AppConsole | None = None) -> None:
        self.console = console or AppConsole()

    def run(self, options: AlertOptions) -> int:
        state_store = AlertStateStore(options.state_dir)
        state = state_store.load()
        rules = load_rules(options.rules_dir)
        events = load_alert_events(options.output_dir)
        notifier_factory = NotifierFactory(options)
        now = datetime.now(timezone.utc)

        self.console.step(
            f"Loaded {len(rules)} rules, {len(events)} events, and {len(notifier_factory.connector_ids())} enabled connectors"
        )

        triggered = 0
        delivered = 0
        for rule in rules:
            if not rule.enabled:
                self.console.warn(f"Skipping disabled rule '{rule.name}'")
                continue

            for event in events:
                if not event_matches_rule(rule, event):
                    continue
                if not event_should_trigger(rule, event, now, options.check_interval_minutes):
                    continue

                triggered += 1
                dedup_key = build_dedup_key(rule, event)
                for connector_id in rule.deliver:
                    preview = preview_match(
                        rule,
                        event,
                        connector_id,
                        "queued",
                    )
                    preview_payload = {
                        "rule": preview.rule_name,
                        "event": preview.event_name,
                        "currency": preview.currency,
                        "impact": preview.impact,
                        "trigger_at": preview.trigger_at.isoformat(),
                        "connector": connector_id,
                    }
                    if state_store.is_sent(state, dedup_key, connector_id):
                        continue
                    try:
                        notifier_factory.send(connector_id, rule, event)
                        state_store.mark_sent(state, dedup_key, connector_id, preview_payload)
                        delivered += 1
                        self.console.success(
                            f"Sent alert for '{rule.name}' via {connector_id}: {event.payload.get('event', '')}"
                        )
                    except NotificationError as exc:
                        state_store.mark_failure(state, dedup_key, connector_id, str(exc))
                        self.console.warn(
                            f"Failed to send alert for '{rule.name}' via {connector_id}: {exc}"
                        )

        state_store.save(state)
        self.console.success(
            f"Alert check complete: {triggered} trigger matches evaluated, {delivered} notifications delivered"
        )
        return 0


def preview_alerts(options: AlertOptions) -> list[dict]:
    rules = load_rules(options.rules_dir)
    events = load_alert_events(options.output_dir)
    state_store = AlertStateStore(options.state_dir)
    state = state_store.load()
    now = datetime.now(timezone.utc)
    previews = []

    for rule in rules:
        if not rule.enabled:
            continue
        for event in events:
            if not event_matches_rule(rule, event):
                continue

            dedup_key = build_dedup_key(rule, event)
            triggered = event_should_trigger(rule, event, now, options.check_interval_minutes)
            if event.event_time < now.astimezone(event.event_time.tzinfo):
                status = "past"
            elif triggered:
                status = "due"
            else:
                status = "upcoming"

            for connector_id in rule.deliver:
                if state_store.is_sent(state, dedup_key, connector_id):
                    connector_status = "sent"
                else:
                    connector_status = status
                preview = preview_match(rule, event, connector_id, connector_status)
                previews.append(
                    {
                        "rule": preview.rule_name,
                        "connector": connector_id,
                        "event": preview.event_name,
                        "currency": preview.currency,
                        "impact": preview.impact,
                        "trigger_at": preview.trigger_at.isoformat(),
                        "event_time": preview.event_time.isoformat(),
                        "timezone": preview.timezone,
                        "status": connector_status,
                    }
                )
    return sorted(previews, key=lambda item: (item["trigger_at"], item["rule"], item["connector"]))
