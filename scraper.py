import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.webdriver import WebDriver # Added for type hinting

from config import ALLOWED_ELEMENT_TYPES, ICON_COLOR_MAP
from utils import reformat_scraped_data


def init_driver() -> WebDriver:
    """Initializes and returns a Chrome WebDriver instance.

    Attempts to initialize a Chrome WebDriver. If a WebDriverException occurs
    (e.g., chromedriver is not in PATH or is incompatible), it attempts
    to download and install the correct version using ChromeDriverManager.

    Returns:
        WebDriver: An instance of the Chrome WebDriver.

    Raises:
        WebDriverException: If the WebDriver cannot be initialized even after
                            attempting to install with ChromeDriverManager.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run headless
    options.add_argument("--no-sandbox")  # Bypass OS security model, REQUIRED for Docker/sandboxed envs
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    options.add_argument("--disable-gpu")  # Applicable to windows os only
    options.add_argument("window-size=1920x1080") # Set window size
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")


    # Simplified: Directly use webdriver.Chrome with options, bypassing ChromeDriverManager
    # as ChromeDriverManager was causing issues in this environment.
    print("Attempting to initialize WebDriver directly with options...")
    try:
        driver = webdriver.Chrome(options=options)
        print("WebDriver initialized successfully directly.")
        return driver
    except Exception as e_direct:
        print(f"Direct WebDriver initialization failed: {e_direct}")
        raise  # Re-raise the exception if direct initialization fails


def scroll_to_bottom(driver: WebDriver, scroll_pause_time: float = 0.5, max_attempts: int = 5) -> None:
    """Scrolls to the bottom of the current page.

    The function simulates scrolling down the page by repeatedly executing
    JavaScript to scroll by a fixed amount. It monitors the scroll position
    and stops if the position doesn't change after a certain number of
    attempts, or if the bottom of the page is reached.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        scroll_pause_time (float): Time in seconds to wait between scroll attempts
                                   and for new content to load.
        max_attempts (int): Maximum number of times to attempt scrolling
                            if the scroll position doesn't change.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    attempts = 0

    while True:
        # Scroll down by a portion of the window height
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            attempts += 1
            if attempts >= max_attempts:
                break  # Exit if scroll position hasn't changed after max_attempts
        else:
            attempts = 0  # Reset attempts if there was a change

        last_height = new_height


def extract_data_from_table(table_element: WebDriver) -> list[list[str]]:
    """Extracts data from a table WebElement.

    Iterates through rows and cells of the given table element, processing
    each row using the _process_row helper function.

    Args:
        table_element (WebDriver): The Selenium WebElement representing the table.

    Returns:
        list[list[str]]: A list of lists, where each inner list represents a row
                         of extracted data from the table.
    """
    extracted_data = []
    for row_element in table_element.find_elements(By.TAG_NAME, "tr"):
        processed_row_data = _process_row(row_element)  # Delegate to _process_row
        if processed_row_data:
            extracted_data.append(processed_row_data)
    return extracted_data


def _extract_impact_color(cell_element: WebDriver) -> str:
    """Extracts the impact color from a table cell WebElement.

    Searches for span elements within the cell that indicate impact level
    (e.g., high, medium, low) and maps their class names to a color string
    using ICON_COLOR_MAP.

    Args:
        cell_element (WebDriver): The Selenium WebElement for the table cell.

    Returns:
        str: The determined impact color string (e.g., "red", "orange", "yellow")
             or a default value "impact" if no specific color is found.
    """
    impact_elements = cell_element.find_elements(By.TAG_NAME, "span")
    color = None
    for impact_span in impact_elements:
        impact_class = impact_span.get_attribute("class")
        # Prefer the color from ICON_COLOR_MAP if available
        if impact_class in ICON_COLOR_MAP:
            color = ICON_COLOR_MAP[impact_class]
            break  # Found the most specific color
    return color or "impact"  # Default if no color found or no spans


def _process_row(row_element: WebDriver) -> list[str]:
    """Processes a single table row WebElement to extract its data.

    Iterates through the cells (td elements) of the row, extracting text
    content or determining impact color for relevant cells.

    Args:
        row_element (WebDriver): The Selenium WebElement for the table row (tr).

    Returns:
        list[str]: A list of strings representing the data extracted from the row.
                   Returns an empty list if the row contains no processable cells.
    """
    row_data = []
    for cell_element in row_element.find_elements(By.TAG_NAME, "td"):
        class_name = cell_element.get_attribute('class')
        if class_name in ALLOWED_ELEMENT_TYPES:
            element_text = cell_element.text
            if element_text:
                row_data.append(element_text)
            elif "calendar__impact" in class_name:
                impact_color = _extract_impact_color(cell_element)
                row_data.append(impact_color)
            else:
                row_data.append('-')  # Default for empty but allowed cells
    return row_data


def scrape_news(mode: str = "day", date_str: str = "may25.2025") -> list[list[str]]:
    """Scrapes news data from Forex Factory for a given date and mode.

    Initializes a WebDriver, navigates to the Forex Factory calendar page
    for the specified date and mode (day/month), scrolls to ensure all data
    is loaded, and then extracts data from the calendar table.

    Args:
        mode (str): The mode for scraping, either "day" or "month".
                    Defaults to "day".
        date_str (str): The date string for scraping (e.g., "may25.2025").
                        Defaults to "may25.2025".

    Returns:
        list[list[str]]: A list of lists containing the scraped data.
    """
    driver = init_driver()
    try:
        url = f"https://www.forexfactory.com/calendar?{mode}={date_str.lower()}"
        driver.get(url)
        scroll_to_bottom(driver)
        table_element = driver.find_element(By.CLASS_NAME, "calendar__table")
        return extract_data_from_table(table_element)
    finally:
        driver.quit()


def main() -> None:
    """Main function to parse arguments and initiate scraping.

    Parses command-line arguments for date and mode, then calls
    the scrape_news function to get data, and finally reformats
    the scraped data.
    """
    parser = argparse.ArgumentParser(description="Scrape Forex Factory news calendar.")
    parser.add_argument(
        '--date',
        type=str,
        default='this',
        help='Date to scrape (e.g., "may.2025" or "may27.2025" or "this" for current day/month)'
    )
    parser.add_argument(
        '--mode',
        type=str,
        choices=['month', 'day'],
        default='month',
        help='Mode to scrape: "month" or "day". Default is "month".'
    )

    args = parser.parse_args()
    scraped_data = scrape_news(mode=args.mode, date_str=args.date.lower())
    reformat_scraped_data(scraped_data, args.date.lower())


if __name__ == "__main__":
    main()
