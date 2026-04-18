import unittest

from ff_calendar_toolkit.normalize import convert_time_zone, normalize_rows


class NormalizeTests(unittest.TestCase):
    def test_normalize_rows_carries_dates_and_times(self):
        rows = [
            {"date": "Tue Sep 2", "time": "3:00am"},
            {
                "currency": "USD",
                "impact": "red",
                "event": "Test Event",
                "actual": "1",
                "forecast": "2",
                "previous": "3",
                "detail": "url",
            },
            {"time": "empty", "currency": "EUR", "impact": "orange", "event": "Second Event"},
        ]

        normalized = normalize_rows(
            rows,
            "2025",
            "UTC",
            "Asia/Karachi",
            ["USD", "EUR"],
            ["red", "orange"],
        )

        self.assertEqual(len(normalized), 2)
        self.assertEqual(normalized[0]["date"], "02/09/2025")
        self.assertEqual(normalized[0]["day"], "Tue")
        self.assertEqual(normalized[0]["time"], "08:00")
        self.assertEqual(normalized[1]["time"], "08:00")

    def test_convert_time_zone_handles_special_values(self):
        self.assertEqual(
            convert_time_zone("02/09/2025", "all day", "UTC", "Asia/Karachi"),
            "all day",
        )


if __name__ == "__main__":
    unittest.main()
