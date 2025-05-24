# 📈 Forex Factory News Event Scraper

A modular and powerful Python scraper for retrieving **Forex Factory news events**! 🚀 Built with **Selenium**, this project includes:

- 🔄 A background job that scrapes daily news every 5 minutes
- 🧩 Modular design (separates scraping logic for reusability)
- 🌐 Optional Flask API to serve scraped news (as a side feature)

---

## 🗂 Project Structure

```
├── scraper.py          # Contains reusable scraping logic
├── api_server.py       # Runs optional Flask API + background job
├── config.py           # Configs for filtering and impact mappings
├── utils.py            # Utility functions for formatting data
├── daily_news.json     # Output file updated every 5 minutes
├── requirements.txt    # Dependencies
└── README.md           # This guide 📘
```

---

## 🧰 Installation & Setup

✅ Make sure Python 3 is installed, then:

```bash
python3 -m pip install -r requirements.txt
```

---

## 📅 How to Retrieve Data

### 🔹 Option 1: Manual Scraping with CLI

Use the `scraper.py` to scrape data manually:

- **By Day** (to scrape a specific day):
```bash
python3 scraper.py --mode day --date may25.2025
```
Loads: `https://www.forexfactory.com/calendar?day=may25.2025`

- **By Month** (to scrape a full month):
```bash
python3 scraper.py --mode month --date may.2025
```
Loads: `https://www.forexfactory.com/calendar?month=may.2025`

This approach runs the scraper and saves formatted data manually.

### 🔹 Option 2: Optional API with Auto-Updating Background Job

If you prefer an always-up-to-date source:
- A background thread scrapes today's news every 5 minutes
- The latest result is saved to `daily_news.json`
- A Flask API provides access to that data

To run the API server:
```bash
python3 api_server.py
```

Access the news:
```
GET http://localhost:5000/news
```

Returns:
```json
{
  "data": [
    [
      "Tue\nMay 27",
      "1:01am",
      "GBP",
      "yellow",
      "BRC Shop Price Index y/y",
      "-",
      "0.0%",
      "-0.1%"
    ],
    [
      "1:50am",
      "JPY",
      "yellow",
      "SPPI y/y",
      "-",
      "3.0%",
      "3.1%"
    ],
    [
      "7:00am",
      "JPY",
      "yellow",
      "BOJ Core CPI y/y",
      "-",
      "2.3%",
      "2.2%"
    ],
    [
      "8:00am",
      "CHF",
      "yellow",
      "Trade Balance",
      "-",
      "5.55B",
      "6.35B"
    ],
    [
      "6:20pm",
      "CHF",
      "orange",
      "SNB Chairman Schlegel Speaks",
      "-",
      "-",
      "-"
    ]
  ],
  "date": "may27.2025"
}
```

This feature is optional and intended for developers who want to expose the data over HTTP.

---

## ⚙️ Chrome WebDriver

This project uses **`webdriver_manager`**, so you *don't need to install ChromeDriver manually*. If it’s missing, it auto-installs! 🛠️

Ensure you have Google Chrome installed.

---

## ⚠️ Notes & Legal

- 🧠 Educational & informational use only
- ⚖️ Respect [Forex Factory's Terms](https://www.forexfactory.com/)
- 📉 Site changes may break scraping – be ready to adapt

> **Disclaimer**: Use responsibly. Comply with laws, terms of service, and robots.txt.

---

## 🎉 That’s It!
You now have a modular Forex calendar scraper that supports both **manual and automated** usage. Happy coding — and good luck trading! 💹

---

Made with ❤️ and Python 🐍