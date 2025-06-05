import time
import argparse
import json
import pandas as pd
from datetime import datetime
from config import ALLOWED_ELEMENT_TYPES, ICON_COLOR_MAP
from utils import save_csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def init_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
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



def parse_table(driver, month,year):
    data = []
    table = driver.find_element(By.CLASS_NAME, "calendar__table")

    for row in table.find_elements(By.TAG_NAME, "tr"):
        row_data = {}
        for element in row.find_elements(By.TAG_NAME, "td"):
            class_name = element.get_attribute('class')
            if class_name in ALLOWED_ELEMENT_TYPES:
                class_name_key = ALLOWED_ELEMENT_TYPES.get(f"{class_name}","cell")
                if element.text:
                    row_data[f"{class_name_key}"] = element.text
                elif "calendar__impact" in class_name:
                    impact_elements = element.find_elements(By.TAG_NAME, "span")
                    color = None
                    for impact in impact_elements:
                        impact_class = impact.get_attribute("class")
                        color = ICON_COLOR_MAP.get(impact_class)
                    row_data[f"{class_name_key}"] = color if color else "impact"
                else:
                    row_data[f"{class_name_key}"] = "empty"

        if row_data:
            data.append(row_data)

    

    save_csv(data, month, year)

    return data,month


def get_target_month(arg_month=None):
    now = datetime.now()
    month = arg_month if arg_month else now.strftime("%B")
    year = now.strftime("%Y")
    return month, year


def main():
    parser = argparse.ArgumentParser(description="Scrape Forex Factory calendar.")
    parser.add_argument("--month", type=str, help="Target month (e.g. June, July). Defaults to current month.")

    args = parser.parse_args()

    month,year = get_target_month(args.month)

    url_param = "this" if not args.month else args.month.lower()
    url = f"https://www.forexfactory.com/calendar?month={url_param}"

    driver = init_driver()
    driver.get(url)
    scroll_to_end(driver)
    parse_table(driver, month,year)
    driver.quit()

if __name__ == "__main__":
    main()