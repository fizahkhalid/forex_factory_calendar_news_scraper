#!/usr/bin/env bash
set -euo pipefail

MODE="${FF_RUN_MODE:-once}"
LOG_DIR="/app/state/logs"
LOG_FILE="${LOG_DIR}/forex_factory_scrape.log"
ALERT_LOG_FILE="${LOG_DIR}/forex_factory_alerts.log"

resolve_schedule() {
  if [[ -n "${CRON_SCHEDULE:-}" ]]; then
    printf '%s' "${CRON_SCHEDULE}"
    return
  fi

  case "${FF_SCHEDULE_PRESET:-weekly}" in
    hourly) printf '0 * * * *' ;;
    daily) printf '0 0 * * *' ;;
    weekly) printf '0 0 * * 0' ;;
    monthly) printf '0 0 1 * *' ;;
    *) printf '0 0 * * 0' ;;
  esac
}

resolve_alert_schedule() {
  if [[ -n "${FF_ALERT_CRON_SCHEDULE:-}" ]]; then
    printf '%s' "${FF_ALERT_CRON_SCHEDULE}"
    return
  fi

  case "${FF_ALERT_SCHEDULE_PRESET:-every_5_minutes}" in
    every_1_minute) printf '* * * * *' ;;
    every_5_minutes) printf '*/5 * * * *' ;;
    every_10_minutes) printf '*/10 * * * *' ;;
    hourly) printf '0 * * * *' ;;
    *) printf '*/5 * * * *' ;;
  esac
}

run_scheduler_loop() {
  local schedule="$1"
  local command_name="$2"
  local log_file="$3"

  mkdir -p "${LOG_DIR}"
  touch "${log_file}"

  echo "Starting ${command_name} scheduler mode with cron '${schedule}'"

  while true; do
    if /usr/local/bin/python3 -m ff_calendar_toolkit.cron_runtime matches "${schedule}"; then
      printf '[%s] Running %s\n' "$(date --iso-8601=seconds)" "${command_name}" >> "${log_file}"
      if (cd /app && /usr/local/bin/python3 -m ff_calendar_toolkit.cli "${command_name}" >> "${log_file}" 2>&1); then
        printf '[%s] %s completed successfully\n' "$(date --iso-8601=seconds)" "${command_name}" >> "${log_file}"
      else
        printf '[%s] %s failed with exit code %s\n' "$(date --iso-8601=seconds)" "${command_name}" "$?" >> "${log_file}"
      fi
      sleep "$(/usr/local/bin/python3 -m ff_calendar_toolkit.cron_runtime sleep-seconds)"
      continue
    fi
    sleep "$(/usr/local/bin/python3 -m ff_calendar_toolkit.cron_runtime sleep-seconds)"
  done
}

if [[ "${MODE}" == "schedule" ]]; then
  SCHEDULE="$(resolve_schedule)"
  run_scheduler_loop "${SCHEDULE}" "scrape" "${LOG_FILE}"
fi

if [[ "${MODE}" == "alerts-schedule" ]]; then
  ALERT_SCHEDULE="$(resolve_alert_schedule)"
  run_scheduler_loop "${ALERT_SCHEDULE}" "alerts-check" "${ALERT_LOG_FILE}"
fi

if [[ "${MODE}" == "alerts-once" ]]; then
  exec python3 -m ff_calendar_toolkit.cli alerts-check "$@"
fi

exec python3 -m ff_calendar_toolkit.cli scrape "$@"
