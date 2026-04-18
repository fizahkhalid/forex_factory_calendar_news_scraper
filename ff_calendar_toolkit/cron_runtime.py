from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class CronField:
    minimum: int
    maximum: int


FIELDS = (
    CronField(0, 59),
    CronField(0, 23),
    CronField(1, 31),
    CronField(1, 12),
    CronField(0, 6),
)


def cron_matches(expression: str, when: datetime | None = None) -> bool:
    when = when or datetime.now().astimezone()
    parts = expression.split()
    if len(parts) != 5:
        raise ValueError("Cron expression must have exactly 5 fields")

    values = (
        when.minute,
        when.hour,
        when.day,
        when.month,
        _cron_weekday(when),
    )

    for part, field, value in zip(parts, FIELDS, values):
        if not _field_matches(part, value, field.minimum, field.maximum):
            return False
    return True


def seconds_until_next_minute(when: datetime | None = None) -> int:
    when = when or datetime.now().astimezone()
    next_minute = (when.replace(second=0, microsecond=0) + timedelta(minutes=1))
    remaining = int((next_minute - when).total_seconds())
    return max(1, remaining)


def _cron_weekday(when: datetime) -> int:
    return (when.weekday() + 1) % 7


def _field_matches(part: str, value: int, minimum: int, maximum: int) -> bool:
    for token in part.split(","):
        token = token.strip()
        if not token:
            continue
        if _token_matches(token, value, minimum, maximum):
            return True
    return False


def _token_matches(token: str, value: int, minimum: int, maximum: int) -> bool:
    if token == "*":
        return True

    if "/" in token:
        base, step_text = token.split("/", 1)
        step = int(step_text)
        if step <= 0:
            raise ValueError("Cron step must be a positive integer")
        allowed = _expand_base(base, minimum, maximum)
        return value in allowed and ((value - min(allowed)) % step == 0)

    return value in _expand_base(token, minimum, maximum)


def _expand_base(base: str, minimum: int, maximum: int) -> list[int]:
    if base in {"", "*"}:
        return list(range(minimum, maximum + 1))

    if "-" in base:
        start_text, end_text = base.split("-", 1)
        start = _normalize_value(int(start_text), minimum, maximum)
        end = _normalize_value(int(end_text), minimum, maximum)
        if end < start:
            raise ValueError("Cron range end cannot be smaller than start")
        return list(range(start, end + 1))

    return [_normalize_value(int(base), minimum, maximum)]


def _normalize_value(value: int, minimum: int, maximum: int) -> int:
    if maximum == 6 and value == 7:
        value = 0
    if not minimum <= value <= maximum:
        raise ValueError(f"Cron value {value} is out of range {minimum}-{maximum}")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cron expression helpers")
    subparsers = parser.add_subparsers(dest="command", required=True)

    matches_parser = subparsers.add_parser("matches", help="Return success if the cron matches now")
    matches_parser.add_argument("expression")

    subparsers.add_parser("sleep-seconds", help="Print seconds until the next minute")

    args = parser.parse_args(argv)

    if args.command == "matches":
        return 0 if cron_matches(args.expression) else 1

    print(seconds_until_next_minute())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
