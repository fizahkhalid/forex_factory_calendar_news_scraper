from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunOptions:
    config_path: Path
    months: list[str]
    output_format: str
    output_dir: Path
    target_timezone: str | None
    allowed_currencies: list[str]
    allowed_impacts: list[str]
    headless: bool


@dataclass(frozen=True)
class ViewOptions:
    config_path: Path
    output_dir: Path
    rules_dir: Path
    state_dir: Path
    host: str
    port: int


@dataclass(frozen=True)
class AlertConnector:
    connector_id: str
    connector_type: str
    enabled: bool
    settings: dict


@dataclass(frozen=True)
class AlertOptions:
    config_path: Path
    output_dir: Path
    rules_dir: Path
    state_dir: Path
    check_interval_minutes: int
    schedule_preset: str
    cron_schedule: str | None
    retry_attempts: int
    retry_backoff_seconds: int
    message_prefix: str
    connectors: list[AlertConnector]


@dataclass(frozen=True)
class ScrapeContext:
    month_param: str
    month_name: str
    month_slug: str
    year: str
    source_timezone: str | None
    target_timezone: str | None
    scraped_at: str


@dataclass(frozen=True)
class WriteResult:
    last_run_paths: list[Path]
    monthly_paths: list[Path]
    history_paths: list[Path]
