import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from config import ALLOWED_ELEMENT_TYPES, ICON_COLOR_MAP
from utils import reformat_scraped_data


def init_driver():
    try:
        return webdriver.Chrome()
    except WebDriverException:
        print("AF: No Chrome webdriver installed, attempting to install with ChromeDriverManager...")
        return webdriver.Chrome(ChromeDriverManager().install())


def scroll_to_bottom(driver):
    while True:
        before_scroll = driver.execute_script("return window.pageYOffset;")
        driver.execute_script("window.scrollTo(0, window.pageYOffset + 500);")
        time.sleep(2)
        after_scroll = driver.execute_script("return window.pageYOffset;")
        if before_scroll == after_scroll:
            break


def scrape_calendar_data(table):
    data = []
    for row in table.find_elements(By.TAG_NAME, "tr"):
        row_data = []
        for element in row.find_elements(By.TAG_NAME, "td"):
            class_name = element.get_attribute('class')
            if class_name in ALLOWED_ELEMENT_TYPES:
                if element.text:
                    row_data.append(element.text)
                elif "calendar__impact" in class_name:
                    impact_elements = element.find_elements(By.TAG_NAME, "span")
                    color = None
                    for impact in impact_elements:
                        impact_class = impact.get_attribute("class")
                        color = ICON_COLOR_MAP.get(impact_class, "impact")
                    row_data.append(color or "impact")
                else:
                    row_data.append('-')
        if row_data:
            data.append(row_data)
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=str, default='this', help='Date to scrape (e.g., "may.2025" or "may27.2025")')
    parser.add_argument('--mode', type=str, choices=['month', 'day'], default='month',
                        help='Mode to scrape: "month" or "day"')
    args = parser.parse_args()

    driver = init_driver()
    url = f"https://www.forexfactory.com/calendar?{args.mode}={args.date.lower()}"
    driver.get(url)

    scroll_to_bottom(driver)
    table = driver.find_element(By.CLASS_NAME, "calendar__table")
    data = scrape_calendar_data(table)

    reformat_scraped_data(data, args.date.lower())


if __name__ == "__main__":
    main()
