#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: run.sh <scrape|alerts-check|view|test-notify> [args...]" >&2
  exit 1
fi

COMMAND="$1"
shift

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  PYTHON_BIN="${FF_PYTHON_BIN:-python3}"
fi

exec "${PYTHON_BIN}" -m ff_calendar_toolkit.cli "${COMMAND}" "$@"
