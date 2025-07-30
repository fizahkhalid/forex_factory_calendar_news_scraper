import time
import argparse
import json
import pandas as pd
from datetime import datetime
from config import ALLOWED_ELEMENT_TYPES, ICON_COLOR_MAP
from utils import save_csv
import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def init_driver(headless=True) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("window-size=1920x1080")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    print("Attempting to initialize WebDriver with ChromeDriverManager...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("WebDriver initialized successfully using ChromeDriverManager.")
    return driver


def scroll_to_end(driver):
    previous_position = None
    while True:
        current_position = driver.execute_script("return window.pageYOffset;")
        driver.execute_script("window.scrollTo(0, window.pageYOffset + 500);")
        time.sleep(2)
        if current_position == previous_position:
            break
        previous_position = current_position


def parse_table(driver, month, year):
    data = []
    table = driver.find_element(By.CLASS_NAME, "calendar__table")

    for row in table.find_elements(By.TAG_NAME, "tr"):
        row_data = {}
        event_id = row.get_attribute("data-event-id")

        for element in row.find_elements(By.TAG_NAME, "td"):
            class_name = element.get_attribute('class')

            if class_name in ALLOWED_ELEMENT_TYPES:
                class_name_key = ALLOWED_ELEMENT_TYPES.get(
                    f"{class_name}", "cell")

                if "calendar__impact" in class_name:
                    impact_elements = element.find_elements(
                        By.TAG_NAME, "span")
                    color = None
                    for impact in impact_elements:
                        impact_class = impact.get_attribute("class")
                        color = ICON_COLOR_MAP.get(impact_class)
                    row_data[f"{class_name_key}"] = color if color else "impact"

                elif "calendar__detail" in class_name and event_id:
                    detail_url = f"https://www.forexfactory.com/calendar?month={month}#detail={event_id}"
                    row_data[f"{class_name_key}"] = detail_url

                elif element.text:
                    row_data[f"{class_name_key}"] = element.text
                else:
                    row_data[f"{class_name_key}"] = "empty"

        if row_data:
            data.append(row_data)

    save_csv(data, month, year)

    return data, month


def get_target_month(arg_month=None):
    now = datetime.now()
    month = arg_month if arg_month else now.strftime("%B")
    year = now.strftime("%Y")
    return month, year


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Forex Factory calendar.")
    parser.add_argument("--months", nargs="+",
                        help='Target months: e.g., this next')

    args = parser.parse_args()
    month_params = args.months if args.months else ["this"]

    for param in month_params:
        param = param.lower()
        url = f"https://www.forexfactory.com/calendar?month={param}"
        print(f"\n[INFO] Navigating to {url}")

        driver = init_driver()
        driver.get(url)
        detected_tz = driver.execute_script("return Intl.DateTimeFormat().resolvedOptions().timeZone")
        print(f"[INFO] Browser timezone: {detected_tz}")
        config.SCRAPER_TIMEZONE = detected_tz
        scroll_to_end(driver)

        # Determine readable month name and year
        if param == "this":
            now = datetime.now()
            month = now.strftime("%B")
            year = now.year
        elif param == "next":
            now = datetime.now()
            next_month = (now.month % 12) + 1
            year = now.year if now.month < 12 else now.year + 1
            month = datetime(year, next_month, 1).strftime("%B")
        else:
            month = param.capitalize()
            year = datetime.now().year

        print(f"[INFO] Scraping data for {month} {year}")
        try:
            parse_table(driver, month, str(year))
        except Exception as e:
            print(f"[ERROR] Failed to scrape {param} ({month} {year}): {e}")

        driver.quit()  #  Kill the driver cleanly after each scrape
        time.sleep(3)


if __name__ == "__main__":
    main()
