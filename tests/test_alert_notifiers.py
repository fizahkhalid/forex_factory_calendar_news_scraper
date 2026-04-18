import os
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytz

from ff_calendar_toolkit.alerts.models import AlertEvent, AlertRule
from ff_calendar_toolkit.alerts.notifiers import NotifierFactory, render_message
from ff_calendar_toolkit.models import AlertConnector, AlertOptions


class AlertNotifierTests(unittest.TestCase):
    def setUp(self):
        self.options = AlertOptions(
            config_path=Path("config.yaml"),
            output_dir=Path("news"),
            rules_dir=Path("rules"),
            state_dir=Path("state/alerts"),
            check_interval_minutes=5,
            schedule_preset="every_5_minutes",
            cron_schedule=None,
            retry_attempts=2,
            retry_backoff_seconds=0,
            message_prefix="Forex Alert",
            connectors=[
                AlertConnector(
                    connector_id="discord_main",
                    connector_type="discord",
                    enabled=True,
                    settings={"webhook_url_env": "DISCORD_WEBHOOK_URL"},
                ),
                AlertConnector(
                    connector_id="telegram_main",
                    connector_type="telegram",
                    enabled=True,
                    settings={
                        "bot_token_env": "TELEGRAM_BOT_TOKEN",
                        "chat_id_env": "TELEGRAM_CHAT_ID",
                    },
                ),
                AlertConnector(
                    connector_id="webhook_main",
                    connector_type="webhook",
                    enabled=True,
                    settings={"url_env": "ALERT_WEBHOOK_URL"},
                ),
            ],
        )
        self.rule = AlertRule(
            rule_id="usd-cpi",
            name="usd-cpi",
            enabled=True,
            match={},
            trigger={"minutes_before": 10},
            deliver=["discord_main"],
            path="rules/usd-cpi.yaml",
        )
        self.event = AlertEvent(
            event_id="event-1",
            event_time=pytz.timezone("Asia/Karachi").localize(datetime(2026, 4, 1, 8, 30)),
            payload={
                "event": "Core CPI",
                "currency": "USD",
                "impact": "red",
                "date": "01/04/2026",
                "time": "08:30",
                "timezone": "Asia/Karachi",
                "detail": "url",
            },
        )

    def test_render_message_contains_core_fields(self):
        message = render_message("Forex Alert", self.rule, self.event)
        self.assertIn("Core CPI", message)
        self.assertIn("USD", message)

    @patch("ff_calendar_toolkit.alerts.notifiers._perform_request")
    def test_webhook_payload_is_sent(self, perform_request):
        previous = dict(os.environ)
        try:
            os.environ["ALERT_WEBHOOK_URL"] = "https://example.com"
            factory = NotifierFactory(self.options)
            factory.send("webhook_main", self.rule, self.event)
            self.assertTrue(perform_request.called)
        finally:
            os.environ.clear()
            os.environ.update(previous)


if __name__ == "__main__":
    unittest.main()
