from datetime import datetime
import unittest

from ff_calendar_toolkit.cron_runtime import cron_matches, seconds_until_next_minute
from ff_calendar_toolkit.scheduler import resolve_alert_schedule, resolve_schedule


class CronRuntimeTests(unittest.TestCase):
    def test_matches_every_five_minutes(self):
        when = datetime.fromisoformat("2026-04-19T03:55:10+05:00")
        self.assertTrue(cron_matches("*/5 * * * *", when))
        self.assertFalse(cron_matches("*/5 * * * *", when.replace(minute=53)))

    def test_matches_weekly_sunday_midnight(self):
        when = datetime.fromisoformat("2026-04-19T00:00:05+05:00")
        self.assertTrue(cron_matches("0 0 * * 0", when))
        self.assertFalse(cron_matches("0 0 * * 1", when))

    def test_seconds_until_next_minute(self):
        when = datetime.fromisoformat("2026-04-19T03:53:41+05:00")
        self.assertEqual(seconds_until_next_minute(when), 19)


class SchedulerTests(unittest.TestCase):
    def test_schedule_prefers_cron_expression(self):
        self.assertEqual(resolve_schedule("daily", "15 2 * * *"), "15 2 * * *")

    def test_schedule_uses_preset(self):
        self.assertEqual(resolve_schedule("monthly", None), "0 0 1 * *")

    def test_schedule_defaults_to_weekly(self):
        self.assertEqual(resolve_schedule(None, None), "0 0 * * 0")

    def test_alert_schedule_defaults_to_every_five_minutes(self):
        self.assertEqual(resolve_alert_schedule(None, None), "*/5 * * * *")


if __name__ == "__main__":
    unittest.main()
