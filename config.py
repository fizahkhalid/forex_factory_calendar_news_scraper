# Mapping of Forex Factory element class names to semantic labels for parsing.
ALLOWED_ELEMENT_TYPES = {
    "calendar__cell": "date",  # Generic cell (used for date continuation rows)
    "calendar__cell calendar__date": "date",  # Date of the news event
    "calendar__cell calendar__time": "time",  # Time of the news event
    "calendar__cell calendar__currency": "currency",  # Affected currency
    "calendar__cell calendar__impact": "impact",  # Expected impact level (color-coded)
    "calendar__cell calendar__detail": "detail",  # Expected impact level (color-coded)
    "calendar__cell calendar__event event": "event",  # News event title
    "calendar__cell calendar__actual": "actual",  # Actual reported value
    "calendar__cell calendar__forecast": "forecast",  # Forecasted value
    "calendar__cell calendar__previous": "previous",  # Previously reported value
}

# Element types to ignore during parsing
EXCLUDED_ELEMENT_TYPES = [
    "calendar__cell calendar__graph",  # Graph cell that is not relevant for scraping
]

# Mapping of CSS icon classes to impact colors
ICON_COLOR_MAP = {
    "icon icon--ff-impact-yel": "yellow",
    "icon icon--ff-impact-ora": "orange",
    "icon icon--ff-impact-red": "red",
    "icon icon--ff-impact-gra": "gray"
}

# Allowed currency codes for filtering news events
ALLOWED_CURRENCY_CODES = ['CAD', 'EUR', 'GBP', 'USD']

# Allowed impact levels for filtering news events
ALLOWED_IMPACT_COLORS = ['red', 'orange', 'gray']

# Timezone configuration
SCRAPER_TIMEZONE = None         # This will be detected from Selenium

# Set this to the target timezone you'd like your output to be in.
# If left as None, no conversion will happen.
# Examples:
#   "UTC"                 → Coordinated Universal Time
#   "US/Eastern"          → Eastern Time (e.g., New York, Boston)
#   "US/Central"          → Central Time (e.g., Chicago)
#   "US/Pacific"          → Pacific Time (e.g., Los Angeles)
#   "Europe/London"       → UK Time (adjusts for DST)
#   "Asia/Karachi"        → Pakistan Standard Time
#   "Asia/Kolkata"        → India Standard Time

TARGET_TIMEZONE = "Asia/Karachi"