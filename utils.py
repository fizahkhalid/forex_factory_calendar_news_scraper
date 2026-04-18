from datetime import datetime

from ff_calendar_toolkit.config import DEFAULT_ALLOWED_CURRENCY_CODES, DEFAULT_ALLOWED_IMPACT_COLORS, DEFAULT_OUTPUT_DIR, DEFAULT_TARGET_TIMEZONE
from ff_calendar_toolkit.models import ScrapeContext
from ff_calendar_toolkit.normalize import convert_time_zone, extract_date_parts, filter_row, normalize_rows, read_json
from ff_calendar_toolkit.storage import FileOutputStore


def reformat_data(data: list, year: str) -> list:
    return normalize_rows(
        data,
        year,
        source_timezone=None,
        target_timezone=DEFAULT_TARGET_TIMEZONE,
        allowed_currencies=DEFAULT_ALLOWED_CURRENCY_CODES,
        allowed_impacts=DEFAULT_ALLOWED_IMPACT_COLORS,
    )


def save_csv(data, month, year):
    records = reformat_data(data, year)
    context = ScrapeContext(
        month_param=month.lower(),
        month_name=month,
        month_slug=f"{year}-{datetime.strptime(month, '%B').month:02d}",
        year=str(year),
        source_timezone=None,
        target_timezone=DEFAULT_TARGET_TIMEZONE,
        scraped_at="",
    )
    store = FileOutputStore(DEFAULT_OUTPUT_DIR)
    store.write(records, context, "csv")
    return True


def find_location_timezone():
    return None
