import argparse
import os
import subprocess
import sys
from pathlib import Path

from .config import DEFAULT_VIEWER_HOST, DEFAULT_VIEWER_PORT
from .console import AppConsole
from .runtime import (
    build_alert_options,
    build_run_options,
    build_view_options,
    current_alert_schedule,
    current_schedule,
    load_env_file,
    resolve_config_path,
)
from .scheduler import resolve_alert_schedule, resolve_schedule


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Professional local-first Forex Factory calendar toolkit."
    )
    subparsers = parser.add_subparsers(dest="command")

    scrape = subparsers.add_parser("scrape", help="Run the scraper and write output files")
    scrape.add_argument("--config", help="Path to YAML config file")
    scrape.add_argument("--months", nargs="+", help="Month selectors such as this next")
    scrape.add_argument(
        "--format",
        dest="output_format",
        choices=["csv", "json", "both"],
        help="Output format to write",
    )
    scrape.add_argument("--output-dir", help="Directory for generated artifacts")
    scrape.add_argument("--timezone", help="Target timezone for converted event times")
    scrape.add_argument(
        "--currencies",
        nargs="+",
        help="Allowed currencies, for example USD EUR GBP CAD",
    )
    scrape.add_argument(
        "--impacts",
        nargs="+",
        help="Allowed impact levels, for example red orange gray",
    )
    scrape.add_argument(
        "--show-browser",
        action="store_true",
        help="Run with a visible browser instead of headless mode",
    )

    view = subparsers.add_parser("view", help="Launch the local Streamlit viewer")
    view.add_argument("--config", help="Path to YAML config file")
    view.add_argument("--output-dir", help="Directory containing generated artifacts")
    view.add_argument("--host", help=f"Viewer host, defaults to {DEFAULT_VIEWER_HOST}")
    view.add_argument("--port", type=int, help=f"Viewer port, defaults to {DEFAULT_VIEWER_PORT}")

    alerts = subparsers.add_parser("alerts-check", help="Evaluate rules and send alert notifications")
    alerts.add_argument("--config", help="Path to YAML config file")
    alerts.add_argument("--output-dir", help="Directory containing generated artifacts")
    alerts.add_argument("--rules-dir", help="Directory containing alert rule YAML files")
    alerts.add_argument("--state-dir", help="Directory for alert state")

    test_notify = subparsers.add_parser(
        "test-notify", help="Send a test message to all enabled connectors"
    )
    test_notify.add_argument("--config", help="Path to YAML config file")
    test_notify.add_argument("--output-dir", help="Directory containing generated artifacts")
    test_notify.add_argument("--rules-dir", help="Directory containing alert rule YAML files")
    test_notify.add_argument("--state-dir", help="Directory for alert state")

    schedule_info = subparsers.add_parser(
        "schedule-info", help="Print the effective cron expression"
    )
    schedule_info.add_argument("--config", help="Path to YAML config file")
    alert_schedule_info = subparsers.add_parser(
        "alerts-schedule-info", help="Print the effective alert cron expression"
    )
    alert_schedule_info.add_argument("--config", help="Path to YAML config file")
    return parser


def _prepare_args(argv: list[str] | None) -> list[str]:
    args = list(argv) if argv is not None else sys.argv[1:]
    if not args or args[0] not in {"scrape", "view", "alerts-check", "schedule-info", "alerts-schedule-info", "test-notify"}:
        return ["scrape", *args]
    return args


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(_prepare_args(argv))
    console = AppConsole()
    config_path = resolve_config_path(getattr(args, "config", None))
    env_path = load_env_file(config_path)
    if env_path.exists() and args.command not in {"schedule-info", "alerts-schedule-info"}:
        console.step(f"Loaded environment secrets from {env_path}")

    if args.command == "view":
        return run_viewer(console, args)

    if args.command == "schedule-info":
        cron_expression, preset = current_schedule(getattr(args, "config", None))
        print(resolve_schedule(preset, cron_expression))
        return 0

    if args.command == "alerts-schedule-info":
        cron_expression, preset = current_alert_schedule(getattr(args, "config", None))
        print(resolve_alert_schedule(preset, cron_expression))
        return 0

    if args.command == "test-notify":
        options = build_alert_options(args)
        from .alerts.notifiers import NotificationError, NotifierFactory

        factory = NotifierFactory(options)
        ids = factory.connector_ids()
        if not ids:
            console.step("No connectors are enabled. Enable at least one in config.yaml.")
            return 0
        all_ok = True
        for connector_id in ids:
            try:
                factory.send_raw(connector_id, "ff-calendar-toolkit: test notification — your setup is working.")
                console.step(f"ok  {connector_id}")
            except NotificationError as exc:
                console.error(f"fail  {connector_id}: {exc}")
                all_ok = False
        return 0 if all_ok else 1

    if args.command == "alerts-check":
        options = build_alert_options(args)
        from .alerts.service import AlertService

        return AlertService(console).run(options)

    options = build_run_options(args)
    from .service import ScrapeService

    return ScrapeService(console).run(options)


def run_viewer(console: AppConsole, args) -> int:
    options = build_view_options(args)
    env = os.environ.copy()
    env["FF_CONFIG_PATH"] = str(options.config_path)
    env["FF_VIEWER_OUTPUT_DIR"] = str(options.output_dir)
    env["FF_ALERT_RULES_DIR"] = str(options.rules_dir)
    env["FF_ALERT_STATE_DIR"] = str(options.state_dir)
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(Path(__file__).resolve().parent / "viewer.py"),
        "--server.address",
        options.host,
        "--server.port",
        str(options.port),
    ]
    console.step(f"Launching viewer on http://{options.host}:{options.port}")
    try:
        return subprocess.call(command, env=env)
    except FileNotFoundError:
        console.error("Streamlit is not installed. Install requirements and try again.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
