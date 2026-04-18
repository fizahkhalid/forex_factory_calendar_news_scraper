# Forex Factory Calendar Toolkit

Forex Factory Calendar Toolkit is a local-first **economic calendar data and alerting toolkit** built around Forex Factory.

It is no longer just a scraper. It gives you a practical workflow for:

- collecting Forex Factory calendar events into clean CSV and JSON datasets
- keeping reusable monthly snapshots and per-run history
- previewing and filtering events through a local UI and local API
- creating alert rules for high-impact calendar events
- delivering notifications to Discord, Telegram, or generic webhooks

If you trade, automate, research macro events, or build tools around economic calendars, this repo is meant to make the data immediately usable instead of leaving it trapped inside a browser page.

## Why This Repo

This toolkit is designed to cover the full local workflow around economic calendar data:

- **Scrape**: collect current month economic calendar data from Forex Factory
- **Store**: keep structured local datasets in CSV and JSON
- **Monitor**: evaluate rules against stored events on a recurring schedule
- **Alert**: push matching events to webhook-based destinations before they happen
- **Operate**: manage the setup through YAML, `.env`, Streamlit, Docker, and helper scripts

## Highlights

- YAML-first config with `config.yaml`
- `.env` for secrets and connector credentials
- Forex Factory calendar scraping with local CSV and JSON outputs
- ISO-style output layout with `last_run/`, `monthly/`, and `history/`
- 5-minute alert checks and weekly scrape refresh by default
- modular connectors for webhook, Discord, and Telegram
- one rule per YAML file under `rules/`
- Streamlit UI for browsing data, editing rules, editing config, and inspecting alert state
- local FastAPI endpoint for serving stored events and alert previews

## Use Cases

- Build a personal macro-event dashboard from Forex Factory calendar data
- Trigger webhook automations before high-impact news events
- Feed a local API for bots, dashboards, or lightweight integrations
- Keep a monthly archive of important economic releases
- Test alert logic locally before wiring it into a larger system

## Quick Start

Set up a local environment:

```bash
./scripts/setup_env.sh
```

The setup script creates a repo-local environment and helper scripts prefer that environment automatically when `.venv/` exists.

Copy the secrets template if you want alerts:

```bash
cp .env.example .env
```

Edit `config.yaml`, then scrape once:

```bash
./scripts/run_scraper.sh
```

Run alert checks once:

```bash
./scripts/run_alerts.sh
```

Launch the local UI:

```bash
./scripts/view_data.sh
```

Run the local API:

```bash
.venv/bin/python local_api.py
```

## Configuration Model

Normal workflow:

1. edit `config.yaml`
2. put secrets in `.env`
3. run helper scripts without repeating flags

Precedence:

1. CLI flags
2. environment variables
3. `config.yaml`
4. internal defaults

`config.yaml` controls normal toolkit behavior. `.env` is for secrets and automation overrides.

### Example `config.yaml`

```yaml
months:
  - this
output_format: both
output_dir: news
timezone: Asia/Karachi
allowed_currencies:
  - CAD
  - EUR
  - GBP
  - USD
allowed_impacts:
  - red
  - orange
  - gray
headless: true
schedule_preset: weekly
viewer_host: 127.0.0.1
viewer_port: 8501
alerts:
  rules_dir: rules
  state_dir: state/alerts
  check_interval_minutes: 5
  schedule_preset: every_5_minutes
  retry_attempts: 3
  retry_backoff_seconds: 1
  message_prefix: "Forex Factory Alert"
  connectors:
    - id: discord_main
      type: discord
      enabled: false
      webhook_url_env: DISCORD_WEBHOOK_URL
    - id: telegram_main
      type: telegram
      enabled: false
      bot_token_env: TELEGRAM_BOT_TOKEN
      chat_id_env: TELEGRAM_CHAT_ID
    - id: webhook_main
      type: webhook
      enabled: false
      url_env: ALERT_WEBHOOK_URL
      auth_header_name: Authorization
      auth_header_env: ALERT_WEBHOOK_AUTH
```

### Example `.env`

Use `.env.example` as the reference:

```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
TELEGRAM_BOT_TOKEN=123456:ABC-DEF
TELEGRAM_CHAT_ID=-1001234567890
ALERT_WEBHOOK_URL=https://example.com/webhook
ALERT_WEBHOOK_AUTH=Bearer your-token
```

### Webhook Networking Note

For most real-world setups, `ALERT_WEBHOOK_URL` will point to a public HTTPS endpoint and Docker networking is not a special concern.

Examples:

- `https://api.example.com/alerts/webhook`
- `https://hooks.slack.com/...`
- `https://discord.com/api/webhooks/...`

Local webhook testing is the special case:

- if you run alerts on the host with `./scripts/run_alerts.sh`, use `http://127.0.0.1:8765/...`
- if you run alerts inside Docker Compose, use `http://host.docker.internal:8765/...`

If you want Docker or another machine to hit a webhook receiver running locally on your laptop, exposing it with a tunnel such as `ngrok` is often the simplest option. In that case, use the public `https://...ngrok...` URL as `ALERT_WEBHOOK_URL`.

## Local API

The repo also includes a small local API for serving stored events and alert previews from your generated files.

Default address:

```bash
http://127.0.0.1:8765
```

Endpoints:

- `/health`
- `/datasets`
- `/events`
- `/events/upcoming`
- `/alerts/preview`
- `/webhook-test`
- `/webhook-test/received`

Examples:

```bash
curl http://127.0.0.1:8765/health
curl "http://127.0.0.1:8765/events?currency=USD&impact=red&limit=5"
curl http://127.0.0.1:8765/alerts/preview
```

## CLI Commands

Scrape once:

```bash
python3 -m ff_calendar_toolkit.cli scrape
```

Run alert checks once:

```bash
python3 -m ff_calendar_toolkit.cli alerts-check
```

Launch Streamlit:

```bash
python3 -m ff_calendar_toolkit.cli view
```

Run the local API:

```bash
.venv/bin/python local_api.py
```

Show scrape schedule:

```bash
python3 -m ff_calendar_toolkit.cli schedule-info
```

Show alert schedule:

```bash
python3 -m ff_calendar_toolkit.cli alerts-schedule-info
```

## Output Layout

Generated runtime data lives under `news/` and is gitignored.

- `news/last_run/2026-04.csv`
- `news/last_run/2026-04.json`
- `news/monthly/2026-04.csv`
- `news/monthly/2026-04.json`
- `news/history/2026-04/2026-04-19T01-27-21+0500.csv`
- `news/history/2026-04/2026-04-19T01-27-21+0500.json`

Meaning:

- `last_run/` contains only the most recent command output
- `monthly/` is the current canonical file for each month
- `history/` keeps timestamped snapshots for each run

Each row includes:

- `timezone`
- `scraped_at`

## Alert Rules

Rules live in `rules/*.yaml`. One file equals one rule.

Example rule:

```yaml
name: usd-core-cpi-alert
enabled: true
match:
  currencies:
    - USD
  impacts:
    - red
  event_names:
    - Core CPI m/m
  event_keywords:
    - CPI
  weekdays:
    - Wed
trigger:
  minutes_before: 10
deliver:
  - discord_main
  - telegram_main
  - webhook_main
```

What this does:

- looks for USD events
- only matches red-impact events
- matches either the exact event name `Core CPI m/m` or event text containing `CPI`
- only triggers on Wednesdays
- sends the alert 10 minutes before the event
- delivers that same alert through Discord, Telegram, and a generic webhook connector

Supported v1 rule matching:

- currency
- impact
- exact event names
- event keywords
- weekday
- enabled or disabled

Supported v1 trigger behavior:

- `minutes_before`

Deduplication is persistent. The toolkit records what was already sent so the same rule-event-trigger combination is not repeatedly posted on every alert check.

## Streamlit UI

The UI is a local control panel for:

- browsing stored data
- creating and editing rules
- editing `config.yaml`
- previewing upcoming rule matches
- viewing sent-alert and failure state

Launch it with:

```bash
./scripts/view_data.sh
```

The UI edits files directly. `rules/` and `config.yaml` remain the source of truth.

## Docker

Recommended path: use Docker Compose so the scraper and alert scheduler are managed together and runtime files stay owned by your local user.

Start or refresh everything:

```bash
./scripts/refresh_docker.sh refresh
```

That script:

- stops old scraper and alert containers
- recreates the services, rebuilding when needed
- starts both services again
- passes your local UID/GID so files created in `news/` and `state/` stay editable

Other useful commands:

```bash
./scripts/refresh_docker.sh restart
./scripts/refresh_docker.sh down
./scripts/refresh_docker.sh up
./scripts/refresh_docker.sh status
```

Compose commands:

```bash
docker compose up -d
docker compose up -d --build
docker compose ps
docker compose logs -f scraper
docker compose logs -f alerts
docker compose down
```

If you prefer Compose directly, this is usually enough:

```bash
DOCKER_UID=$(id -u) DOCKER_GID=$(id -g) docker compose up -d --build
```

If you previously started the scraper or alerts with raw `docker run`, the helper script now cleans up those old same-name containers automatically before Compose starts.

Manual `docker run` usage is still possible, but it is now the fallback path rather than the recommended one.

### Manual Docker Fallback

Manual image build:

```bash
docker build -t forex-factory-toolkit .
```

Run one scrape:

```bash
docker run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$(pwd)/config.yaml:/app/config.yaml" \
  -v "$(pwd)/.env:/app/.env" \
  -v "$(pwd)/news:/app/news" \
  -v "$(pwd)/rules:/app/rules" \
  -v "$(pwd)/state:/app/state" \
  forex-factory-toolkit
```

Run the weekly scrape scheduler in the background:

```bash
docker run -d \
  --name forex-factory-scraper \
  --restart unless-stopped \
  --user "$(id -u):$(id -g)" \
  -e FF_RUN_MODE="schedule" \
  -v "$(pwd)/config.yaml:/app/config.yaml" \
  -v "$(pwd)/.env:/app/.env" \
  -v "$(pwd)/news:/app/news" \
  -v "$(pwd)/rules:/app/rules" \
  -v "$(pwd)/state:/app/state" \
  forex-factory-toolkit
```

Run the 5-minute alert scheduler in the background:

```bash
docker run -d \
  --name forex-factory-alerts \
  --restart unless-stopped \
  --user "$(id -u):$(id -g)" \
  -e FF_RUN_MODE="alerts-schedule" \
  -v "$(pwd)/config.yaml:/app/config.yaml" \
  -v "$(pwd)/.env:/app/.env" \
  -v "$(pwd)/news:/app/news" \
  -v "$(pwd)/rules:/app/rules" \
  -v "$(pwd)/state:/app/state" \
  forex-factory-toolkit
```

That container keeps running in the background. You do not need to rerun it every 5 minutes. The scheduler loop inside the container keeps triggering `alerts-check`.

Useful raw Docker commands:

```bash
docker ps
docker logs -f forex-factory-scraper
docker logs -f forex-factory-alerts
docker restart forex-factory-scraper
docker restart forex-factory-alerts
```

If older Docker runs already created root-owned files, repair them once with:

```bash
sudo chown -R "$USER:$USER" news state
```

## Host Cron Alternative

If you prefer host cron:

Weekly scrape:

```bash
0 0 * * 0 cd /path/to/repo && ./scripts/run_scraper.sh >> /tmp/forex_factory_scrape.log 2>&1
```

5-minute alert checks:

```bash
*/5 * * * * cd /path/to/repo && ./scripts/run_alerts.sh >> /tmp/forex_factory_alerts.log 2>&1
```

## Project Structure

- `config.yaml`: default non-secret configuration
- `.env.example`: secret/reference template
- `local_api.py`: local FastAPI server for stored events and alert previews
- `rules/`: one rule file per alert rule
- `ff_calendar_toolkit/cli.py`: main entrypoint
- `ff_calendar_toolkit/service.py`: scrape orchestration
- `ff_calendar_toolkit/alerts/`: alert engine, rule loading, state, and connectors
- `ff_calendar_toolkit/viewer.py`: Streamlit UI
- `docker/entrypoint.sh`: Docker run modes
- `scripts/setup_env.sh`: local environment setup
- `scripts/run_scraper.sh`: local scrape command
- `scripts/run_alerts.sh`: local alert-check command
- `scripts/view_data.sh`: local UI command

## Troubleshooting

- If helper scripts do not use the right interpreter, check whether `.venv/` exists and contains `bin/python`.
- If the viewer shows no data, run the scraper first so `news/monthly/*.json` or `news/last_run/*.json` exists.
- If the local API has nothing useful to serve, make sure you have already generated `news/*.json` outputs.
- If alerts are not firing, verify:
  - the rule is enabled
  - the connector is enabled in `config.yaml`
  - the required secret env vars exist in `.env`
  - the event time and timezone in stored data are correct
- Runtime outputs under `news/` and alert state under `state/` are intentionally gitignored.

## Notes

This project is intended for educational and informational use. Respect Forex Factory's terms of service and applicable laws. The site may change over time, which can require scraper updates.
