import json
import os
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import streamlit as st
import yaml

from ff_calendar_toolkit.alerts.rules import load_rule_document, load_rules, rule_template, save_rule
from ff_calendar_toolkit.alerts.service import preview_alerts
from ff_calendar_toolkit.alerts.state import AlertStateStore
from ff_calendar_toolkit.config import NORMALIZED_FIELDS
from ff_calendar_toolkit.runtime import (
    build_alert_options,
    build_view_options,
    load_env_file,
    resolve_config_path,
)


WEEKDAY_OPTIONS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _load_default_file(output_dir: Path) -> Path | None:
    last_run_files = sorted((output_dir / "last_run").glob("*.json"))
    if last_run_files:
        return last_run_files[-1]

    history_files = sorted((output_dir / "history").rglob("*.json"))
    if history_files:
        return history_files[-1]

    monthly_files = sorted((output_dir / "monthly").glob("*.json"))
    if monthly_files:
        return monthly_files[-1]

    return None


def _load_records(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _view_context():
    config_path = resolve_config_path(os.getenv("FF_CONFIG_PATH"))
    load_env_file(config_path)
    args = SimpleNamespace(
        config=str(config_path),
        output_dir=os.getenv("FF_VIEWER_OUTPUT_DIR"),
        rules_dir=os.getenv("FF_ALERT_RULES_DIR"),
        state_dir=os.getenv("FF_ALERT_STATE_DIR"),
        host=None,
        port=None,
    )
    view_options = build_view_options(args)
    alert_options = build_alert_options(args)
    return view_options, alert_options


def _rule_defaults(records: list[dict]) -> tuple[list[str], list[str]]:
    if not records:
        return ["USD", "EUR", "GBP", "CAD"], ["red", "orange", "gray"]
    df = pd.DataFrame(records)
    currencies = sorted(value for value in df.get("currency", pd.Series(dtype=str)).dropna().unique() if value)
    impacts = sorted(value for value in df.get("impact", pd.Series(dtype=str)).dropna().unique() if value)
    return currencies, impacts


def _save_config_text(config_path: Path, content: str) -> None:
    parsed = yaml.safe_load(content) or {}
    with open(config_path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(parsed, handle, sort_keys=False)


def _render_data_browser(output_dir: Path) -> list[dict]:
    default_path = _load_default_file(output_dir)
    if default_path is None:
        st.warning(f"No JSON data found in {output_dir}. Run the scraper first.")
        return []

    json_files = (
        sorted((output_dir / "last_run").glob("*.json"))
        + sorted((output_dir / "monthly").glob("*.json"))
        + sorted((output_dir / "history").rglob("*.json"))
    )
    selected = st.sidebar.selectbox(
        "Dataset",
        options=json_files,
        index=json_files.index(default_path),
        format_func=lambda path: str(path.relative_to(output_dir)),
    )

    records = _load_records(selected)
    if not records:
        st.info("The selected dataset is empty.")
        st.dataframe(pd.DataFrame(columns=NORMALIZED_FIELDS), use_container_width=True)
        return []

    df = pd.DataFrame(records, columns=NORMALIZED_FIELDS)
    currencies = st.sidebar.multiselect(
        "Currencies",
        options=sorted(df["currency"].dropna().unique()),
        default=sorted(df["currency"].dropna().unique()),
    )
    impacts = st.sidebar.multiselect(
        "Impact",
        options=sorted(df["impact"].dropna().unique()),
        default=sorted(df["impact"].dropna().unique()),
    )

    filtered = df[df["currency"].isin(currencies) & df["impact"].isin(impacts)]
    st.metric("Rows", len(filtered))
    st.dataframe(filtered, use_container_width=True)
    return records


def _render_rules_tab(alert_options, records: list[dict]) -> None:
    st.subheader("Rules")
    rules_dir = alert_options.rules_dir
    rules_dir.mkdir(parents=True, exist_ok=True)

    existing_files = sorted(rules_dir.glob("*.yaml"))
    choices = ["<new rule>"] + [path.name for path in existing_files]
    selected_name = st.selectbox("Rule file", choices)

    if selected_name == "<new rule>":
        payload = rule_template()
        file_name = ""
    else:
        selected_path = rules_dir / selected_name
        payload = load_rule_document(selected_path)
        file_name = selected_name

    currencies, impacts = _rule_defaults(records)
    connector_ids = [connector.connector_id for connector in alert_options.connectors]
    deliver_default = payload.get("deliver", []) or connector_ids[:1]
    match = payload.get("match", {})
    trigger = payload.get("trigger", {})

    with st.form("rule_editor"):
        name = st.text_input("Rule name", value=payload.get("name", ""))
        enabled = st.checkbox("Enabled", value=bool(payload.get("enabled", True)))
        selected_currencies = st.multiselect(
            "Currencies",
            options=currencies,
            default=[value for value in match.get("currencies", []) if value in currencies],
        )
        selected_impacts = st.multiselect(
            "Impacts",
            options=impacts,
            default=[value for value in match.get("impacts", []) if value in impacts],
        )
        event_names = st.text_input(
            "Exact event names (comma separated)",
            value=", ".join(match.get("event_names", [])),
        )
        event_keywords = st.text_input(
            "Event keywords (comma separated)",
            value=", ".join(match.get("event_keywords", [])),
        )
        weekdays = st.multiselect(
            "Weekdays",
            options=WEEKDAY_OPTIONS,
            default=[value for value in match.get("weekdays", []) if value in WEEKDAY_OPTIONS],
        )
        minutes_before = st.number_input(
            "Minutes before event", min_value=0, step=1, value=int(trigger.get("minutes_before", 10))
        )
        deliver = st.multiselect(
            "Connectors",
            options=connector_ids,
            default=[value for value in deliver_default if value in connector_ids],
        )
        submitted = st.form_submit_button("Save rule")

    if submitted:
        new_payload = {
            "name": name,
            "enabled": enabled,
            "match": {
                "currencies": selected_currencies,
                "impacts": selected_impacts,
                "event_names": _split_csv(event_names),
                "event_keywords": _split_csv(event_keywords),
                "weekdays": weekdays,
            },
            "trigger": {"minutes_before": int(minutes_before)},
            "deliver": deliver,
        }
        target_name = file_name or f"{''.join(char.lower() if char.isalnum() else '_' for char in name).strip('_')}.yaml"
        try:
            save_rule(rules_dir, new_payload, target_name)
            st.success(f"Saved rule to {rules_dir / target_name}")
        except ValueError as exc:
            st.error(str(exc))

    st.caption("Rule YAML preview")
    st.code(yaml.safe_dump(payload if selected_name != "<new rule>" else rule_template(), sort_keys=False), language="yaml")


def _render_config_tab(config_path: Path, alert_options) -> None:
    st.subheader("Configuration")
    config_text = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    updated_text = st.text_area("config.yaml", value=config_text, height=360)
    if st.button("Save config.yaml"):
        try:
            _save_config_text(config_path, updated_text)
            st.success(f"Saved {config_path}")
        except yaml.YAMLError as exc:
            st.error(f"Invalid YAML: {exc}")

    st.markdown("**Expected secret env vars**")
    env_rows = []
    for connector in alert_options.connectors:
        for key, value in connector.settings.items():
            if str(key).endswith("_env"):
                env_rows.append({"connector": connector.connector_id, "variable": value})
    if env_rows:
        st.dataframe(pd.DataFrame(env_rows), use_container_width=True)
    else:
        st.info("No connectors configured yet.")


def _render_preview_tab(alert_options) -> None:
    st.subheader("Upcoming alert matches")
    preview_rows = preview_alerts(alert_options)
    if not preview_rows:
        st.info("No matching alerts found with the current data and rules.")
        return
    st.dataframe(pd.DataFrame(preview_rows), use_container_width=True)


def _render_state_tab(alert_options) -> None:
    st.subheader("Alert state")
    state = AlertStateStore(alert_options.state_dir).load()

    sent_rows = []
    for dedup_key, payload in state.get("sent", {}).items():
        sent_rows.append(
            {
                "dedup_key": dedup_key,
                "connectors": ", ".join(payload.get("connectors", [])),
                "sent_at": payload.get("sent_at", ""),
                "rule": payload.get("preview", {}).get("rule", ""),
                "event": payload.get("preview", {}).get("event", ""),
            }
        )
    failure_rows = []
    for key, payload in state.get("failures", {}).items():
        failure_rows.append(
            {
                "key": key,
                "error": payload.get("error", ""),
                "updated_at": payload.get("updated_at", ""),
            }
        )

    st.markdown("**Sent notifications**")
    st.dataframe(pd.DataFrame(sent_rows), use_container_width=True)
    st.markdown("**Recent failures**")
    st.dataframe(pd.DataFrame(failure_rows), use_container_width=True)


def _split_csv(text: str) -> list[str]:
    return [value.strip() for value in text.split(",") if value.strip()]


def main() -> None:
    view_options, alert_options = _view_context()
    st.set_page_config(page_title="Forex Factory Calendar Toolkit", layout="wide")
    st.title("Forex Factory Calendar Toolkit")
    st.caption("Browse data, edit rules, and manage alert configuration from one local UI.")

    data_tab, rules_tab, config_tab, preview_tab, state_tab = st.tabs(
        ["Data", "Rules", "Config", "Preview", "Alert State"]
    )

    with data_tab:
        records = _render_data_browser(view_options.output_dir)
    with rules_tab:
        _render_rules_tab(alert_options, records)
    with config_tab:
        _render_config_tab(view_options.config_path, alert_options)
    with preview_tab:
        _render_preview_tab(alert_options)
    with state_tab:
        _render_state_tab(alert_options)


if __name__ == "__main__":
    main()
