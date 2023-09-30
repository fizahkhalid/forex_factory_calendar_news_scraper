import re
import json
import pandas as pd

def read_json(path):
    with open(path,'r') as f:
        data = json.load(f)
    return data

allowed_classes = ["calendar__cell calendar__date",
"calendar__cell calendar__time",
"calendar__cell calendar__currency",
"calendar__cell calendar__impact",
"calendar__cell calendar__event event"]
allowed_currencies = ['CAD','EUR','GBP','USD']
allowed_impact = ['red','orange','gray']
classes = {
"calendar__cell":"date",
"calendar__cell calendar__date":"date",
"calendar__cell calendar__time":"time",
"calendar__cell calendar__currency":"currency",
"calendar__cell calendar__impact":"impact",
"calendar__cell calendar__event event":"event"}
color_codes =  {
    "icon icon--ff-impact-yel":"yellow",
    "icon icon--ff-impact-ora":"orange",
    "icon icon--ff-impact-red":"red",
    "icon icon--ff-impact-gra":"gray"}
not_needed_classes = ["calendar__cell calendar__forecast","calendar__cell calendar__graph","calendar__cell calendar__previous"]


def contains_day_or_month(text):
    days_of_week = r'\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b'
    months = r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b'
    pattern = f'({days_of_week}|{months})'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        matched_text = match.group(0)
        if re.match(days_of_week, matched_text, re.IGNORECASE):
            return True, matched_text
    else:
        return False, None


def find_pattern_category(text):
    time_pattern = r'\d{1,2}:\d{2}(am|pm)'
    day_pattern = r'Day\s+\d+'
    date_range_pattern = r'\d{1,2}(st|nd|rd|th)\s*-\s*\d{1,2}(st|nd|rd|th)'
    tentative_pattern = r'\bTentative\b'
    pattern = f'({time_pattern}|{day_pattern}|{date_range_pattern}|{tentative_pattern})'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        matched_text = match.group(0)
        if re.match(time_pattern, matched_text, re.IGNORECASE):
            category = "time"
        elif re.match(day_pattern, matched_text, re.IGNORECASE):
            category = "day_reference"
        elif re.match(date_range_pattern, matched_text, re.IGNORECASE):
            category = "date_range"
        elif re.match(tentative_pattern, matched_text, re.IGNORECASE):
            category = "tentative"
        else:
            category = "Unknown"
        return True, category, matched_text
    else:
        return False, None, None
    
def reformat_scraped_data(data,month):
    current_date = ''
    current_time = ''
    structured_rows = []

    for index,row in enumerate(data):
        if len(row)==1 or len(row)==5:
            match, day = contains_day_or_month(row[0])
            if match:
                current_date = row[0].replace(day,"").replace("\n","")
        if len(row)==4:
            current_time = row[0]

        if len(row)==5:
            current_time = row[1]
        
        if len(row)>1:
            event = row[-1]
            impact = row[-2]
            currency = row[-3]
            structured_rows.append([current_date,current_time,currency,impact,event])
                

    df = pd.DataFrame(structured_rows,columns=['date','time','currency','impact','event'])
    df.to_csv(f"news/{month}_news.csv",index=False)

    return df


