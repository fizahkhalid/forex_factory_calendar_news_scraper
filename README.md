# Forex Factory News Event Scraper
This project is a Python-based web scraper designed to retrieve news events for the current month from Forex Factory. It utilizes the Selenium library to automate the process of collecting data from the Forex Factory page. Here, I provide a brief overview of the project's structure and how to use it.

## Project Structure
The project consists of several Python files and a configuration file:

***scraper.py***: This is the main script responsible for scraping data from the Forex Factory calendar page. It uses Selenium to interact with the website, scroll through the page to load all events, and extract relevant data.

***utils.py***: This file contains utility functions for reading JSON data and processing text to extract relevant information from the scraped data.

***config.py***: Here, you can configure constants related to allowed HTML element types, excluded element types, impact color mapping, allowed currency codes, and allowed impact colors. These configurations help filter and categorize the scraped data.

***gui_scraper.py***: A modern graphical user interface built with CustomTkinter, allowing users to select filters (currencies, impact levels, month, timezone, date range), choose export format (CSV/JSON), set custom filenames, and run the scraper interactively with detailed progress logs.

## How to Use
Follow these steps to use the Forex Factory News Event Scraper:
Ensure you have Python installed on your system.
Install the necessary Python libraries by running the following command:

`python3 -m pip install -r requirements.txt`

## Webdriver Installation:
The script uses the Chrome WebDriver to interact with the website. Make sure you have Google Chrome installed.
If you don't have the Chrome WebDriver installed, the script will attempt to install it using webdriver_manager. However, it's recommended to install it manually for better control.

## Running the Scraper:
Execute the scraper.py script to initiate the scraping process, using the command:

`python3 scraper.py`

It will launch a Chrome browser, navigate to the Forex Factory calendar page for the current month, and collect data. The scraped data will be reformatted and saved as a CSV file in the "news" directory with the filename in the format "MONTH_news.csv," where "MONTH" is the current month's name.

## Running the GUI Scraper:
For a user-friendly experience with customizable filters, you can either:

**Option 1: Direct Python execution**
```
python gui_scraper.py
```

**Option 2: Cross-platform Python Launcher (Recommended)**
Run `python start_gui.py` on any operating system. This script automatically installs requirements and launches the GUI.

**Option 3: Windows Batch File**
Double-click `start_gui.bat` in the project directory (Windows only).

This opens a modern dark-themed interface where you can select the month, currencies, impact levels, target timezone, date range for filtering, export format (CSV or JSON), and custom filename. The GUI runs the scraping in the background, shows detailed progress updates, and provides a log viewer for troubleshooting.

## GUI Features and Usage Guide

The Forex Factory Advanced Scraper features a modern, intuitive graphical interface with comprehensive filtering options and real-time progress tracking.

### Interface Overview

**Main Sections:**
- **Title Bar**: "Forex Factory Advanced Scraper" with professional styling
- **Filter Options**: Month, timezone, currency, and impact level selections
- **Export Settings**: Format choice, date range filtering, and filename customization
- **Control Panel**: Start button with progress bar and status updates
- **Log Viewer**: Real-time scraping logs with auto-scroll

### Filter Options

**Month Selection:**
- Choose between "this" (current month) or "next" (upcoming month)
- Scrapes the entire selected month's economic calendar

**Timezone Selection:**
- Dropdown with major financial timezones:
  - UTC (Coordinated Universal Time)
  - US/Eastern (New York, EST/EDT)
  - US/Central (Chicago, CST/CDT)
  - US/Pacific (Los Angeles, PST/PDT)
  - Europe/London (UK, GMT/BST)
  - Europe/Paris (France, CET/CEST)
  - Asia/Tokyo (Japan, JST)
  - Asia/Shanghai (China, CST)
  - Asia/Karachi (Pakistan, PKT)
  - Asia/Kolkata (India, IST)
  - Australia/Sydney (Australia, AEST/AEDT)
- Automatically converts event times to your selected timezone

**Currency Filtering:**
- Checkboxes for major currencies: CAD, EUR, GBP, USD
- Select multiple currencies or all (default)
- Only events affecting selected currencies will be included

**Impact Level Filtering:**
- Checkboxes for event impact levels: red (high), orange (medium), gray (low), yellow (holiday)
- Red, orange, and gray are selected by default
- Filter events by their expected market impact

### Export Settings

**Format Selection:**
- Choose between CSV (comma-separated values) or JSON (JavaScript Object Notation)
- CSV: Tabular format compatible with Excel and most spreadsheet applications
- JSON: Structured format ideal for programmatic processing

**Date Range Filtering:**
- Optional day-based filtering within the selected month
- "From day": Starting day (1-31)
- "To day": Ending day (1-31)
- Leave empty to include all days in the month
- Automatically filters events to the specified date range

**Filename Customization:**
- Optional custom filename (without extension)
- Default: "scraped_data" if left blank
- Files saved in `news/` directory with appropriate extension

### Using the Scraper

1. **Launch the GUI** using one of the methods above
2. **Select Month**: Choose current or next month
3. **Choose Timezone**: Select your preferred timezone for time conversion
4. **Filter Currencies**: Check desired currencies (all selected by default)
5. **Filter Impact Levels**: Check desired impact levels (high/medium/low selected by default)
6. **Set Export Options**:
   - Choose CSV or JSON format
   - Optionally set date range (from/to days)
   - Optionally enter custom filename
7. **Click "🚀 Start Scraping"**
8. **Monitor Progress**: Watch the animated progress bar and real-time logs
9. **View Results**: Files saved automatically in `news/` directory

### Progress Tracking

**Progress Bar:**
- Smoothly animated bar showing completion percentage
- Updates in real-time as scraping progresses
- Shows stages: initialization (0-10%), navigation (10-20%), scrolling (20-30%), extraction (30-50%), processing (50-70%), filtering (70-80%), saving (80-100%)

**Status Messages:**
- Dynamic labels showing current operation
- Percentage completion display
- Final success/error messages

**Log Viewer:**
- Real-time log messages appearing as operations complete
- Detailed step-by-step process information
- Auto-scrolling to show latest activity
- Error details for troubleshooting

### Output Files

**CSV Format:**
- Tabular data with headers
- Compatible with Excel, Google Sheets, and data analysis tools
- Includes all filtered event data with converted times

**JSON Format:**
- Structured object array
- Perfect for web applications and programmatic processing
- Maintains data relationships and types

**File Location:**
- All files saved in `news/` subdirectory
- Naming: `{custom_name}.{extension}` or `scraped_data.{extension}`
- Example: `news/forex_september.csv`

### Tips and Best Practices

- **First Run**: May take longer due to WebDriver setup
- **Timezone**: Choose timezone relevant to your trading location
- **Filtering**: Start with default settings, then customize as needed
- **Date Range**: Useful for focusing on specific trading periods
- **Logs**: Check logs if scraping fails for error details
- **Performance**: Scraping typically completes in 30-60 seconds depending on event volume

The GUI provides a complete, professional solution for Forex economic calendar data collection with extensive customization options and real-time feedback.


### Notes
This scraper is designed for educational and informational purposes. Ensure you comply with the terms of use and policies of Forex Factory when using this tool. Keep in mind that web scraping may be subject to legal and ethical considerations. 
Always respect the website's terms of service and robots.txt file.
It's a good practice to schedule the scraper to run periodically if you need updated data regularly.

**Disclaimer**: The accuracy and functionality of this scraper may change over time due to updates on the Forex Factory website. Be prepared to make adjustments if necessary.

**Please use this tool responsibly and in accordance with applicable laws and regulations.**
