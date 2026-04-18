#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_NAME="${IMAGE_NAME:-forex-factory-toolkit}"
SCRAPER_CONTAINER="${SCRAPER_CONTAINER:-forex-factory-scraper}"
ALERTS_CONTAINER="${ALERTS_CONTAINER:-forex-factory-alerts}"
MODE="${1:-refresh}"
DOCKER_UID="${DOCKER_UID:-$(id -u)}"
DOCKER_GID="${DOCKER_GID:-$(id -g)}"

compose_available() {
  docker compose version >/dev/null 2>&1
}

build_image() {
  echo "Building Docker image ${IMAGE_NAME} (raw Docker mode)"
  docker build -t "${IMAGE_NAME}" "${ROOT_DIR}"
}

stop_and_remove() {
  local container_name="$1"
  if docker ps -a --format '{{.Names}}' | grep -Fxq "${container_name}"; then
    echo "Stopping ${container_name}"
    docker stop "${container_name}" >/dev/null 2>&1 || true
    echo "Removing ${container_name}"
    docker rm "${container_name}" >/dev/null 2>&1 || true
  fi
}

down_raw() {
  stop_and_remove "${SCRAPER_CONTAINER}"
  stop_and_remove "${ALERTS_CONTAINER}"
}

cleanup_compose_name_conflicts() {
  stop_and_remove "${SCRAPER_CONTAINER}"
  stop_and_remove "${ALERTS_CONTAINER}"
}

up_raw() {
  mkdir -p "${ROOT_DIR}/news" "${ROOT_DIR}/rules" "${ROOT_DIR}/state"

  echo "Starting ${SCRAPER_CONTAINER}"
  docker run -d \
    --name "${SCRAPER_CONTAINER}" \
    --restart unless-stopped \
    --user "${DOCKER_UID}:${DOCKER_GID}" \
    --add-host host.docker.internal:host-gateway \
    -e FF_RUN_MODE="schedule" \
    -v "${ROOT_DIR}/config.yaml:/app/config.yaml" \
    -v "${ROOT_DIR}/.env:/app/.env" \
    -v "${ROOT_DIR}/news:/app/news" \
    -v "${ROOT_DIR}/rules:/app/rules" \
    -v "${ROOT_DIR}/state:/app/state" \
    "${IMAGE_NAME}" >/dev/null

  echo "Starting ${ALERTS_CONTAINER}"
  docker run -d \
    --name "${ALERTS_CONTAINER}" \
    --restart unless-stopped \
    --user "${DOCKER_UID}:${DOCKER_GID}" \
    --add-host host.docker.internal:host-gateway \
    -e FF_RUN_MODE="alerts-schedule" \
    -v "${ROOT_DIR}/config.yaml:/app/config.yaml" \
    -v "${ROOT_DIR}/.env:/app/.env" \
    -v "${ROOT_DIR}/news:/app/news" \
    -v "${ROOT_DIR}/rules:/app/rules" \
    -v "${ROOT_DIR}/state:/app/state" \
    "${IMAGE_NAME}" >/dev/null
}

status_raw() {
  docker ps --filter "name=${SCRAPER_CONTAINER}" --filter "name=${ALERTS_CONTAINER}"
}

down_compose() {
  (
    cd "${ROOT_DIR}"
    DOCKER_UID="${DOCKER_UID}" DOCKER_GID="${DOCKER_GID}" docker compose down
  )
}

up_compose() {
  mkdir -p "${ROOT_DIR}/news" "${ROOT_DIR}/rules" "${ROOT_DIR}/state"
  cleanup_compose_name_conflicts
  (
    cd "${ROOT_DIR}"
    DOCKER_UID="${DOCKER_UID}" DOCKER_GID="${DOCKER_GID}" docker compose up -d "$@"
  )
}

build_compose() {
  (
    cd "${ROOT_DIR}"
    DOCKER_UID="${DOCKER_UID}" DOCKER_GID="${DOCKER_GID}" docker compose build
  )
}

status_compose() {
  (
    cd "${ROOT_DIR}"
    DOCKER_UID="${DOCKER_UID}" DOCKER_GID="${DOCKER_GID}" docker compose ps
  )
}

down() {
  if compose_available; then
    down_compose
  else
    down_raw
  fi
}

up() {
  if compose_available; then
    up_compose
  else
    up_raw
  fi
}

build() {
  if compose_available; then
    build_compose
  else
    build_image
  fi
}

status() {
  if compose_available; then
    status_compose
  else
    status_raw
  fi
}

usage() {
  cat <<'EOF'
Usage:
  ./scripts/refresh_docker.sh [refresh|build|down|up|restart|status]

Commands:
  refresh  Stop old containers, rebuild services, and start scraper + alerts
  restart  Stop old containers and start scraper + alerts without rebuilding
  build    Build services only
  down     Stop and remove scraper + alerts containers
  up       Start scraper + alerts containers
  status   Show running scraper + alerts containers

Notes:
  - Uses `docker compose` automatically when available and falls back to raw Docker otherwise.
  - Exports your current UID/GID to keep files in `news/` and `state/` editable.
EOF
}

case "${MODE}" in
  refresh)
    if compose_available; then
      down_compose
      up_compose --build
      status_compose
    else
      down_raw
      build_image
      up_raw
      status_raw
    fi
    ;;
  restart)
    down
    up
    status
    ;;
  build)
    build
    ;;
  down)
    down
    ;;
  up)
    up
    status
    ;;
  status)
    status
    ;;
  *)
    usage
    exit 1
    ;;
esac
