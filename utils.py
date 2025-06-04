import os
import re
import json
import pandas as pd


from typing import Any, Tuple, Optional


def read_json(path: str) -> dict[str, Any]:
    """
    Read JSON data from a file.
    Args: path (str): The path to the JSON file.
    Returns: dict: The loaded JSON data.
    """
    with open(path, 'r') as f:
        data: dict[str, Any] = json.load(f)
    return data


def contains_day_or_month(text: str) -> tuple[bool, Optional[str]]:
    """
    Check if the given text contains a day of the week or a month.

    Args:
        text (str): The input text to check.

    Returns:
        tuple: A tuple containing a boolean indicating whether a match was found,
        and the matched text (day or month) if found.
    """

    # Regular expressions for days of the week and months
    # It's generally good practice to pre-compile regex if used frequently,
    # but for this script's current usage, direct use is acceptable.
    days_of_week_pattern = r'\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b'
    months_pattern = r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b'
    combined_pattern = f'({days_of_week_pattern}|{months_pattern})'

    match = re.search(combined_pattern, text, re.IGNORECASE)

    if not match:
        return False, None

    matched_text = match.group(0)
    # Check if the matched text is a day of the week
    if re.match(days_of_week_pattern, matched_text, re.IGNORECASE):
        return True, matched_text
    # If it's a month, the original logic didn't explicitly return it,
    # but the pattern allows it. Assuming we only care if it's a day for now.
    # To return month as well, an else if for months_pattern would be needed.
    # For now, aligning with original apparent intent:
    if re.match(months_pattern, matched_text, re.IGNORECASE): # If it's a month
        return True, matched_text # Modified: return month as well

    return False, None # Should not be reached if combined_pattern matches


def find_pattern_category(text: str) -> tuple[bool, Optional[str], Optional[str]]:
    """
    Find the category of a specific pattern within the given text.

    Args:
        text (str): The input text to analyze.

    Returns:
        tuple: A tuple containing a boolean indicating whether a match was found,
        the category of the matched pattern, and the matched text.
    """

    # Regular expressions for different patterns
    # Similar to contains_day_or_month, pre-compilation could be an optimization.
    time_regex = r'\d{1,2}:\d{2}(am|pm)'
    day_regex = r'Day\s+\d+'
    date_range_regex = r'\d{1,2}(st|nd|rd|th)\s*-\s*\d{1,2}(st|nd|rd|th)'
    tentative_regex = r'\bTentative\b'
    combined_regex = f'({time_regex}|{day_regex}|{date_range_regex}|{tentative_regex})'

    match = re.search(combined_regex, text, re.IGNORECASE)

    if not match:
        return False, None, None

    matched_text = match.group(0)
    category: Optional[str] = None

    if re.fullmatch(time_regex, matched_text, re.IGNORECASE):
        category = "time"
    elif re.fullmatch(day_regex, matched_text, re.IGNORECASE):
        category = "day_reference"
    elif re.fullmatch(date_range_regex, matched_text, re.IGNORECASE):
        category = "date_range"
    elif re.fullmatch(tentative_regex, matched_text, re.IGNORECASE):
        category = "tentative"
    else:
        category = "Unknown"  # Should ideally not be reached if combined_regex matched
    return True, category, matched_text


def reformat_scraped_data(data: list[list[str]], file_prefix: str) -> pd.DataFrame:
    """
    Reformat scraped data, extracting date, time, and event details,
    and save it as a DataFrame and a CSV file.

    Args:
        data (list[list[str]]): The scraped data, where each inner list
                                represents a row from the source table.
        file_prefix (str): The prefix for naming the output CSV file (e.g., "may2025").

    Returns:
        pd.DataFrame: The reformatted data as a Pandas DataFrame.
    """
    current_date_str = ''
    current_time_str = ''
    structured_rows: list[list[Optional[str]]] = []

    for row in data:
        if not row:  # Skip empty rows
            continue

        # Attempt to extract date from the first element of the row
        # Assumes date information is primarily in the first column if it contains a day/month.
        is_date_info, matched_day_or_month = contains_day_or_month(row[0])
        if is_date_info and matched_day_or_month:
            # Clean up the date string by removing the matched day/month and newlines
            current_date_str = row[0].replace(matched_day_or_month, "").replace("\n", "").strip()

        # Attempt to extract time
        # Time can appear in different positions based on row structure.
        # Case 1: Row length 7, first element is a time.
        if len(row) == 7:
            is_time, time_cat, matched_time = find_pattern_category(row[0])
            if is_time and time_cat == "time":
                current_time_str = matched_time
        # Case 2: Row length 8, second element is a time.
        elif len(row) == 8:
            is_time, time_cat, matched_time = find_pattern_category(row[1])
            if is_time and time_cat == "time":
                current_time_str = matched_time
            # Also, if the first element was a date, the second might be time (covered above)
            # or the first element itself in a length 8 row might be a time if no day/month was found
            elif not is_date_info: # If row[0] wasn't a date, check if it's a time
                is_time_alt, time_cat_alt, matched_time_alt = find_pattern_category(row[0])
                if is_time_alt and time_cat_alt == "time":
                    current_time_str = matched_time_alt


        # Process rows that are expected to contain event data.
        # Assumption: Event data rows have more than 5 columns,
        # and the last 6 columns are currency, impact, event, actual, forecast, previous.
        if len(row) > 5:
            # Slicing the last 6 elements for the main event data
            currency, impact, event, actual, forecast, previous = row[-6:]

            structured_rows.append([
                current_date_str,
                current_time_str,
                currency,
                impact,
                event,
                actual,
                forecast,
                previous
            ])

    df = pd.DataFrame(
        structured_rows,
        columns=['date', 'time', 'currency', 'impact', 'event', 'actual', 'forecast', 'previous']
    )

    # Ensure the directory for saving news exists
    output_dir = "news"
    os.makedirs(output_dir, exist_ok=True)

    # Save the DataFrame to a CSV file
    csv_file_path = os.path.join(output_dir, f"{file_prefix}_news.csv")
    df.to_csv(csv_file_path, index=False)
    # print(f"Data saved to {csv_file_path}") # Or use logging if available

    return df
