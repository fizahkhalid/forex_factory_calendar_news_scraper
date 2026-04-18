import tempfile
import unittest
from pathlib import Path

from ff_calendar_toolkit.alerts.state import AlertStateStore


class AlertStateTests(unittest.TestCase):
    def test_state_tracks_sent_and_failures(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = AlertStateStore(Path(temp_dir))
            state = store.load()

            store.mark_failure(state, "key1", "discord_main", "boom")
            self.assertIn("key1|discord_main", state["failures"])

            store.mark_sent(
                state,
                "key1",
                "discord_main",
                {"rule": "usd-cpi", "event": "Core CPI"},
            )
            self.assertTrue(store.is_sent(state, "key1", "discord_main"))
            self.assertNotIn("key1|discord_main", state["failures"])

            store.save(state)
            reloaded = store.load()
            self.assertTrue(store.is_sent(reloaded, "key1", "discord_main"))


if __name__ == "__main__":
    unittest.main()
