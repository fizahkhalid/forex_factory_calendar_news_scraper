import json
import os
import time
from urllib import parse, request
from urllib.error import HTTPError, URLError

from ff_calendar_toolkit.models import AlertConnector, AlertOptions

from .models import AlertEvent, AlertRule


class NotificationError(RuntimeError):
    pass


class NotifierFactory:
    def __init__(self, options: AlertOptions) -> None:
        self.options = options
        self.connector_map = {
            connector.connector_id: connector
            for connector in options.connectors
            if connector.enabled
        }

    def connector_ids(self) -> list[str]:
        return sorted(self.connector_map)

    def send(self, connector_id: str, rule: AlertRule, event: AlertEvent) -> None:
        connector = self.connector_map.get(connector_id)
        if connector is None:
            raise NotificationError(f"Connector '{connector_id}' is not configured or enabled")

        message = render_message(self.options.message_prefix, rule, event)
        for attempt in range(1, self.options.retry_attempts + 1):
            try:
                self._send_once(connector, message, rule, event)
                return
            except NotificationError:
                if attempt == self.options.retry_attempts:
                    raise
                time.sleep(self.options.retry_backoff_seconds * attempt)

    def _send_once(
        self, connector: AlertConnector, message: str, rule: AlertRule, event: AlertEvent
    ) -> None:
        if connector.connector_type == "discord":
            self._send_discord(connector, message)
            return
        if connector.connector_type == "telegram":
            self._send_telegram(connector, message)
            return
        if connector.connector_type == "webhook":
            self._send_webhook(connector, message, rule, event)
            return
        raise NotificationError(f"Unsupported connector type '{connector.connector_type}'")

    def _send_discord(self, connector: AlertConnector, message: str) -> None:
        webhook_url = _required_env(connector.settings.get("webhook_url_env"))
        _post_json(webhook_url, {"content": message})

    def _send_telegram(self, connector: AlertConnector, message: str) -> None:
        bot_token = _required_env(connector.settings.get("bot_token_env"))
        chat_id = _required_env(connector.settings.get("chat_id_env"))
        payload = parse.urlencode({"chat_id": chat_id, "text": message}).encode("utf-8")
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        _post_form(url, payload)

    def _send_webhook(
        self, connector: AlertConnector, message: str, rule: AlertRule, event: AlertEvent
    ) -> None:
        url = _required_env(connector.settings.get("url_env"))
        headers = {}
        header_name = connector.settings.get("auth_header_name")
        header_env = connector.settings.get("auth_header_env")
        if header_name and header_env:
            headers[str(header_name)] = _required_env(header_env)

        payload = {
            "message": message,
            "rule": {
                "id": rule.rule_id,
                "name": rule.name,
            },
            "event": event.payload,
            "event_time": event.event_time.isoformat(),
        }
        _post_json(url, payload, headers=headers)


def render_message(prefix: str, rule: AlertRule, event: AlertEvent) -> str:
    payload = event.payload
    return (
        f"{prefix}\n"
        f"Rule: {rule.name}\n"
        f"Event: {payload.get('event', '')}\n"
        f"Currency: {payload.get('currency', '')}\n"
        f"Impact: {payload.get('impact', '')}\n"
        f"When: {payload.get('date', '')} {payload.get('time', '')} {payload.get('timezone', '')}\n"
        f"Detail: {payload.get('detail', '')}"
    )


def _required_env(env_name) -> str:
    if not env_name:
        raise NotificationError("Connector is missing required environment-variable mapping")
    value = os.getenv(str(env_name))
    if not value:
        raise NotificationError(f"Missing required secret environment variable '{env_name}'")
    return value


def _post_json(url: str, payload: dict, headers: dict | None = None) -> None:
    body = json.dumps(payload).encode("utf-8")
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    _perform_request(url, body, request_headers)


def _post_form(url: str, payload: bytes) -> None:
    _perform_request(url, payload, {"Content-Type": "application/x-www-form-urlencoded"})


def _perform_request(url: str, payload: bytes, headers: dict) -> None:
    req = request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=10) as response:
            status = getattr(response, "status", 200)
            if status >= 400:
                raise NotificationError(f"Request failed with status {status}")
    except (HTTPError, URLError) as exc:
        raise NotificationError(str(exc)) from exc
