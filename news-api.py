import time
import json
import threading
from datetime import datetime
from flask import Flask, jsonify
from scraper import scrape_news  # <--- this is the key

DATA_FILE = "daily_news.json"
SCRAPE_INTERVAL = 300  # 5 minutes

app = Flask(__name__)


def scrape_and_save_daily_news():
    while True:
        today = datetime.now().strftime("%b%d.%Y").lower()
        try:
            data = scrape_news(mode="day", date_str=today)
            with open(DATA_FILE, "w") as f:
                json.dump({"date": today, "data": data}, f, indent=2)
        except Exception as e:
            print(f"Scrape error: {e}")
        time.sleep(SCRAPE_INTERVAL)


@app.route("/news", methods=["GET"])
def get_daily_news():
    try:
        with open(DATA_FILE, "r") as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({"error": "Data not yet available."}), 503


if __name__ == "__main__":
    threading.Thread(target=scrape_and_save_daily_news, daemon=True).start()
    app.run(debug=True)
