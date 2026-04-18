#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  PYTHON_BIN="${FF_PYTHON_BIN:-python3}"
fi

exec "${PYTHON_BIN}" -m ff_calendar_toolkit.cli scrape "$@"
