from datetime import datetime

def parse_timestamp(timestamp_str: str, fmt="%d.%m.%Y %H:%M:%S") -> datetime:
    """Convert string timestamp to datetime object."""
    return datetime.strptime(timestamp_str, fmt)

def duration_minutes(start: datetime, end: datetime) -> float:
    """Return duration in minutes between two datetime objects."""
    delta = end - start
    return round(delta.total_seconds() / 60, 2)

def duration_seconds(start: datetime, end: datetime) -> float:
    """Return duration in seconds between two datetime objects."""
    delta = end - start
    return round(delta.total_seconds(), 2)
