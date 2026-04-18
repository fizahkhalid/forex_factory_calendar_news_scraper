import json
import tempfile
import unittest
from pathlib import Path

from ff_calendar_toolkit.models import ScrapeContext
from ff_calendar_toolkit.storage import FileOutputStore


class StorageTests(unittest.TestCase):
    def test_file_output_store_writes_last_run_monthly_and_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            store = FileOutputStore(tmp_path)
            context = ScrapeContext(
                month_param="this",
                month_name="April",
                month_slug="2026-04",
                year="2026",
                source_timezone="UTC",
                target_timezone="Asia/Karachi",
                scraped_at="2026-04-19T00:00:00+00:00",
            )
            records = [
                {
                    "time": "08:00",
                    "timezone": "Asia/Karachi",
                    "currency": "USD",
                    "impact": "red",
                    "event": "NFP",
                    "detail": "url",
                    "actual": "1",
                    "forecast": "2",
                    "previous": "3",
                    "day": "Tue",
                    "date": "02/04/2026",
                    "scraped_at": "2026-04-19T00:00:00+00:00",
                }
            ]

            store.begin_run("both")
            result = store.write(records, context, "both")

            self.assertEqual(len(result.last_run_paths), 2)
            self.assertTrue((tmp_path / "last_run" / "2026-04.csv").exists())
            self.assertTrue((tmp_path / "last_run" / "2026-04.json").exists())
            self.assertTrue((tmp_path / "monthly" / "2026-04.csv").exists())
            self.assertTrue((tmp_path / "monthly" / "2026-04.json").exists())
            self.assertTrue(
                any(path.parent.name == "2026-04" for path in result.history_paths)
            )

            payload = json.loads((tmp_path / "last_run" / "2026-04.json").read_text(encoding="utf-8"))
            self.assertEqual(payload[0]["event"], "NFP")
            self.assertEqual(payload[0]["timezone"], "Asia/Karachi")


if __name__ == "__main__":
    unittest.main()
