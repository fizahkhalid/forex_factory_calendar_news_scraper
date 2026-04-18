import tempfile
import unittest
from pathlib import Path

from ff_calendar_toolkit.alerts.rules import load_rules, save_rule


class AlertRuleTests(unittest.TestCase):
    def test_valid_rule_loads(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir)
            save_rule(
                rules_dir,
                {
                    "name": "usd-cpi",
                    "enabled": True,
                    "match": {"currencies": ["USD"], "impacts": ["red"], "event_keywords": ["CPI"]},
                    "trigger": {"minutes_before": 10},
                    "deliver": ["discord_main"],
                },
                "usd-cpi.yaml",
            )

            rules = load_rules(rules_dir)

            self.assertEqual(len(rules), 1)
            self.assertEqual(rules[0].rule_id, "usd-cpi")

    def test_invalid_rule_raises(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "broken.yaml"
            path.write_text("name: broken\ndeliver: []\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                load_rules(Path(temp_dir))


if __name__ == "__main__":
    unittest.main()
