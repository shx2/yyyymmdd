"""
The ``Date`` class.
"""

import datetime as _dt
import pytz

from .misc import classproperty
from .tz import get_timezone


################################################################################
# Constants

_dtdate = _dt.date

_FORMATS = ['%Y%m%d', '%Y-%m-%d']

_DATE_ALIASES = {
    'MIN': _dtdate.min,
    'MAX': _dtdate.max,
}

_DELTA_MAP = {
    'yest': -1,
    'yesterday': -1,
    'today': 0,
    'tomorrow': +1,
}


################################################################################
# The Date class

class Date(_dtdate):
    """
    A date, in yyyymmdd format.

    This is a subclass of ``datetime.date``, and is mostly (but not fully) compatible with it.

    This class supports flexible creation of ``Date`` objects, e.g.: from a yyyymmdd string, from
    delta (number of days relative to today), aliases ('yesterday', 'today', 'MIN', 'MAX', etc.),
    from a ``datetime.date`` object, etc.

    Convenient date arithmetic: ``Date +/- int => Date``, ``Date - Date => int``.

    """

    FORMAT = _FORMATS[0]

    # ===============================================================================================
    # ctor
    # ===============================================================================================

    def __new__(cls, *args, **kwargs):
        if len(args) == 1 and not kwargs:
            x = args[0]
            d = _to_dt_date(x)
            if d is not None:
                return cls.fromordinal(d.toordinal())
            else:
                raise ValueError('invalid date: %r' % x)
        return super().__new__(cls, *args, **kwargs)

    # ===============================================================================================
    #  adjusted datetime.date interface
    # ===============================================================================================

    def replace(self, *args, **kwargs):
        return type(self)(super().replace(*args, **kwargs))

    @classproperty
    def min(cls):
        """ The earliest date supported. """
        return cls(super().min)

    @classproperty
    def max(cls):
        """ The latest date supported. """
        return cls(super().max)

    @classmethod
    def today(cls):
        """ Today's date, in current timezone. """
        return cls(_today())

    @classmethod
    def utctoday(cls):
        """ Today's date, in UTC. """
        return cls(_utctoday())

    def __str__(self):
        return self.strftime(self.FORMAT)

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, self)

    # ===============================================================================================
    # date arithmetic
    # ===============================================================================================

    def __add__(self, days):
        """
        >>> Date(20120130) + 2
        Date(20120201)
        """
        return self.fromordinal(self.toordinal() + days)

    def __sub__(self, x):
        """
        >>> Date(20120130) - 2
        Date(20120128)
        >>> Date(20120130) - Date(20120128)
        2
        """
        if isinstance(x, int):
            # subtract days
            return self + (-x)
        elif isinstance(x, Date):
            # difference between dates, in days
            return (self.as_datetime_date() - x.as_datetime_date()).days
        else:
            raise TypeError(x)

    # ===============================================================================================
    # misc
    # ===============================================================================================

    def year_start(self):
        """
        >>> Date(20120830).year_start()
        Date(20120101)
        """
        return self.replace(month=1, day=1)

    def year_end(self):
        """
        >>> Date(20120830).year_end()
        Date(20121231)
        """
        return self.replace(year=self.year + 1).year_start() - 1

    def month_start(self):
        """
        >>> Date(20120830).month_start()
        Date(20120801)
        """
        return self.replace(day=1)

    def month_end(self):
        """
        >>> Date(20120115).month_end()
        Date(20120131)
        """
        d = self.replace(day=28)
        while d.month == (d + 1).month:
            d += 1
        return d

    def min_timestamp(self, **kwargs):
        """
        First timestamp of the day.
        """
        return _dt.datetime.fromordinal(self.toordinal()).replace(**kwargs)

    def max_timestamp(self, **kwargs):
        """
        Last timestamp of the day.
        """
        return (self + 1).min_timestamp(**kwargs) - _dt.datetime.resolution

    @property
    def yyyy(self):
        """
        A string represeneting the year part.

        >>> Date(19950607).yyyy
        '1995'
        """
        return self.strftime('%Y')

    @property
    def mm(self):
        """
        2-char string represeneting the month part.

        >>> Date(19950607).mm
        '06'
        """
        return self.strftime('%m')

    @property
    def dd(self):
        """
        2-char string represeneting the day part.

        >>> Date(19950607).dd
        '07'
        """
        return self.strftime('%d')

    def as_datetime_date(self):
        """ Convert self to a ``datetime.date`` object. """
        return _dtdate.fromordinal(self.toordinal())


################################################################################
# Private functions

def _today():
    tz = get_timezone()
    if tz is None:
        # local
        return _dtdate.today()
    else:
        # convert utc to TIMEZONE
        t_utc = pytz.utc.localize(_dt.datetime.utcnow())
        t_local = t_utc.astimezone(tz)
        return t_local.date()


def _utctoday():
    return _dt.datetime.utcnow().date()


def _to_dt_date(x):
    if isinstance(x, (_dtdate, Date)):
        return x
    elif isinstance(x, str):
        return _from_string(x)
    elif isinstance(x, int):
        return _from_int(x)
    else:
        return None


def _from_string(x):
    if not x:
        raise ValueError(x)
    # relative
    delta = _delta_from_string(x)
    if delta is not None:
        return _from_delta(delta)
    # date aliases
    try:
        return _DATE_ALIASES[x]
    except KeyError:
        pass

    # absolute date
    # we zero-pad the year, otherwise dates before year 1000 can parse incorrectly
    x2 = _pad_date_string(x)
    for fmt in _FORMATS:
        try:
            return _dt.datetime.strptime(x2, fmt).date()
        except ValueError:
            continue
    return None


def _delta_from_string(x):
    try:
        return _DELTA_MAP[x.lower()]
    except KeyError:
        pass
    if (x and x[0] in '+-') or x in ['0']:
        try:
            return int(x)
        except (TypeError, ValueError):
            pass
    return None


def _from_int(x):
    if x < 1:
        # negative delta, relative to today, e.g. -1, -500
        return _from_delta(x)
    else:
        # a date as int, e.g. 20120305
        return _dtdate(x // 10000, (x // 100) % 100, x % 100)


def _from_delta(x):
    return _today() + _dt.timedelta(days=x)


def _pad_date_string(x):
    if '-' in x:
        # A yyyy-mm-dd string
        unpadded, _, _ = x.partition('-')
        n = 4
    else:
        # A yyyymmdd string
        unpadded = x
        n = 8
    padlen = max(0, n - len(unpadded))
    return (padlen * '0') + x


################################################################################
