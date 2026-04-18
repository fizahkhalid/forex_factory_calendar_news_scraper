# Forex Factory Calendar Toolkit

Scrape Forex Factory news events with Python + Selenium, store them as structured data, and send configurable alerts via webhooks, Discord, or Telegram.

## At A Glance

| Area | What It Does |
| --- | --- |
| 📥 Scraping | Pulls Forex Factory calendar data into CSV and JSON files |
| ⏱ Scheduling | Runs on a schedule with Docker Compose or host cron |
| 🚨 Alerts | Triggers alerts before events based on rules you define |
| 🎯 Matching | Supports currency, impact, weekday, exact event name, and keyword matching |
| 📡 Delivery | Sends alerts to generic webhooks, Discord, and Telegram |
| 🗂 Storage | Keeps `last_run`, monthly snapshots, and timestamped history |
| 🖥 UI | Includes a small Streamlit UI for browsing data and editing rules/config |

## Docker Quick Start

Docker Compose is the main setup path.

1. Copy the secrets template:

```bash
cp .env.example .env
```

2. Review `config.yaml` and enable the connectors you want.

3. Start everything:

```bash
./scripts/refresh_docker.sh refresh
```

That starts:

- the scraper scheduler
- the alert scheduler

Useful Docker commands:

```bash
./scripts/refresh_docker.sh restart
./scripts/refresh_docker.sh down
./scripts/refresh_docker.sh status
docker compose logs -f scraper
docker compose logs -f alerts
```

Direct Compose also works:

```bash
DOCKER_UID=$(id -u) DOCKER_GID=$(id -g) docker compose up -d --build
```

If older Docker runs created root-owned files, repair them once with:

```bash
sudo chown -R "$USER:$USER" news state
```

Local webhook testing from Docker needs extra networking setup because your webhook receiver is running on your own machine. Public HTTPS webhook URLs do not have that problem.

## Local Setup

If you do not want Docker, use the local scripts instead.

Set up the environment:

```bash
./scripts/setup_env.sh
```

Then:

```bash
cp .env.example .env
./scripts/run_scraper.sh
./scripts/run_alerts.sh
./scripts/view_data.sh
```

## What Gets Generated

Runtime output lives under `news/` and is gitignored.

- `news/last_run/`
  most recent command output
- `news/monthly/`
  current canonical file for each month
- `news/history/`
  timestamped snapshots from previous runs

Each row includes:

- `timezone`
- `scraped_at`

## Alert Rules

Rules live in `rules/*.yaml`. One file equals one rule.

Example:

```yaml
name: usd-core-cpi-alert
enabled: true
match:
  currencies:
    - USD
  impacts:
    - red
  event_keywords:
    - CPI
  weekdays:
    - Wed
trigger:
  minutes_before: 10
deliver:
  - webhook_main
  - discord_main
  - telegram_main
```

This rule means:

- only USD events
- only red-impact events
- only events whose name contains `CPI`
- only on Wednesdays
- send 10 minutes before the event

Supported rule matching:

- currencies
- impacts
- exact event names
- event keywords
- weekdays

Supported delivery targets:

- generic webhook
- Discord webhook
- Telegram bot

## Configuration

Normal workflow:

1. edit `config.yaml`
2. put secrets in `.env`
3. run Docker or the helper scripts

Precedence:

1. CLI flags
2. environment variables
3. `config.yaml`
4. internal defaults

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

```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
TELEGRAM_BOT_TOKEN=123456:ABC-DEF
TELEGRAM_CHAT_ID=-1001234567890
ALERT_WEBHOOK_URL=https://example.com/webhook
ALERT_WEBHOOK_AUTH=Bearer your-token
```

## Common Commands

Scrape once:

```bash
python3 -m ff_calendar_toolkit.cli scrape
```

Run alert checks once:

```bash
python3 -m ff_calendar_toolkit.cli alerts-check
```

Show scrape schedule:

```bash
python3 -m ff_calendar_toolkit.cli schedule-info
```

Show alert schedule:

```bash
python3 -m ff_calendar_toolkit.cli alerts-schedule-info
```

## Streamlit UI

The Streamlit UI is optional. It is mainly for:

- browsing stored data
- editing rules
- editing `config.yaml`
- previewing upcoming rule matches

Launch it with:

```bash
./scripts/view_data.sh
```

## Optional Local API

There is also a small local FastAPI app in `local_api.py` for local testing and lightweight integrations.

Run it with:

```bash
.venv/bin/python local_api.py
```

## Host Cron Alternative

If you prefer host cron instead of Docker scheduling:

Weekly scrape:

```bash
0 0 * * 0 cd /path/to/repo && ./scripts/run_scraper.sh >> /tmp/forex_factory_scrape.log 2>&1
```

5-minute alert checks:

```bash
*/5 * * * * cd /path/to/repo && ./scripts/run_alerts.sh >> /tmp/forex_factory_alerts.log 2>&1
```

## Troubleshooting

- If alerts are not firing, verify that the rule is enabled, the connector is enabled, and the needed secrets exist in `.env`.
- If local files become root-owned after Docker runs, repair them with `sudo chown -R "$USER:$USER" news state`.
- If you are testing against a webhook on your own machine, expect some extra local networking setup. Public webhook URLs are simpler.

## Notes

This project is intended for educational and informational use. Respect Forex Factory's terms of service and applicable laws. The site may change over time, which can require scraper updates.
