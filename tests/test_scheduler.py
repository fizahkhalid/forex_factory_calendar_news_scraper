import unittest

from ff_calendar_toolkit.scheduler import resolve_alert_schedule, resolve_schedule


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
