"""
Timezone stuff.
"""

import datetime
import pytz


TIMEZONE = None
"""
Timezone used for resolving what "today" means.  Defaults to local tz.
"""


def get_timezone():
    return TIMEZONE


def set_timezone(tz):
    """
    Set a timezone to use for resolving what "today" means.
    Set to None to reset to default.
    """
    global TIMEZONE
    if tz is not None and not isinstance(tz, datetime.tzinfo):
        tz = pytz.timezone(tz)
    prev_tz = TIMEZONE
    TIMEZONE = tz
    return prev_tz


def set_timezone_utc():
    """
    Same as ``set_timezone('UTC')``.
    """
    return set_timezone('UTC')
