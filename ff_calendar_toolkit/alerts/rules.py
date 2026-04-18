from pathlib import Path
from typing import Iterable

import yaml

from .models import AlertRule


RULE_TEMPLATE = {
    "name": "usd-high-impact",
    "enabled": True,
    "match": {
        "currencies": ["USD"],
        "impacts": ["red"],
        "event_names": [],
        "event_keywords": ["CPI", "Non-Farm"],
        "weekdays": [],
    },
    "trigger": {
        "minutes_before": 10,
    },
    "deliver": ["discord_main"],
}


def slugify_rule_name(name: str) -> str:
    return "".join(char.lower() if char.isalnum() else "-" for char in name).strip("-")


def rule_template() -> dict:
    return yaml.safe_load(yaml.safe_dump(RULE_TEMPLATE))


def load_rules(rules_dir: Path) -> list[AlertRule]:
    if not rules_dir.exists():
        return []

    rules = []
    for path in sorted(rules_dir.glob("*.yaml")):
        with open(path, "r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}
        rules.append(_validate_rule(path, payload))
    return rules


def save_rule(rules_dir: Path, payload: dict, filename: str | None = None) -> Path:
    rules_dir.mkdir(parents=True, exist_ok=True)
    rule = _validate_rule(Path(filename or ""), payload)
    file_name = filename or f"{rule.rule_id}.yaml"
    target = rules_dir / file_name
    with open(target, "w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False)
    return target


def load_rule_document(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _validate_rule(path: Path, payload: dict) -> AlertRule:
    if not isinstance(payload, dict):
        raise ValueError(f"Rule file {path} must contain a YAML object")

    name = str(payload.get("name", "")).strip()
    if not name:
        raise ValueError(f"Rule file {path} is missing a non-empty 'name'")

    match = payload.get("match") or {}
    trigger = payload.get("trigger") or {}
    deliver = payload.get("deliver") or []

    if not isinstance(match, dict):
        raise ValueError(f"Rule file {path} has invalid 'match' section")
    if not isinstance(trigger, dict):
        raise ValueError(f"Rule file {path} has invalid 'trigger' section")
    if not isinstance(deliver, list) or not deliver:
        raise ValueError(f"Rule file {path} must define a non-empty 'deliver' list")

    minutes_before = trigger.get("minutes_before", 10)
    if not isinstance(minutes_before, int) or minutes_before < 0:
        raise ValueError(f"Rule file {path} has invalid trigger.minutes_before")

    rule_id = slugify_rule_name(name) or path.stem
    return AlertRule(
        rule_id=rule_id,
        name=name,
        enabled=bool(payload.get("enabled", True)),
        match=match,
        trigger=trigger,
        deliver=[str(item).strip() for item in deliver if str(item).strip()],
        path=str(path),
    )


def connector_choices_from_rules(rules: Iterable[AlertRule]) -> list[str]:
    choices = []
    for rule in rules:
        for connector in rule.deliver:
            if connector not in choices:
                choices.append(connector)
    return choices
