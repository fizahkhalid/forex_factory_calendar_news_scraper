import csv
import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from .config import NORMALIZED_FIELDS
from .models import ScrapeContext, WriteResult


class OutputStore(ABC):
    @abstractmethod
    def write(self, records: list[dict], context: ScrapeContext, output_format: str) -> WriteResult:
        raise NotImplementedError


class FileOutputStore(OutputStore):
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.last_run_dir = self.output_dir / "last_run"
        self.monthly_dir = self.output_dir / "monthly"
        self.history_dir = self.output_dir / "history"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.last_run_dir.mkdir(parents=True, exist_ok=True)
        self.monthly_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def begin_run(self, output_format: str) -> None:
        for path in self.last_run_dir.glob("*"):
            if path.is_file():
                path.unlink()

    def write(self, records: list[dict], context: ScrapeContext, output_format: str) -> WriteResult:
        formats = ["csv", "json"] if output_format == "both" else [output_format]
        last_run_paths = []
        monthly_paths = []
        history_paths = []
        timestamp = datetime.now().astimezone().strftime("%Y-%m-%dT%H-%M-%S%z")
        history_month_dir = self.history_dir / context.month_slug
        history_month_dir.mkdir(parents=True, exist_ok=True)

        for file_format in formats:
            last_run_path = self.last_run_dir / f"{context.month_slug}.{file_format}"
            monthly_path = self.monthly_dir / f"{context.month_slug}.{file_format}"
            history_path = history_month_dir / f"{timestamp}.{file_format}"

            self._write_file(last_run_path, file_format, records)
            self._write_file(monthly_path, file_format, records)
            self._write_file(history_path, file_format, records)

            last_run_paths.append(last_run_path)
            monthly_paths.append(monthly_path)
            history_paths.append(history_path)

        return WriteResult(
            last_run_paths=last_run_paths,
            monthly_paths=monthly_paths,
            history_paths=history_paths,
        )

    def _write_file(self, path: Path, file_format: str, records: list[dict]) -> None:
        if file_format == "csv":
            self._write_csv(path, records)
            return
        self._write_json(path, records)

    def _write_csv(self, path: Path, records: list[dict]) -> None:
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=NORMALIZED_FIELDS)
            writer.writeheader()
            writer.writerows([{field: row.get(field, "") for field in NORMALIZED_FIELDS} for row in records])

    def _write_json(self, path: Path, records: list[dict]) -> None:
        payload = [{field: row.get(field, "") for field in NORMALIZED_FIELDS} for row in records]
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
