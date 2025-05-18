# Constants for allowed classes and patterns

ALLOWED_ELEMENT_TYPES = {
    "calendar__cell": "date",
    "calendar__cell calendar__date": "date",
    "calendar__cell calendar__time": "time",
    "calendar__cell calendar__currency": "currency",
    "calendar__cell calendar__impact": "impact",
    "calendar__cell calendar__event event": "event",
    "calendar__cell calendar__actual": "actual",
    "calendar__cell calendar__forecast": "forecast",
    "calendar__cell calendar__previous": "previous",
}

EXCLUDED_ELEMENT_TYPES = [
    "calendar__cell calendar__graph"
]

ICON_COLOR_MAP = {
    "icon icon--ff-impact-yel": "yellow",
    "icon icon--ff-impact-ora": "orange",
    "icon icon--ff-impact-red": "red",
    "icon icon--ff-impact-gra": "gray"
}

# THE CURRENCY CODES I WANT TO SCRAPE
ALLOWED_CURRENCY_CODES = ['CAD', 'EUR', 'GBP', 'USD']

# THE NEWS EVENTS WITH IMPACTS, THAT I WANT TO SCRAPE
ALLOWED_IMPACT_COLORS = ['red', 'orange', 'gray']
