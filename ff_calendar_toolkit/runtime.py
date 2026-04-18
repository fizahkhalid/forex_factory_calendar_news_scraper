import os
from pathlib import Path

import yaml

from .config import (
    DEFAULT_ALERT_CHECK_INTERVAL_MINUTES,
    DEFAULT_ALERT_MESSAGE_PREFIX,
    DEFAULT_ALERT_RETRY_ATTEMPTS,
    DEFAULT_ALERT_RETRY_BACKOFF_SECONDS,
    DEFAULT_ALERT_RULES_DIR,
    DEFAULT_ALERT_SCHEDULE_PRESET,
    DEFAULT_ALERT_STATE_DIR,
    DEFAULT_ALLOWED_CURRENCY_CODES,
    DEFAULT_ALLOWED_IMPACT_COLORS,
    DEFAULT_CONFIG_PATH,
    DEFAULT_ENV_PATH,
    DEFAULT_HEADLESS,
    DEFAULT_MONTHS,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_SCHEDULE_PRESET,
    DEFAULT_TARGET_TIMEZONE,
    DEFAULT_VIEWER_HOST,
    DEFAULT_VIEWER_PORT,
    ENV_KEYS,
)
from .models import AlertConnector, AlertOptions, RunOptions, ViewOptions


def _csv_values(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


def _space_values(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return list(default)
    return [item.strip() for item in value.split() if item.strip()]


def _bool_value(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.lower() not in {"0", "false", "no", "off"}


def _int_value(value: str | None, default: int) -> int:
    if value is None:
        return default
    return int(value)


def _config_relative_path(config_path: Path, value, default: Path) -> Path:
    raw_path = Path(str(value)) if value is not None else default
    if raw_path.is_absolute():
        return raw_path
    return (config_path.parent / raw_path).resolve()


def resolve_config_path(path_value: str | None = None) -> Path:
    return Path(path_value or os.getenv(ENV_KEYS["config_path"]) or DEFAULT_CONFIG_PATH)


def resolve_env_path(config_path: Path, env_path_value: str | None = None) -> Path:
    return Path(
        env_path_value
        or os.getenv(ENV_KEYS["env_path"])
        or config_path.parent / DEFAULT_ENV_PATH
    )


def load_env_file(config_path: Path | None = None, env_path_value: str | None = None) -> Path:
    resolved_config_path = config_path or resolve_config_path()
    env_path = resolve_env_path(resolved_config_path, env_path_value)
    if not env_path.exists():
        return env_path

    with open(env_path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)
    return env_path


def _load_yaml_config(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        return {}
    return loaded


def _yaml_list(value, default: list[str]) -> list[str]:
    if value is None:
        return list(default)
    if isinstance(value, str):
        return _space_values(value, default)
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return list(default)


def _alerts_config(yaml_config: dict) -> dict:
    alerts = yaml_config.get("alerts") or {}
    return alerts if isinstance(alerts, dict) else {}


def _connector_configs(alerts_config: dict) -> list[AlertConnector]:
    connectors = alerts_config.get("connectors") or []
    result = []
    if not isinstance(connectors, list):
        return result

    for connector in connectors:
        if not isinstance(connector, dict):
            continue
        connector_id = str(connector.get("id", "")).strip()
        connector_type = str(connector.get("type", "")).strip()
        if not connector_id or not connector_type:
            continue
        settings = {key: value for key, value in connector.items() if key not in {"id", "type", "enabled"}}
        result.append(
            AlertConnector(
                connector_id=connector_id,
                connector_type=connector_type,
                enabled=bool(connector.get("enabled", True)),
                settings=settings,
            )
        )
    return result


def build_run_options(args) -> RunOptions:
    config_path = resolve_config_path(getattr(args, "config", None))
    yaml_config = _load_yaml_config(config_path)

    yaml_months = _yaml_list(yaml_config.get("months"), DEFAULT_MONTHS)
    yaml_timezone = yaml_config.get("timezone", DEFAULT_TARGET_TIMEZONE)
    yaml_currencies = _yaml_list(
        yaml_config.get("allowed_currencies"), DEFAULT_ALLOWED_CURRENCY_CODES
    )
    yaml_impacts = _yaml_list(
        yaml_config.get("allowed_impacts"), DEFAULT_ALLOWED_IMPACT_COLORS
    )
    yaml_output_dir = _config_relative_path(
        config_path, yaml_config.get("output_dir"), DEFAULT_OUTPUT_DIR
    )
    yaml_output_format = yaml_config.get("output_format", DEFAULT_OUTPUT_FORMAT)
    yaml_headless = bool(yaml_config.get("headless", DEFAULT_HEADLESS))

    env_months = _space_values(os.getenv(ENV_KEYS["months"]), yaml_months)
    env_timezone = os.getenv(ENV_KEYS["timezone"], yaml_timezone)
    env_currencies = _csv_values(os.getenv(ENV_KEYS["currencies"]), yaml_currencies)
    env_impacts = _csv_values(os.getenv(ENV_KEYS["impacts"]), yaml_impacts)
    env_output_dir = Path(os.getenv(ENV_KEYS["output_dir"], str(yaml_output_dir)))
    env_output_format = os.getenv(ENV_KEYS["output_format"], yaml_output_format)
    env_headless = _bool_value(os.getenv(ENV_KEYS["headless"]), yaml_headless)

    return RunOptions(
        config_path=config_path,
        months=args.months if args.months else env_months,
        output_format=args.output_format or env_output_format,
        output_dir=Path(args.output_dir) if args.output_dir else env_output_dir,
        target_timezone=args.timezone if args.timezone is not None else env_timezone,
        allowed_currencies=args.currencies if args.currencies else env_currencies,
        allowed_impacts=args.impacts if args.impacts else env_impacts,
        headless=(not args.show_browser) if args.show_browser else env_headless,
    )


def build_view_options(args) -> ViewOptions:
    config_path = resolve_config_path(getattr(args, "config", None))
    yaml_config = _load_yaml_config(config_path)
    alerts_config = _alerts_config(yaml_config)

    yaml_output_dir = _config_relative_path(
        config_path, yaml_config.get("output_dir"), DEFAULT_OUTPUT_DIR
    )
    yaml_viewer_host = yaml_config.get("viewer_host", DEFAULT_VIEWER_HOST)
    yaml_viewer_port = int(yaml_config.get("viewer_port", DEFAULT_VIEWER_PORT))
    yaml_rules_dir = _config_relative_path(
        config_path, alerts_config.get("rules_dir"), DEFAULT_ALERT_RULES_DIR
    )
    yaml_state_dir = _config_relative_path(
        config_path, alerts_config.get("state_dir"), DEFAULT_ALERT_STATE_DIR
    )

    env_output_dir = Path(os.getenv(ENV_KEYS["output_dir"], str(yaml_output_dir)))
    env_viewer_host = os.getenv(ENV_KEYS["viewer_host"], yaml_viewer_host)
    env_viewer_port = int(os.getenv(ENV_KEYS["viewer_port"], str(yaml_viewer_port)))
    env_rules_dir = Path(os.getenv(ENV_KEYS["alert_rules_dir"], str(yaml_rules_dir)))
    env_state_dir = Path(os.getenv(ENV_KEYS["alert_state_dir"], str(yaml_state_dir)))

    return ViewOptions(
        config_path=config_path,
        output_dir=Path(args.output_dir) if args.output_dir else env_output_dir,
        rules_dir=env_rules_dir,
        state_dir=env_state_dir,
        host=args.host or env_viewer_host,
        port=args.port or env_viewer_port,
    )


def build_alert_options(args) -> AlertOptions:
    config_path = resolve_config_path(getattr(args, "config", None))
    yaml_config = _load_yaml_config(config_path)
    alerts_config = _alerts_config(yaml_config)

    yaml_output_dir = _config_relative_path(
        config_path, yaml_config.get("output_dir"), DEFAULT_OUTPUT_DIR
    )
    yaml_rules_dir = _config_relative_path(
        config_path, alerts_config.get("rules_dir"), DEFAULT_ALERT_RULES_DIR
    )
    yaml_state_dir = _config_relative_path(
        config_path, alerts_config.get("state_dir"), DEFAULT_ALERT_STATE_DIR
    )
    yaml_check_interval = int(
        alerts_config.get("check_interval_minutes", DEFAULT_ALERT_CHECK_INTERVAL_MINUTES)
    )
    yaml_schedule_preset = alerts_config.get(
        "schedule_preset", DEFAULT_ALERT_SCHEDULE_PRESET
    )
    yaml_retry_attempts = int(
        alerts_config.get("retry_attempts", DEFAULT_ALERT_RETRY_ATTEMPTS)
    )
    yaml_retry_backoff = int(
        alerts_config.get("retry_backoff_seconds", DEFAULT_ALERT_RETRY_BACKOFF_SECONDS)
    )
    yaml_message_prefix = alerts_config.get(
        "message_prefix", DEFAULT_ALERT_MESSAGE_PREFIX
    )

    env_output_dir = Path(os.getenv(ENV_KEYS["output_dir"], str(yaml_output_dir)))
    env_rules_dir = Path(os.getenv(ENV_KEYS["alert_rules_dir"], str(yaml_rules_dir)))
    env_state_dir = Path(os.getenv(ENV_KEYS["alert_state_dir"], str(yaml_state_dir)))
    env_schedule_preset = os.getenv(
        ENV_KEYS["alert_schedule_preset"], yaml_schedule_preset
    )
    env_cron_schedule = os.getenv(ENV_KEYS["alert_cron_schedule"])
    env_check_interval = _int_value(
        os.getenv(ENV_KEYS["alert_check_interval"]), yaml_check_interval
    )
    env_retry_attempts = _int_value(
        os.getenv(ENV_KEYS["alert_retry_attempts"]), yaml_retry_attempts
    )
    env_retry_backoff = _int_value(
        os.getenv(ENV_KEYS["alert_retry_backoff"]), yaml_retry_backoff
    )
    env_message_prefix = os.getenv(
        ENV_KEYS["alert_message_prefix"], yaml_message_prefix
    )

    return AlertOptions(
        config_path=config_path,
        output_dir=Path(args.output_dir) if getattr(args, "output_dir", None) else env_output_dir,
        rules_dir=Path(args.rules_dir) if getattr(args, "rules_dir", None) else env_rules_dir,
        state_dir=Path(args.state_dir) if getattr(args, "state_dir", None) else env_state_dir,
        check_interval_minutes=env_check_interval,
        schedule_preset=env_schedule_preset,
        cron_schedule=env_cron_schedule,
        retry_attempts=env_retry_attempts,
        retry_backoff_seconds=env_retry_backoff,
        message_prefix=env_message_prefix,
        connectors=_connector_configs(alerts_config),
    )


def current_schedule(config_path: str | None = None) -> tuple[str | None, str]:
    resolved_config_path = resolve_config_path(config_path)
    yaml_config = _load_yaml_config(resolved_config_path)
    return (
        os.getenv(ENV_KEYS["cron_schedule"]),
        os.getenv(
            ENV_KEYS["schedule_preset"],
            yaml_config.get("schedule_preset", DEFAULT_SCHEDULE_PRESET),
        ),
    )


def current_alert_schedule(config_path: str | None = None) -> tuple[str | None, str]:
    resolved_config_path = resolve_config_path(config_path)
    yaml_config = _load_yaml_config(resolved_config_path)
    alerts_config = _alerts_config(yaml_config)
    return (
        os.getenv(ENV_KEYS["alert_cron_schedule"]),
        os.getenv(
            ENV_KEYS["alert_schedule_preset"],
            alerts_config.get("schedule_preset", DEFAULT_ALERT_SCHEDULE_PRESET),
        ),
    )
