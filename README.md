# Forex Factory Calendar Scraper & Alert System

Python scraper for the [Forex Factory](https://www.forexfactory.com/calendar) economic calendar. Pulls monthly events into structured CSV/JSON, filters by currency and impact, converts timezones, and fires configurable pre-event alerts to Discord, Telegram, or any HTTP webhook.

## Features

- Scrapes the full FF economic calendar — currency, impact, time, event name, detail URL
- Filter by currency (USD, EUR, GBP, CAD, JPY, ...) and impact level (high/medium/low)
- Converts all event times to your local timezone
- Stores data in three tiers: last run, monthly canonical, and timestamped history
- Rule-based alerts: match events by currency, impact, keywords, exact name, or weekday
- Fires alerts N minutes before each matched event
- Delivers to Discord webhooks, Telegram bots, or any HTTPS endpoint
- Runs unattended via Docker Compose with built-in scheduling
- Optional Streamlit UI for browsing data and editing rules live

## Quickstart

**Docker (recommended)**

```bash
cp .env.example .env
# add connector secrets to .env, enable connectors in config.yaml
./scripts/refresh_docker.sh refresh
```

That builds the image, starts the scraper scheduler and the alert checker, and prints their status. Common management commands:

```bash
./scripts/refresh_docker.sh restart   # restart without rebuilding
./scripts/refresh_docker.sh down      # stop and remove containers
./scripts/refresh_docker.sh status    # show running containers
docker compose logs -f alerts         # tail alert logs
docker compose logs -f scraper        # tail scraper logs
```

**Local**

```bash
./scripts/setup_env.sh
cp .env.example .env
./scripts/run.sh scrape
```

## Commands

```bash
python -m ff_calendar_toolkit.cli scrape           # scrape now
python -m ff_calendar_toolkit.cli alerts-check     # check alerts now
python -m ff_calendar_toolkit.cli test-notify      # verify notification delivery
python -m ff_calendar_toolkit.cli view             # open the Streamlit UI
```

---

## Scraping

### What gets scraped

Each event row contains:

| Field | Example |
|---|---|
| `currency` | `USD` |
| `impact` | `red` |
| `date` | `2025-01-15` |
| `time` | `13:30` |
| `event` | `Core CPI m/m` |
| `detail` | `https://www.forexfactory.com/...` |
| `timezone` | `Asia/Karachi` |
| `scraped_at` | `2025-01-14T08:00:00` |

### Filtering

Control which events are stored via `config.yaml`:

```yaml
allowed_currencies:
  - USD
  - EUR
  - GBP
  - CAD

allowed_impacts:
  - red      # high impact
  - orange   # medium impact
  - gray     # low impact / holidays
```

Override at runtime with CLI flags:

```bash
python -m ff_calendar_toolkit.cli scrape --currencies USD EUR --impacts red orange
```

### Month selection

```yaml
months:
  - this     # current month
  - next     # next month
```

Or pass a specific month:

```bash
python -m ff_calendar_toolkit.cli scrape --months 2025-03
```

Multiple values are supported: `--months this next 2025-06`

### Output format and storage

```yaml
output_format: both   # csv | json | both
output_dir: news
```

Three storage tiers are written on every run:

```
news/last_run/     ← overwritten each run (easy to read latest)
news/monthly/      ← canonical file for each month (updated in place)
news/history/      ← timestamped snapshots, never overwritten
```

### Timezone conversion

```yaml
timezone: Asia/Karachi
```

All event times are converted from the Forex Factory source timezone to your configured timezone. Any [tz database name](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) works.

---

## Scheduling

Set `schedule_preset` in `config.yaml`:

**Scraper presets**

| Preset | Cron |
|---|---|
| `weekly` (default) | `0 0 * * 0` |
| `daily` | `0 0 * * *` |
| `monthly` | `0 0 1 * *` |
| `hourly` | `0 * * * *` |

**Alert check presets**

| Preset | Cron |
|---|---|
| `every_1_minute` | `* * * * *` |
| `every_5_minutes` | `*/5 * * * *` |
| `every_10_minutes` | `*/10 * * * *` |
| `hourly` | `0 * * * *` |

Use a custom cron expression instead of a preset via the `CRON_SCHEDULE` or `ALERT_CRON_SCHEDULE` env variables.

---

## Alert rules

One YAML file per rule in `rules/`. A rule fires when all `match` conditions are met.

```yaml
name: usd-cpi-alert
enabled: true
match:
  currencies: [USD]
  impacts: [red]
  event_keywords: [CPI]
  weekdays: [Wed]
trigger:
  minutes_before: 10
deliver:
  - discord_main
```

**Match fields** (all optional, combined with AND logic):

| Field | Type | Example |
|---|---|---|
| `currencies` | list | `[USD, EUR, GBP]` |
| `impacts` | list | `[red, orange]` |
| `event_names` | list | exact event name match |
| `event_keywords` | list | substring match on event name |
| `weekdays` | list | `[Mon, Tue, Wed, Thu, Fri]` |

Multiple rules can target the same connector. State is tracked so an alert fires only once per event.

---

## Notification setup

Enable connectors in `config.yaml` under `alerts.connectors`, then add secrets to `.env`.

**Discord**

Discord uses an incoming webhook URL — no bot required. To create one: open the Discord channel → Edit Channel → Integrations → Webhooks → New Webhook → Copy Webhook URL.

```yaml
- id: discord_main
  type: discord
  enabled: true
  webhook_url_env: DISCORD_WEBHOOK_URL
```

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/1234567890/xxxx
```

**Telegram**

Create a bot via [@BotFather](https://t.me/BotFather) (`/newbot`). Get your chat ID by messaging the bot, then calling `https://api.telegram.org/bot<TOKEN>/getUpdates`. Group chat IDs are negative.

```yaml
- id: telegram_main
  type: telegram
  enabled: true
  bot_token_env: TELEGRAM_BOT_TOKEN
  chat_id_env: TELEGRAM_CHAT_ID
```

```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF
TELEGRAM_CHAT_ID=-1001234567890
```

**Webhook**

Sends a JSON payload with `message`, `rule`, `event`, and `event_time` fields. Supports an optional auth header.

```yaml
- id: webhook_main
  type: webhook
  enabled: true
  url_env: ALERT_WEBHOOK_URL
  auth_header_name: Authorization
  auth_header_env: ALERT_WEBHOOK_AUTH
```

**Testing your setup**

After configuring any connector, run:

```bash
python -m ff_calendar_toolkit.cli test-notify
```

It sends a real test message through every enabled connector and prints the result:

```
ok    discord_main
ok    telegram_main
fail  webhook_main: Missing required secret environment variable 'ALERT_WEBHOOK_URL'
```

`fail` lines show the exact error — usually a missing `.env` variable or an invalid URL. Fix those before relying on live alerts.

---

## Configuration reference

Full `config.yaml` with all available keys:

```yaml
months: [this]              # this | next | YYYY-MM (list)
output_format: both         # csv | json | both
output_dir: news
timezone: UTC               # any tz database name
allowed_currencies: [USD, EUR, GBP, CAD]
allowed_impacts: [red, orange, gray]
headless: true
schedule_preset: weekly     # weekly | daily | monthly | hourly
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
  connectors: []
```

Config precedence: **CLI flags > env vars > config.yaml > defaults**

---

## Troubleshooting

- Alerts not firing: check `enabled: true` on the rule and connector, and confirm the secret exists in `.env`
- Run `test-notify` to verify delivery works before waiting for a real event
- If the FF site changes and rows stop parsing, update selectors in `ff_calendar_toolkit/scraper.py`

---

For educational use. Respect Forex Factory's terms of service.