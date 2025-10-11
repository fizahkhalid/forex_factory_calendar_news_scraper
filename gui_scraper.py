import customtkinter as ctk
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import pandas as pd
import os
import pytz
import re
from urllib.request import urlopen
import json
import queue

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Forex Factory Advanced Scraper")
        self.geometry("800x650")
        self.resizable(True, True)

        # Title
        self.title_label = ctk.CTkLabel(self, text="Forex Factory Advanced Scraper", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        # Main container
        self.main_frame = ctk.CTkScrollableFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Filter Section
        self.filter_frame = ctk.CTkFrame(self.main_frame)
        self.filter_frame.pack(fill="x", pady=10)
        self.filter_label = ctk.CTkLabel(self.filter_frame, text="Filter Options", font=ctk.CTkFont(size=16, weight="bold"))
        self.filter_label.pack(pady=10)

        # Month and Timezone row
        self.month_tz_frame = ctk.CTkFrame(self.filter_frame, fg_color="transparent")
        self.month_tz_frame.pack(anchor="center", padx=20, pady=5)
        self.month_label = ctk.CTkLabel(self.month_tz_frame, text="Month:")
        self.month_label.pack(side="left", padx=10, pady=5)
        self.month_var = ctk.StringVar(value="this")
        self.month_menu = ctk.CTkOptionMenu(self.month_tz_frame, variable=self.month_var, values=["this", "next"], width=100)
        self.month_menu.pack(side="left", padx=10, pady=5)
        self.tz_label = ctk.CTkLabel(self.month_tz_frame, text="Timezone:")
        self.tz_label.pack(side="left", padx=10, pady=5)
        self.tz_var = ctk.StringVar(value="UTC")
        self.tz_menu = ctk.CTkOptionMenu(self.month_tz_frame, variable=self.tz_var,
                                         values=["UTC", "US/Eastern", "US/Central", "US/Pacific",
                                                 "Europe/London", "Europe/Paris", "Asia/Tokyo",
                                                 "Asia/Shanghai", "Asia/Karachi", "Asia/Kolkata",
                                                 "Australia/Sydney"], width=150)
        self.tz_menu.pack(side="left", padx=10, pady=5)

        # Currencies
        self.currency_label = ctk.CTkLabel(self.filter_frame, text="Currencies:")
        self.currency_label.pack(anchor="center", pady=5)
        self.currency_frame = ctk.CTkFrame(self.filter_frame, fg_color="transparent")
        self.currency_frame.pack(anchor="center", pady=5)
        self.currency_vars = {}
        currencies = ["CAD", "EUR", "GBP", "USD"]
        for curr in currencies:
            var = ctk.BooleanVar(value=True)
            chk = ctk.CTkCheckBox(self.currency_frame, text=curr, variable=var)
            chk.pack(side="left", padx=10, pady=5)
            self.currency_vars[curr] = var

        # Impacts
        self.impact_label = ctk.CTkLabel(self.filter_frame, text="Impact Levels:")
        self.impact_label.pack(anchor="center", pady=5)
        self.impact_frame = ctk.CTkFrame(self.filter_frame, fg_color="transparent")
        self.impact_frame.pack(anchor="center", pady=5)
        self.impact_vars = {}
        impacts = ["red", "orange", "gray", "yellow"]
        for imp in impacts:
            var = ctk.BooleanVar(value=True if imp in ["red", "orange", "gray"] else False)
            chk = ctk.CTkCheckBox(self.impact_frame, text=imp, variable=var)
            chk.pack(side="left", padx=10, pady=5)
            self.impact_vars[imp] = var

        # Export Section
        self.export_frame = ctk.CTkFrame(self.main_frame)
        self.export_frame.pack(fill="x", pady=10)
        self.export_label = ctk.CTkLabel(self.export_frame, text="Export Settings", font=ctk.CTkFont(size=16, weight="bold"))
        self.export_label.pack(pady=10)

        # Format and Filename row
        self.format_file_frame = ctk.CTkFrame(self.export_frame, fg_color="transparent")
        self.format_file_frame.pack(anchor="center", padx=20, pady=5)
        self.format_label = ctk.CTkLabel(self.format_file_frame, text="Format:")
        self.format_label.pack(side="left", padx=10, pady=5)
        self.format_var = ctk.StringVar(value="CSV")
        self.format_menu = ctk.CTkOptionMenu(self.format_file_frame, variable=self.format_var, values=["CSV", "JSON"], width=100)
        self.format_menu.pack(side="left", padx=10, pady=5)
        self.filename_label = ctk.CTkLabel(self.format_file_frame, text="Filename (optional):")
        self.filename_label.pack(side="left", padx=10, pady=5)
        self.filename_entry = ctk.CTkEntry(self.format_file_frame, placeholder_text="scraped_data", width=150)
        self.filename_entry.pack(side="left", padx=10, pady=5)

        # Date range (days only, selected month)
        self.date_label = ctk.CTkLabel(self.export_frame, text="Date Range (days in selected month, optional):")
        self.date_label.pack(anchor="center", pady=5)
        self.date_frame = ctk.CTkFrame(self.export_frame, fg_color="transparent")
        self.date_frame.pack(anchor="center", pady=5)

        # From day
        self.date_from_label = ctk.CTkLabel(self.date_frame, text="From day:")
        self.date_from_label.pack(side="left", padx=10, pady=5)
        self.from_day_var = ctk.StringVar()
        self.from_day_menu = ctk.CTkOptionMenu(self.date_frame, variable=self.from_day_var,
                                               values=[""] + [str(i) for i in range(1, 32)], width=80)
        self.from_day_menu.pack(side="left", padx=10, pady=5)

        # To day
        self.date_to_label = ctk.CTkLabel(self.date_frame, text="To day:")
        self.date_to_label.pack(side="left", padx=10, pady=5)
        self.to_day_var = ctk.StringVar()
        self.to_day_menu = ctk.CTkOptionMenu(self.date_frame, variable=self.to_day_var,
                                             values=[""] + [str(i) for i in range(1, 32)], width=80)
        self.to_day_menu.pack(side="left", padx=10, pady=5)

        # Control Section
        self.control_frame = ctk.CTkFrame(self.main_frame)
        self.control_frame.pack(fill="x", pady=10)
        self.start_btn = ctk.CTkButton(self.control_frame, text="🚀 Start Scraping", command=self.start_scrape, font=ctk.CTkFont(size=14, weight="bold"))
        self.start_btn.pack(pady=10)
        self.progress_bar = ctk.CTkProgressBar(self.control_frame, width=400)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)
        self.progress_label = ctk.CTkLabel(self.control_frame, text="", font=ctk.CTkFont(size=12))
        self.progress_label.pack(pady=5)

        # Logs Section
        self.logs_frame = ctk.CTkFrame(self.main_frame)
        self.logs_frame.pack(fill="both", expand=True, pady=10)
        self.log_label = ctk.CTkLabel(self.logs_frame, text="📋 Scraping Logs", font=ctk.CTkFont(size=14, weight="bold"))
        self.log_label.pack(pady=5)
        self.log_text = ctk.CTkTextbox(self.logs_frame, wrap="word", font=ctk.CTkFont(size=10), height=100)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.logs = []

        # Progress bar
        self.progress_queue = queue.Queue()
        self.log_queue = queue.Queue()
        self.scraping = False

    def check_progress(self):
        try:
            while True:
                target = self.progress_queue.get_nowait()
                self.animate_progress(target)
        except queue.Empty:
            pass
        try:
            while True:
                log_msg = self.log_queue.get_nowait()
                self.log_text.insert("end", log_msg + "\n")
                self.log_text.see("end")
        except queue.Empty:
            pass
        if self.scraping:
            self.after(100, self.check_progress)

    def animate_progress(self, target):
        current = self.progress_bar.get() * 100
        if current < target:
            current += 1
            self.progress_bar.set(current / 100)
            self.progress_label.configure(text=f"Progress: {int(current)}%")
            self.after(20, lambda: self.animate_progress(target))
        else:
            self.progress_label.configure(text=f"Progress: {int(target)}%")


    def start_scrape(self):
        month = self.month_var.get()
        selected_currencies = [c for c, v in self.currency_vars.items() if v.get()]
        selected_impacts = [i for i, v in self.impact_vars.items() if v.get()]
        target_tz = self.tz_var.get()
        format_type = self.format_var.get()
        # Determine target month/year
        now = datetime.now()
        if month == "this":
            target_month = now.month
            target_year = now.year
        elif month == "next":
            target_month = (now.month % 12) + 1
            target_year = now.year if now.month < 12 else now.year + 1
        # Build date strings
        date_from = ""
        if self.from_day_var.get():
            date_from = f"{int(self.from_day_var.get()):02d}/{target_month:02d}/{target_year}"
        date_to = ""
        if self.to_day_var.get():
            date_to = f"{int(self.to_day_var.get()):02d}/{target_month:02d}/{target_year}"
        custom_filename = self.filename_entry.get().strip()

        if not selected_currencies or not selected_impacts:
            self.progress_label.configure(text="Please select at least one currency and impact level.")
            return

        self.scraping = True
        self.progress_bar.set(0)
        self.progress_label.configure(text="Initializing scraper...")
        self.start_btn.configure(state="disabled")
        self.log_text.delete("1.0", "end")
        self.check_progress()

        threading.Thread(target=self.scrape, args=(month, selected_currencies, selected_impacts, target_tz, format_type, date_from, date_to, custom_filename)).start()

    def scrape(self, month, currencies, impacts, tz, format_type, date_from, date_to, custom_filename):
        try:
            result = self.perform_scrape(month, currencies, impacts, tz, format_type, date_from, date_to, custom_filename)
            self.progress_queue.put(100)
            self.progress_label.configure(text=f"Scraping completed. Data saved to {result}")
        except Exception as e:
            self.progress_label.configure(text=f"Error: {str(e)}")
            self.log_queue.put(f"Error: {str(e)}")
        finally:
            self.scraping = False
            self.start_btn.configure(state="normal")

    def perform_scrape(self, month_param, allowed_currencies, allowed_impacts, target_timezone, format_type, date_from, date_to, custom_filename):
        ALLOWED_ELEMENT_TYPES = {
            "calendar__cell": "date",
            "calendar__cell calendar__date": "date",
            "calendar__cell calendar__time": "time",
            "calendar__cell calendar__currency": "currency",
            "calendar__cell calendar__impact": "impact",
            "calendar__cell calendar__detail": "detail",
            "calendar__cell calendar__event event": "event",
            "calendar__cell calendar__actual": "actual",
            "calendar__cell calendar__forecast": "forecast",
            "calendar__cell calendar__previous": "previous",
        }

        ICON_COLOR_MAP = {
            "icon icon--ff-impact-yel": "yellow",
            "icon icon--ff-impact-ora": "orange",
            "icon icon--ff-impact-red": "red",
            "icon icon--ff-impact-gra": "gray"
        }

        self.log_queue.put("Initializing WebDriver...")
        self.progress_queue.put(5)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("window-size=1920x1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        self.log_queue.put("WebDriver initialized successfully.")
        self.progress_queue.put(10)

        url = f"https://www.forexfactory.com/calendar?month={month_param}"
        self.log_queue.put(f"Navigating to {url}")
        driver.get(url)
        self.progress_queue.put(20)

        self.log_queue.put("Loading all events by scrolling...")
        previous_position = None
        while True:
            current_position = driver.execute_script("return window.pageYOffset;")
            driver.execute_script("window.scrollTo(0, window.pageYOffset + 500);")
            time.sleep(2)
            if current_position == previous_position:
                break
            previous_position = current_position
        self.log_queue.put("Page fully loaded.")
        self.progress_queue.put(30)

        self.log_queue.put("Extracting data from calendar table...")
        data = []
        table = driver.find_element(By.CLASS_NAME, "calendar__table")
        for row in table.find_elements(By.TAG_NAME, "tr"):
            row_data = {}
            event_id = row.get_attribute("data-event-id")
            for element in row.find_elements(By.TAG_NAME, "td"):
                class_name = element.get_attribute('class')
                if class_name in ALLOWED_ELEMENT_TYPES:
                    class_name_key = ALLOWED_ELEMENT_TYPES.get(f"{class_name}", "cell")
                    if "calendar__impact" in class_name:
                        impact_elements = element.find_elements(By.TAG_NAME, "span")
                        color = None
                        for impact in impact_elements:
                            impact_class = impact.get_attribute("class")
                            color = ICON_COLOR_MAP.get(impact_class)
                        row_data[f"{class_name_key}"] = color if color else "impact"
                    elif "calendar__detail" in class_name and event_id:
                        detail_url = f"https://www.forexfactory.com/calendar?month={month_param}#detail={event_id}"
                        row_data[f"{class_name_key}"] = detail_url
                    elif element.text:
                        row_data[f"{class_name_key}"] = element.text
                    else:
                        row_data[f"{class_name_key}"] = "empty"
            if row_data:
                data.append(row_data)
        self.log_queue.put(f"Extracted {len(data)} raw events.")
        self.progress_queue.put(50)

        driver.quit()
        self.log_queue.put("WebDriver closed.")

        now = datetime.now()
        if month_param == "this":
            month = now.strftime("%B")
            year = str(now.year)
        elif month_param == "next":
            next_month = (now.month % 12) + 1
            year = str(now.year if now.month < 12 else now.year + 1)
            month = datetime(year=int(year), month=next_month, day=1).strftime("%B")
        else:
            month = month_param.capitalize()
            year = str(now.year)

        self.log_queue.put("Processing and structuring data...")
        current_date = ''
        current_time = ''
        current_day = ''
        structured_rows = []
        scraper_timezone = self.find_location_timezone()

        for row in data:
            new_row = row.copy()
            if "date" in new_row and new_row['date'] != "empty":
                date_parts = self.extract_date_parts(new_row["date"], year)
                if date_parts:
                    current_date = date_parts["date"]
                    current_day = date_parts["day"]
            if "time" in new_row:
                if new_row["time"] != "empty":
                    current_time = new_row["time"].strip()
                else:
                    new_row["time"] = current_time
            if len(row) == 1:
                continue
            new_row["day"] = current_day
            new_row["date"] = current_date
            if scraper_timezone and target_timezone:
                new_row["time"] = self.convert_time_zone(current_date, current_time, scraper_timezone, target_timezone)
            else:
                new_row["time"] = current_time
            new_row["currency"] = row.get("currency", "")
            new_row["impact"] = row.get("impact", "")
            new_row["event"] = row.get("event", "")
            new_row["detail"] = row.get("detail", "")
            new_row["actual"] = row.get("actual", "")
            new_row["forecast"] = row.get("forecast", "")
            new_row["previous"] = row.get("previous", "")
            for key, value in new_row.items():
                if value == "empty":
                    new_row[key] = ""
            if new_row['currency'] not in allowed_currencies or new_row['impact'].lower() not in [i.lower() for i in allowed_impacts]:
                continue
            structured_rows.append(new_row)
        self.log_queue.put(f"Structured {len(structured_rows)} events after filtering.")
        self.progress_queue.put(70)

        # Date range filtering
        if date_from or date_to:
            self.log_queue.put("Applying date range filter...")
            filtered_rows = []
            for row in structured_rows:
                row_date_str = row.get("date", "")
                if row_date_str:
                    try:
                        row_date = datetime.strptime(row_date_str, "%d/%m/%Y")
                        include = True
                        if date_from:
                            from_date = datetime.strptime(date_from, "%d/%m/%Y")
                            if row_date < from_date:
                                include = False
                        if date_to:
                            to_date = datetime.strptime(date_to, "%d/%m/%Y")
                            if row_date > to_date:
                                include = False
                        if include:
                            filtered_rows.append(row)
                    except ValueError:
                        filtered_rows.append(row)  # Include if parsing fails
                else:
                    filtered_rows.append(row)
            structured_rows = filtered_rows
            self.log_queue.put(f"Date filtered to {len(structured_rows)} events.")
        self.progress_queue.put(80)

        # Save data
        self.progress_queue.put(90)
        if custom_filename.strip():
            base_name = custom_filename.strip()
        else:
            base_name = "scraped_data"

        os.makedirs("news", exist_ok=True)
        if format_type == "JSON":
            filename = f"news/{base_name}.json"
            with open(filename, 'w') as f:
                json.dump(structured_rows, f, indent=4)
            self.log_queue.put(f"Data saved as JSON to {filename}")
        else:
            filename = f"news/{base_name}.csv"
            header = list(structured_rows[0].keys()) if structured_rows else []
            df = pd.DataFrame(structured_rows, columns=header)
            df.to_csv(filename, index=False)
            self.log_queue.put(f"Data saved as CSV to {filename}")

        return filename

    def extract_date_parts(self, text, year):
        pattern = r'\b(?P<day>Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b\s+' \
                  r'(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b\s+' \
                  r'(?P<date>\d{1,2})\b'
        match = re.search(pattern, text)
        if match:
            month_abbr = match.group("month")
            day = int(match.group("date"))
            month_number = datetime.strptime(month_abbr, "%b").month
            formatted_date = f"{day:02d}/{month_number:02d}/{year}"
            return {
                "day": match.group("day"),
                "date": formatted_date
            }
        return None

    def convert_time_zone(self, date_str, time_str, from_zone_str, to_zone_str):
        if not time_str or not date_str:
            return time_str
        if time_str.lower() in ["all day", "tentative"]:
            return time_str
        try:
            from_zone = pytz.timezone(from_zone_str)
            to_zone = pytz.timezone(to_zone_str)
            naive_dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %I:%M%p")
            localized_dt = from_zone.localize(naive_dt)
            converted_dt = localized_dt.astimezone(to_zone)
            return converted_dt.strftime("%H:%M")
        except Exception as e:
            return time_str

    def find_location_timezone(self):
        try:
            url = 'http://ipinfo.io/json'
            response = urlopen(url)
            data = json.load(response)
            return data['timezone']
        except:
            return None

if __name__ == "__main__":
    app = App()
    app.mainloop()