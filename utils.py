import os
import re
import json
import pytz
import pandas as pd
from datetime import datetime
import config


def read_json(path):
    """
    Read JSON data from a file.
    Args: path (str): The path to the JSON file.
    Returns: dict: The loaded JSON data.
    """
    with open(path, 'r') as f:
        data = json.load(f)
    return data


def extract_date_parts(text, year):
    # Full pattern: Day (e.g., Sun), Month (e.g., Jun), Day number (e.g., 1 or 01)
    pattern = r'\b(?P<day>Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b\s+' \
              r'(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b\s+' \
              r'(?P<date>\d{1,2})\b'

    match = re.search(pattern, text)
    if match:
        month_abbr = match.group("month")
        day = int(match.group("date"))

        # Convert month abbreviation to month number
        month_number = datetime.strptime(month_abbr, "%b").month

        # Format date as dd/mm/yyyy
        formatted_date = f"{day:02d}/{month_number:02d}/{year}"

        return {
            "day": match.group("day"),
            "date": formatted_date
        }
    else:
        return None


def reformat_data(data: list, year: str) -> list:
    current_date = ''
    current_time = ''
    current_day = ''
    structured_rows = []

    for row in data:
        new_row = row.copy()

        if "date" in new_row and new_row['date'] != "empty":
            date_parts = extract_date_parts(new_row["date"], year)
            if date_parts:
                current_date = date_parts["date"]
                current_day = date_parts["day"]

        if "time" in new_row:
            current_time = new_row["time"].strip()

        if len(row) == 1:
            continue

        new_row["day"] = current_day
        new_row["date"] = current_date

        if config.SCRAPER_TIMEZONE and config.TARGET_TIMEZONE:
            new_row["time"] = convert_time_zone(
                current_date, current_time, config.SCRAPER_TIMEZONE, config.TARGET_TIMEZONE
            )
        else:
            new_row["time"] = current_time

        new_row["currency"] = row.get("currency", "")
        new_row["impact"] = row.get("impact", "")
        new_row["event"] = row.get("event", "")
        new_row["detail"] = row.get("detail", "")
        new_row["actual"] = row.get("actual", "")
        new_row["forecast"] = row.get("forecast", "")
        new_row["previous"] = row.get("previous", "")

        # Replace "empty" with ""
        for key, value in new_row.items():
            if value == "empty":
                new_row[key] = ""

        structured_rows.append(new_row)

    return structured_rows


def save_csv(data, month, year):
    structured_rows = reformat_data(data, year)
    header = list(structured_rows[0].keys())
    df = pd.DataFrame(structured_rows, columns=header)
    os.makedirs("news", exist_ok=True)
    df.to_csv(f"news/{month}_{year}_news.csv", index=False)
    return True


def convert_time_zone(date_str, time_str, from_zone_str, to_zone_str):
    """
    Convert time from one timezone to another.
    - date_str: '01/07/2025'
    - time_str: '3:00am'
    """
    if not time_str or not date_str:
        return time_str

    if time_str.lower() in ["all day", "tentative"]:
        return time_str

    try:
        from_zone = pytz.timezone(from_zone_str)
        to_zone = pytz.timezone(to_zone_str)

        naive_dt = datetime.strptime(
            f"{date_str} {time_str}", "%d/%m/%Y %I:%M%p")
        localized_dt = from_zone.localize(naive_dt)
        converted_dt = localized_dt.astimezone(to_zone)

        return converted_dt.strftime("%H:%M")
    except Exception as e:
        print(f"[WARN] Failed to convert '{time_str}' on {date_str}: {e}")
        return time_str
