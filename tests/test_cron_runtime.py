from datetime import datetime
import unittest

from ff_calendar_toolkit.cron_runtime import cron_matches, seconds_until_next_minute


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


if __name__ == "__main__":
    unittest.main()
