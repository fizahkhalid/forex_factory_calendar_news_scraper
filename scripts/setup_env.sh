#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
CONDA_DIR="${ROOT_DIR}/.conda-env"
REQ_FILE="${ROOT_DIR}/requirements.txt"
MIN_PYTHON_MAJOR=3
MIN_PYTHON_MINOR=9

print_header() {
  printf '\nForex Factory Toolkit Environment Setup\n'
  printf '======================================\n'
}

print_choice_menu() {
  printf '\nChoose an environment manager:\n'
  printf '  1) uv\n'
  printf '  2) conda\n'
  printf '  3) python venv\n'
}

ensure_command() {
  local command_name="$1"
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    printf '\nError: %s is not installed or not on PATH.\n' "${command_name}" >&2
    exit 1
  fi
}

python_is_supported() {
  local interpreter="$1"
  "${interpreter}" - <<'PY'
import sys
sys.exit(0 if sys.version_info >= (3, 9) else 1)
PY
}

pick_python_interpreter() {
  local candidates=(
    "python3.12"
    "python3.11"
    "python3.10"
    "python3.9"
    "python3"
  )

  local candidate
  for candidate in "${candidates[@]}"; do
    if command -v "${candidate}" >/dev/null 2>&1 && python_is_supported "${candidate}"; then
      command -v "${candidate}"
      return 0
    fi
  done

  printf '\nError: no supported Python interpreter found.\n' >&2
  printf 'This project requires Python %s.%s or newer.\n' "${MIN_PYTHON_MAJOR}" "${MIN_PYTHON_MINOR}" >&2
  exit 1
}

setup_uv() {
  ensure_command "uv"
  local python_bin
  python_bin="$(pick_python_interpreter)"

  printf '\nCreating uv environment in %s\n' "${VENV_DIR}"
  printf 'Using Python interpreter: %s\n' "${python_bin}"
  uv venv --python "${python_bin}" "${VENV_DIR}"
  uv pip install --python "${VENV_DIR}/bin/python" -r "${REQ_FILE}"

  printf '\nDone.\n'
  printf 'Activate it with:\n'
  printf '  source .venv/bin/activate\n'
}

setup_conda() {
  ensure_command "conda"

  printf '\nCreating conda environment in %s\n' "${CONDA_DIR}"
  conda create --prefix "${CONDA_DIR}" python=3.11 pip -y
  conda run --prefix "${CONDA_DIR}" python -m pip install -r "${REQ_FILE}"

  printf '\nDone.\n'
  printf 'Activate it with:\n'
  printf '  conda activate "%s"\n' "${CONDA_DIR}"
}

setup_venv() {
  local python_bin
  python_bin="$(pick_python_interpreter)"

  printf '\nCreating venv environment in %s\n' "${VENV_DIR}"
  printf 'Using Python interpreter: %s\n' "${python_bin}"
  "${python_bin}" -m venv "${VENV_DIR}"
  "${VENV_DIR}/bin/python" -m pip install --upgrade pip
  "${VENV_DIR}/bin/python" -m pip install -r "${REQ_FILE}"

  printf '\nDone.\n'
  printf 'Activate it with:\n'
  printf '  source .venv/bin/activate\n'
}

main() {
  print_header
  print_choice_menu
  printf '\nEnter 1, 2, or 3: '
  read -r choice

  case "${choice}" in
    1)
      setup_uv
      ;;
    2)
      setup_conda
      ;;
    3)
      setup_venv
      ;;
    *)
      printf '\nInvalid choice. Please run the script again and choose 1, 2, or 3.\n' >&2
      exit 1
      ;;
  esac

  printf '\nNext steps:\n'
  printf '  ./scripts/run_scraper.sh --months this --format both\n'
  printf '  ./scripts/run_alerts.sh\n'
  printf '  ./scripts/view_data.sh --output-dir news\n'
}

main "$@"
