import unittest
from datetime import datetime, timedelta

import pytz

from ff_calendar_toolkit.alerts.matcher import build_dedup_key, event_matches_rule, event_should_trigger
from ff_calendar_toolkit.alerts.models import AlertEvent, AlertRule


class AlertMatchingTests(unittest.TestCase):
    def setUp(self):
        timezone = pytz.timezone("Asia/Karachi")
        self.event = AlertEvent(
            event_id="01/04/2026|08:30|USD|Core CPI|red",
            event_time=timezone.localize(datetime(2026, 4, 1, 8, 30)),
            payload={
                "currency": "USD",
                "impact": "red",
                "event": "Core CPI",
                "timezone": "Asia/Karachi",
                "date": "01/04/2026",
                "time": "08:30",
            },
        )
        self.rule = AlertRule(
            rule_id="usd-cpi",
            name="usd-cpi",
            enabled=True,
            match={
                "currencies": ["USD"],
                "impacts": ["red"],
                "event_names": [],
                "event_keywords": ["CPI"],
                "weekdays": ["Wed"],
            },
            trigger={"minutes_before": 10},
            deliver=["discord_main"],
            path="rules/usd-cpi.yaml",
        )

    def test_event_matches_rule(self):
        self.assertTrue(event_matches_rule(self.rule, self.event))

    def test_event_should_trigger_in_window(self):
        now = self.event.event_time - timedelta(minutes=8)
        self.assertTrue(event_should_trigger(self.rule, self.event, now, 5))

    def test_build_dedup_key_is_deterministic(self):
        key = build_dedup_key(self.rule, self.event)
        self.assertIn("usd-cpi", key)
        self.assertIn("Core CPI", key)


if __name__ == "__main__":
    unittest.main()
