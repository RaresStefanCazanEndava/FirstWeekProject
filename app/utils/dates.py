from datetime import datetime, date

MIN_YEAR = 1900
MAX_YEAR = 2100

class DateParseError(ValueError):
    pass

def parse_iso_date(value: str) -> date:
    """YYYY-MM-DD, cu an în [1900, 2100]. Ridică DateParseError dacă nu e valid."""
    try:
        d = datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        raise DateParseError("date must be in format YYYY-MM-DD")
    if d.year < MIN_YEAR or d.year > MAX_YEAR:
        raise DateParseError(f"date year must be between {MIN_YEAR} and {MAX_YEAR}")
    return d
