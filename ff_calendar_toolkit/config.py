"""Internal defaults and schema definitions."""

from pathlib import Path

DEFAULT_CONFIG_PATH = Path("config.yaml")
DEFAULT_ENV_PATH = Path(".env")

ALLOWED_ELEMENT_TYPES = {
    "calendar__cell": "date",
    "calendar__cell calendar__date": "date",
    "calendar__cell calendar__time": "time",
    "calendar__cell calendar__currency": "currency",
    "calendar__cell calendar__impact": "impact",
    "calendar__cell calendar__detail": "detail",
    "calendar__cell calendar__event event": "event",
    "calendar__cell calendar__actual": "actual",
    "calendar__cell calendar__forecast": "forecast",
    "calendar__cell calendar__previous": "previous",
}

EXCLUDED_ELEMENT_TYPES = [
    "calendar__cell calendar__graph",
]

ICON_COLOR_MAP = {
    "icon icon--ff-impact-yel": "yellow",
    "icon icon--ff-impact-ora": "orange",
    "icon icon--ff-impact-red": "red",
    "icon icon--ff-impact-gra": "gray",
}

NORMALIZED_FIELDS = [
    "time",
    "timezone",
    "currency",
    "impact",
    "event",
    "detail",
    "actual",
    "forecast",
    "previous",
    "day",
    "date",
    "scraped_at",
]

DEFAULT_ALLOWED_CURRENCY_CODES = ["CAD", "EUR", "GBP", "USD"]
DEFAULT_ALLOWED_IMPACT_COLORS = ["red", "orange", "gray"]
DEFAULT_TARGET_TIMEZONE = "Asia/Karachi"
DEFAULT_OUTPUT_DIR = Path("news")
DEFAULT_OUTPUT_FORMAT = "both"
DEFAULT_MONTHS = ["this"]
DEFAULT_HEADLESS = True
DEFAULT_SCHEDULE_PRESET = "weekly"
DEFAULT_VIEWER_HOST = "127.0.0.1"
DEFAULT_VIEWER_PORT = 8501
DEFAULT_ALERT_RULES_DIR = Path("rules")
DEFAULT_ALERT_STATE_DIR = Path("state/alerts")
DEFAULT_ALERT_CHECK_INTERVAL_MINUTES = 5
DEFAULT_ALERT_SCHEDULE_PRESET = "every_5_minutes"
DEFAULT_ALERT_RETRY_ATTEMPTS = 3
DEFAULT_ALERT_RETRY_BACKOFF_SECONDS = 1
DEFAULT_ALERT_MESSAGE_PREFIX = "Forex Factory Alert"

ENV_KEYS = {
    "config_path": "FF_CONFIG_PATH",
    "env_path": "FF_ENV_PATH",
    "months": "FF_MONTHS",
    "timezone": "FF_TARGET_TIMEZONE",
    "currencies": "FF_ALLOWED_CURRENCIES",
    "impacts": "FF_ALLOWED_IMPACTS",
    "output_dir": "FF_OUTPUT_DIR",
    "output_format": "FF_OUTPUT_FORMAT",
    "headless": "FF_HEADLESS",
    "viewer_host": "FF_VIEWER_HOST",
    "viewer_port": "FF_VIEWER_PORT",
    "schedule_preset": "FF_SCHEDULE_PRESET",
    "cron_schedule": "CRON_SCHEDULE",
    "alert_rules_dir": "FF_ALERT_RULES_DIR",
    "alert_state_dir": "FF_ALERT_STATE_DIR",
    "alert_schedule_preset": "FF_ALERT_SCHEDULE_PRESET",
    "alert_cron_schedule": "FF_ALERT_CRON_SCHEDULE",
    "alert_check_interval": "FF_ALERT_CHECK_INTERVAL_MINUTES",
    "alert_retry_attempts": "FF_ALERT_RETRY_ATTEMPTS",
    "alert_retry_backoff": "FF_ALERT_RETRY_BACKOFF_SECONDS",
    "alert_message_prefix": "FF_ALERT_MESSAGE_PREFIX",
}
