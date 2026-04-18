import json
import re
from datetime import datetime
from pathlib import Path

import pytz

from .config import NORMALIZED_FIELDS


def read_json(path: str | Path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def extract_date_parts(text: str, year: str):
    pattern = (
        r"\b(?P<day>Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b\s+"
        r"(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b\s+"
        r"(?P<date>\d{1,2})\b"
    )
    match = re.search(pattern, text)
    if not match:
        return None

    month_number = datetime.strptime(match.group("month"), "%b").month
    return {
        "day": match.group("day"),
        "date": f"{int(match.group('date')):02d}/{month_number:02d}/{year}",
    }


def convert_time_zone(
    date_str: str,
    time_str: str,
    from_zone_str: str | None,
    to_zone_str: str | None,
) -> str:
    if not time_str or not date_str or not from_zone_str or not to_zone_str:
        return time_str

    if time_str.lower() in ["all day", "tentative"]:
        return time_str

    try:
        from_zone = pytz.timezone(from_zone_str)
        to_zone = pytz.timezone(to_zone_str)
        naive_dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %I:%M%p")
        localized_dt = from_zone.localize(naive_dt)
        return localized_dt.astimezone(to_zone).strftime("%H:%M")
    except Exception:
        return time_str


def filter_row(row: dict, allowed_currencies: list[str], allowed_impacts: list[str]):
    if row["currency"] not in allowed_currencies:
        return False
    if row["impact"].lower() not in allowed_impacts:
        return False
    return True


def normalize_rows(
    data: list[dict],
    year: str,
    source_timezone: str | None,
    target_timezone: str | None,
    allowed_currencies: list[str],
    allowed_impacts: list[str],
    scraped_at: str | None = None,
) -> list[dict]:
    current_date = ""
    current_time = ""
    current_day = ""
    structured_rows = []

    for row in data:
        new_row = row.copy()

        if "date" in new_row and new_row["date"] != "empty":
            date_parts = extract_date_parts(new_row["date"], year)
            if date_parts:
                current_date = date_parts["date"]
                current_day = date_parts["day"]

        if "time" in new_row:
            if new_row["time"] != "empty":
                current_time = new_row["time"].strip()
            else:
                new_row["time"] = current_time

        if len(row) == 1:
            continue

        new_row["day"] = current_day
        new_row["date"] = current_date
        new_row["time"] = convert_time_zone(
            current_date, current_time, source_timezone, target_timezone
        )
        new_row["timezone"] = target_timezone or source_timezone or ""
        new_row["currency"] = row.get("currency", "")
        new_row["impact"] = row.get("impact", "")
        new_row["event"] = row.get("event", "")
        new_row["detail"] = row.get("detail", "")
        new_row["actual"] = row.get("actual", "")
        new_row["forecast"] = row.get("forecast", "")
        new_row["previous"] = row.get("previous", "")
        new_row["scraped_at"] = scraped_at or ""

        for key, value in list(new_row.items()):
            if value == "empty":
                new_row[key] = ""

        if filter_row(new_row, allowed_currencies, allowed_impacts):
            structured_rows.append({field: new_row.get(field, "") for field in NORMALIZED_FIELDS})

    return structured_rows
