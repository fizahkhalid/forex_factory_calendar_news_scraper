SCHEDULE_PRESETS = {
    "hourly": "0 * * * *",
    "daily": "0 0 * * *",
    "weekly": "0 0 * * 0",
    "monthly": "0 0 1 * *",
}

ALERT_SCHEDULE_PRESETS = {
    "every_1_minute": "* * * * *",
    "every_5_minutes": "*/5 * * * *",
    "every_10_minutes": "*/10 * * * *",
    "hourly": "0 * * * *",
}


def resolve_schedule(preset: str | None, cron_expression: str | None) -> str:
    if cron_expression:
        return cron_expression
    if preset and preset.lower() in SCHEDULE_PRESETS:
        return SCHEDULE_PRESETS[preset.lower()]
    return SCHEDULE_PRESETS["weekly"]


def resolve_alert_schedule(preset: str | None, cron_expression: str | None) -> str:
    if cron_expression:
        return cron_expression
    if preset and preset.lower() in ALERT_SCHEDULE_PRESETS:
        return ALERT_SCHEDULE_PRESETS[preset.lower()]
    return ALERT_SCHEDULE_PRESETS["every_5_minutes"]
