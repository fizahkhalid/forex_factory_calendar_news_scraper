import os
import tempfile
import unittest
from pathlib import Path

from ff_calendar_toolkit.runtime import build_alert_options, build_run_options


class Args:
    config = None
    months = None
    output_format = None
    output_dir = None
    rules_dir = None
    state_dir = None
    timezone = None
    currencies = None
    impacts = None
    show_browser = False


class RuntimeTests(unittest.TestCase):
    def test_cli_options_override_environment(self):
        previous = dict(os.environ)
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                config_path = Path(temp_dir) / "config.yaml"
                config_path.write_text(
                    "\n".join(
                        [
                            "months:",
                            "  - this",
                            "output_format: both",
                            "output_dir: yaml-news",
                            "timezone: Europe/London",
                        ]
                    ),
                    encoding="utf-8",
                )
                os.environ["FF_MONTHS"] = "this next"
                os.environ["FF_OUTPUT_FORMAT"] = "json"
                os.environ["FF_OUTPUT_DIR"] = os.path.join(temp_dir, "env-news")
                os.environ["FF_TARGET_TIMEZONE"] = "UTC"

                args = Args()
                args.config = str(config_path)
                args.months = ["next"]
                args.output_format = "csv"
                args.output_dir = os.path.join(temp_dir, "cli-news")
                args.timezone = "Asia/Karachi"

                options = build_run_options(args)

                self.assertEqual(options.months, ["next"])
                self.assertEqual(options.output_format, "csv")
                self.assertTrue(str(options.output_dir).endswith("cli-news"))
                self.assertEqual(options.target_timezone, "Asia/Karachi")
                self.assertEqual(options.config_path, config_path)
        finally:
            os.environ.clear()
            os.environ.update(previous)

    def test_yaml_config_is_used_when_env_and_cli_are_absent(self):
        previous = dict(os.environ)
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                config_path = Path(temp_dir) / "config.yaml"
                config_path.write_text(
                    "\n".join(
                        [
                            "months:",
                            "  - next",
                            "output_format: json",
                            "output_dir: yaml-news",
                            "timezone: UTC",
                            "allowed_currencies:",
                            "  - USD",
                            "allowed_impacts:",
                            "  - red",
                        ]
                    ),
                    encoding="utf-8",
                )

                args = Args()
                args.config = str(config_path)

                options = build_run_options(args)

                self.assertEqual(options.months, ["next"])
                self.assertEqual(options.output_format, "json")
                self.assertTrue(str(options.output_dir).endswith("yaml-news"))
                self.assertEqual(options.target_timezone, "UTC")
                self.assertEqual(options.allowed_currencies, ["USD"])
        finally:
            os.environ.clear()
            os.environ.update(previous)

    def test_alert_options_load_from_yaml(self):
        previous = dict(os.environ)
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                config_path = Path(temp_dir) / "config.yaml"
                config_path.write_text(
                    "\n".join(
                        [
                            "output_dir: news",
                            "alerts:",
                            "  rules_dir: rules",
                            "  state_dir: state/alerts",
                            "  check_interval_minutes: 5",
                            "  schedule_preset: every_5_minutes",
                            "  connectors:",
                            "    - id: discord_main",
                            "      type: discord",
                            "      enabled: true",
                            "      webhook_url_env: DISCORD_WEBHOOK_URL",
                        ]
                    ),
                    encoding="utf-8",
                )

                args = Args()
                args.config = str(config_path)
                args.rules_dir = None
                args.state_dir = None

                options = build_alert_options(args)

                self.assertEqual(options.check_interval_minutes, 5)
                self.assertEqual(options.schedule_preset, "every_5_minutes")
                self.assertEqual(options.connectors[0].connector_id, "discord_main")
        finally:
            os.environ.clear()
            os.environ.update(previous)


if __name__ == "__main__":
    unittest.main()
