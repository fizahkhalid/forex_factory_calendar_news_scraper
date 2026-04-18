import json
from datetime import datetime, timezone
from pathlib import Path


class AlertStateStore:
    def __init__(self, state_dir: Path) -> None:
        self.state_dir = state_dir
        self.state_path = self.state_dir / "alert_state.json"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict:
        if not self.state_path.exists():
            return {"sent": {}, "failures": {}}
        with open(self.state_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        payload.setdefault("sent", {})
        payload.setdefault("failures", {})
        return payload

    def save(self, state: dict) -> None:
        with open(self.state_path, "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2)

    def is_sent(self, state: dict, dedup_key: str, connector_id: str) -> bool:
        sent = state.get("sent", {}).get(dedup_key, {})
        connectors = sent.get("connectors", [])
        return connector_id in connectors

    def mark_sent(self, state: dict, dedup_key: str, connector_id: str, preview: dict) -> None:
        sent = state.setdefault("sent", {}).setdefault(
            dedup_key,
            {
                "connectors": [],
                "preview": preview,
                "sent_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        if connector_id not in sent["connectors"]:
            sent["connectors"].append(connector_id)
        state.setdefault("failures", {}).pop(f"{dedup_key}|{connector_id}", None)

    def mark_failure(self, state: dict, dedup_key: str, connector_id: str, error_message: str) -> None:
        state.setdefault("failures", {})[f"{dedup_key}|{connector_id}"] = {
            "error": error_message,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
