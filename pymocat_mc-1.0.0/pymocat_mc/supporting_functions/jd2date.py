"""
Julian date to datetime conversion.

Python equivalent of jd2date.m.
"""

from datetime import datetime, timedelta
import numpy as np


def jd2date(jd: float) -> datetime:
    """
    Convert Julian date to datetime.

    Args:
        jd: Julian date

    Returns:
        DateTime object
    """
    # Julian date of January 1, 2000, 12:00:00 UTC
    jd_2000 = 2451545.0

    # Calculate days since J2000
    days_since_j2000 = jd - jd_2000

    # Reference date: January 1, 2000, 12:00:00 UTC
    ref_date = datetime(2000, 1, 1, 12, 0, 0)

    # Add the days
    result_date = ref_date + timedelta(days=days_since_j2000)

    return result_date


def date2jd(dt: datetime) -> float:
    """
    Convert datetime to Julian date

    Args:
        dt: DateTime object

    Returns:
        Julian date
    """
    a = (14 - dt.month) // 12
    y = dt.year + 4800 - a
    m = dt.month + 12 * a - 3

    jd = (dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 +
          y // 400 - 32045 + (dt.hour - 12) / 24 + dt.minute / 1440 +
          dt.second / 86400 + dt.microsecond / 86400000000)

    return jd
