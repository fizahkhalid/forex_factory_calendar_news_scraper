from typing import Dict, List

# Constants for allowed classes and patterns

# Defines the mapping of Forex Factory calendar cell class names to their data type.
# Used by the scraper to identify and categorize the content of table cells.
ALLOWED_ELEMENT_TYPES: Dict[str, str] = {
    "calendar__cell": "date",  # General cell, often part of a date display
    "calendar__cell calendar__date": "date",  # Specific cell for date
    "calendar__cell calendar__time": "time",  # Cell containing event time
    "calendar__cell calendar__currency": "currency",  # Cell for currency code (e.g., USD)
    "calendar__cell calendar__impact": "impact",  # Cell indicating event impact (contains color icons)
    "calendar__cell calendar__event event": "event",  # Cell for the event description
    "calendar__cell calendar__actual": "actual",  # Cell for the actual outcome value
    "calendar__cell calendar__forecast": "forecast",  # Cell for the forecast value
    "calendar__cell calendar__previous": "previous",  # Cell for the previous value
}

# List of specific Forex Factory calendar cell class names to be explicitly ignored by the scraper.
EXCLUDED_ELEMENT_TYPES: List[str] = [
    "calendar__cell calendar__graph"  # Cells containing graph icons, not needed for data extraction
]

# Maps the class names of Forex Factory impact icons to human-readable color names.
# These colors typically represent the expected impact level of an event (e.g., high, medium, low).
ICON_COLOR_MAP: Dict[str, str] = {
    "icon icon--ff-impact-yel": "yellow",  # Typically low impact
    "icon icon--ff-impact-ora": "orange",  # Typically medium impact
    "icon icon--ff-impact-red": "red",  # Typically high impact
    "icon icon--ff-impact-gra": "gray"  # Typically non-economic or holiday
}

# Specifies a list of ISO currency codes (e.g., 'USD', 'EUR') that the user is interested in.
# The scraper might use this to filter events related only to these currencies.
ALLOWED_CURRENCY_CODES: List[str] = ['CAD', 'EUR', 'GBP', 'USD']

# Defines which news impact levels (represented by their mapped colors) the user wants to include.
# This allows filtering of events based on their significance (e.g., only high impact 'red' events).
ALLOWED_IMPACT_COLORS: List[str] = ['red', 'orange', 'gray']
