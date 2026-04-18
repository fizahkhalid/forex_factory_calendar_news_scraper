import os
import time
from datetime import datetime, timezone

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from .config import ALLOWED_ELEMENT_TYPES, ICON_COLOR_MAP
from .models import ScrapeContext


class ForexFactoryScraper:
    def __init__(self, console, headless: bool = True) -> None:
        self.console = console
        self.headless = headless

    def init_driver(self) -> webdriver.Chrome:
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("window-size=1920x1080")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )

        chrome_bin = os.getenv("FF_CHROME_BIN") or os.getenv("CHROME_BIN")
        if chrome_bin:
            options.binary_location = chrome_bin

        chromedriver_path = os.getenv("FF_CHROMEDRIVER_PATH") or os.getenv("CHROMEDRIVER_PATH")
        if chromedriver_path:
            return webdriver.Chrome(service=Service(chromedriver_path), options=options)

        try:
            return webdriver.Chrome(options=options)
        except Exception:
            self.console.step("Falling back to ChromeDriverManager for WebDriver setup")
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)

    def scroll_to_end(self, driver: webdriver.Chrome) -> None:
        previous_position = None
        scroll_count = 0
        self.console.step("Scrolling calendar page to load all events")
        while True:
            current_position = driver.execute_script("return window.pageYOffset;")
            driver.execute_script("window.scrollTo(0, window.pageYOffset + 500);")
            scroll_count += 1
            if scroll_count == 1 or scroll_count % 5 == 0:
                self.console.step(
                    f"Scroll progress: step {scroll_count}, page offset {int(current_position)}"
                )
            time.sleep(2)
            if current_position == previous_position:
                self.console.step(
                    f"Reached end of calendar after {scroll_count} scroll steps"
                )
                break
            previous_position = current_position

    def parse_table(self, driver: webdriver.Chrome, month_name: str) -> list[dict]:
        data = []
        self.console.step("Parsing loaded calendar rows")
        table = driver.find_element(By.CLASS_NAME, "calendar__table")

        for row in table.find_elements(By.TAG_NAME, "tr"):
            row_data = {}
            event_id = row.get_attribute("data-event-id")

            for element in row.find_elements(By.TAG_NAME, "td"):
                class_name = element.get_attribute("class")
                if class_name not in ALLOWED_ELEMENT_TYPES:
                    continue

                class_name_key = ALLOWED_ELEMENT_TYPES.get(class_name, "cell")
                if "calendar__impact" in class_name:
                    impact_elements = element.find_elements(By.TAG_NAME, "span")
                    color = None
                    for impact in impact_elements:
                        impact_class = impact.get_attribute("class")
                        color = ICON_COLOR_MAP.get(impact_class)
                    row_data[class_name_key] = color if color else "impact"
                elif "calendar__detail" in class_name and event_id:
                    row_data[class_name_key] = (
                        f"https://www.forexfactory.com/calendar?month={month_name}#detail={event_id}"
                    )
                elif element.text:
                    row_data[class_name_key] = element.text
                else:
                    row_data[class_name_key] = "empty"

            if row_data:
                data.append(row_data)

        self.console.step(f"Parsed {len(data)} raw calendar rows")
        return data

    def resolve_month(self, month_param: str) -> tuple[str, str, int]:
        param = month_param.lower()
        now = datetime.now()
        if param == "this":
            return now.strftime("%B"), str(now.year), now.month
        if param == "next":
            next_month = (now.month % 12) + 1
            year = now.year if now.month < 12 else now.year + 1
            return datetime(year, next_month, 1).strftime("%B"), str(year), next_month
        month_number = datetime.strptime(param.capitalize(), "%B").month
        return param.capitalize(), str(now.year), month_number

    def scrape_month(
        self, month_param: str, target_timezone: str | None
    ) -> tuple[list[dict], ScrapeContext]:
        url = f"https://www.forexfactory.com/calendar?month={month_param.lower()}"
        month_name, year, month_number = self.resolve_month(month_param)
        self.console.step(f"Navigating to {url}")
        driver = self.init_driver()
        try:
            driver.get(url)
            self.console.step("Calendar page loaded, detecting browser timezone")
            source_timezone = driver.execute_script(
                "return Intl.DateTimeFormat().resolvedOptions().timeZone"
            )
            self.console.step(f"Browser timezone detected as {source_timezone}")
            self.scroll_to_end(driver)
            rows = self.parse_table(driver, month_name)
            context = ScrapeContext(
                month_param=month_param.lower(),
                month_name=month_name,
                month_slug=f"{year}-{month_number:02d}",
                year=year,
                source_timezone=source_timezone,
                target_timezone=target_timezone,
                scraped_at=datetime.now(timezone.utc).isoformat(),
            )
            return rows, context
        finally:
            driver.quit()
