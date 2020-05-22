"""
The ``DateRange`` class.
"""

from .date import Date
from .misc import classproperty, egcd as _egcd


################################################################################
# The DateRange class

class DateRange(object):
    """
    A `range <https://docs.python.org/3.8/library/functions.html#func-range>`_ -like type, whose
    elements are ``Date``s.

    This class mostly follows the semantics of the builtin ``range`` type.  E.g.,
    stop is exclusive, behavior of steps, negative steps, slicing,
    ``range1 == range2`` iff ``tuple(range1) == tuple(range2)``, etc.

    Creation of ``DateRange`` objects is flexible.  ``start`` and ``stop`` parameters are converted
    to ``Date`` automatically.  See ``Date`` class for values which can be converted.
    """

    DATE_TYPE = Date
    DELIM = ':'
    OTHER_SIDE_MARKER = '%'
    EMPTY_RANGE_STRING = 'NONE'
    FULL_RANGE_STRING = 'ALL'

    # ===============================================================================================
    # ctor
    # ===============================================================================================

    def __init__(self, start, stop, step=1):
        """
        :param start, stop: range's boundries. Automatically converted to Date objects.
        """
        start = self.DATE_TYPE(start)
        stop = self.DATE_TYPE(stop)
        self._ordrange = range(
            self._d2o(start),
            self._d2o(stop),
            step,
        )

    @classmethod
    def empty(cls):
        """ Creates an empty range, """
        return cls(cls.max_date, cls.max_date)

    @classmethod
    def full(cls, step=1):
        """ Creates a range containing all supported dates, """
        dates = [cls.min_date, cls.max_date]
        if step < 0:
            dates = reversed(dates)
        return cls(*dates, step=step)

    @classmethod
    def _from_ordrange(cls, ordrange):
        r = cls(cls.DATE_TYPE.min, cls.DATE_TYPE.min)  # create a stub
        r._ordrange = ordrange  # replace internals
        return r

    # ===============================================================================================
    # range interface
    # ===============================================================================================

    @property
    def start(self):
        """ Same as ``range.start``. """
        return self._o2d(self._ordrange.start)

    @property
    def stop(self):
        """ Same as ``range.stop``. """
        return self._o2d(self._ordrange.stop)

    @property
    def step(self):
        """ Same as ``range.step``. """
        return self._ordrange.step

    def __iter__(self):
        """ Iterate over the ``Date``s in the range. """
        return (self._o2d(o) for o in self._ordrange)

    def __reversed__(self):
        return (self._o2d(o) for o in reversed(self._ordrange))

    def __len__(self):
        return len(self._ordrange)

    def __bool__(self):
        return bool(self._ordrange)

    def __contains__(self, date):
        """
        Is the date contained in the range?
        :param date:
            a Date, a datetime.date, or a datetime.datetime.
            For the latter, it is contained if its date is contained.
        """
        return self._d2o(date) in self._ordrange

    def index(self, date):
        """ Same as ``range.index``. """
        ordinal = self._d2o(date)
        try:
            return self._ordrange.index(ordinal)
        except ValueError:
            raise ValueError('%r is not in range' % date) from None

    def count(self, date):
        """ Same as ``range.count``. """
        return self._ordrange.count(self._d2o(date))

    def __getitem__(self, idx):
        """ Same as ``range.__getitem__``. """
        if isinstance(idx, slice):
            return self._from_ordrange(self._ordrange[idx])
        else:
            return self._o2d(self._ordrange[idx])

    def __hash__(self):
        """ Same as ``range.__hash__``. """
        return hash(self._ordrange)

    def __eq__(self, other):
        try:
            other_ordrange = other._ordrange
        except AttributeError:
            return False
        else:
            return self._ordrange == other_ordrange

    # ===========================================================================
    # str and repr
    # ===========================================================================

    def to_string(self,
                  opening_bracket='[', closing_bracket=')', *,
                  date_format=None, delim=None, step_delim=None, include_step=None,
                  empty_range_string=EMPTY_RANGE_STRING):

        if empty_range_string is not None and not self:
            return empty_range_string

        if delim is None:
            delim = self.DELIM

        if date_format is None:
            d1 = str(self.start)
            d2 = str(self.stop)
        else:
            d1 = self.start.strftime(date_format)
            d2 = self.stop.strftime(date_format)

        tokens = [opening_bracket, d1, delim, d2]

        if (include_step is True) or (include_step is None and self.step != 1):
            if step_delim is None:
                step_delim = delim
            tokens.extend([step_delim, str(self.step)])

        tokens.append(closing_bracket)
        return ''.join(tokens)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        tokens = [self.start, self.stop]
        if self.step != 1:
            tokens.append(self.step)
        return '%s(%s)' % (type(self).__name__, ', '.join([str(x) for x in tokens]))

    # ===========================================================================
    # from string
    # ===========================================================================

    @classmethod
    def from_string(cls, s, allow_non_range=True):
        """
        Create a DateRange from a string representation.

        >>> DateRange.from_string('20120202:20120303')
        DateRange(20120202, 20120303)
        >>> DateRange.from_string('[20120202:20120303)')
        DateRange(20120202, 20120303)
        >>> DateRange.from_string('20120202:20120303:7')
        DateRange(20120202, 20120303, 7)

        > DateRange.from_string('yest:today')  # if running on 20120705
        DateRange(20120704, 20120705)
        > DateRange.from_string('-1:+1')  # if running on 20120705
        DateRange(20120704, 20120706)
        """

        if s in (cls.FULL_RANGE_STRING, 'FULL'):
            return cls.full()
        if s in (cls.EMPTY_RANGE_STRING, 'EMPTY'):
            return cls.empty()

        # remove brackets:
        if s.startswith('[') and s.endswith(')'):
            s = s[1:-1]

        # split to parts:
        parts = s.split(cls.DELIM)
        n = len(parts)
        if n == 1:
            # a single-date range
            d = cls.DATE_TYPE(s)
            return cls(d, d + 1)

        elif 2 <= n <= 3:
            # start and stop, and possibly step

            def has_marker(p, m=cls.OTHER_SIDE_MARKER):
                return (p == m) or (p.startswith(m) and p[len(m)] in '+-')

            def relative_to(part, rel_to, m=cls.OTHER_SIDE_MARKER):
                offset_str = part[len(cls.OTHER_SIDE_MARKER):]
                if offset_str:
                    # e.g. '%+10'
                    offset = int(offset_str)
                else:
                    # just '%'
                    offset = 0
                return rel_to + offset

            marker1 = has_marker(parts[0])
            marker2 = has_marker(parts[1])
            if marker1:
                d2 = cls.DATE_TYPE(parts[1])
                d1 = relative_to(parts[0], d2)
            elif marker2:
                d1 = cls.DATE_TYPE(parts[0])
                d2 = relative_to(parts[1], d1)
            else:
                d1 = cls.DATE_TYPE(parts[0])
                d2 = cls.DATE_TYPE(parts[1])
            if n == 3:
                step = int(parts[2])
            else:
                step = 1
            return cls(d1, d2, step)

        else:
            raise ValueError('Invalid %s string: %r' % (cls.__name__, s))

    # ===========================================================================
    # misc
    # ===========================================================================

    def replace(self, *, start=None, stop=None, step=None):
        """ Create a range like self, with different parts (start/stop/step) """
        kwargs = {}
        kwargs['start'] = start if start is not None else self.start
        kwargs['stop'] = stop if stop is not None else self.stop
        kwargs['step'] = step if step is not None else self.step
        return type(self)(**kwargs)

    @classproperty
    def min_date(cls):
        """ The earliest date supported. """
        return cls.DATE_TYPE.min

    @classproperty
    def max_date(cls):
        """ The latest date supported. """
        return cls.DATE_TYPE.max

    def min_timestamp(self, **kwargs):
        """
        First timestamp of the range, or None if empty.
        :return: a datetime.datetime object
        """
        if self:
            return self.start.min_timestamp(**kwargs)

    def max_timestamp(self, **kwargs):
        """
        Last timestamp of the range, or None if empty.
        :return: a datetime.datetime object
        """
        if self:
            # note: self.stop-1 is not necessarily in self, if step>1. thus using self[-1]
            return self[-1].max_timestamp(**kwargs)

    def cli_repr(self):
        """
        A command-line representation of the date range.
        This is a convenience method for providing the date range to another script.
        """
        if len(self) == 1:
            return str(self[0])
        return self.to_string('', '')

    # ===========================================================================
    # Intersection
    # ===========================================================================

    def __and__(self, other):
        return self.intersection(other)

    def intersection(self, other):
        """
        Calculate the intersection of the two DateRanges and return the result as a DateRange.

        This implementation was copied (and adjusted) from rangeplus
        (https://github.com/avnr/rangeplus).
        """

        # check steps have the same sign
        if (self.step > 0) != (other.step > 0):
            raise ValueError('Intersection is undefined for steps with opposite signs: %r & %r' % (
                self, other))

        # more helpers

        def stop_min(x, y):
            return None if x is None and y is None \
                else x if y is None else y if x is None else min(x, y)

        def stop_max_inv(x, y):
            return None if x is None and y is None \
                else x if y is None else y if x is None else max(x, y)

        # return empty Range if either ranges is empty
        empty = self.empty()
        if not self or not other:
            return empty()

        # both directions are the same
        step0, step1, sign, offset = (abs(self.step), abs(other.step),
                                      (self.step > 0) - (self.step < 0), other.start - self.start)
        gcd, x, y = _egcd(step0, step1)
        interval0, interval1 = step0 // gcd, step1 // gcd  # calculate the coprime intervals
        step = interval0 * interval1 * gcd * sign
        if offset % gcd != 0:  # return empty result if offset not alligned on gcd
            return empty()

        # Apply Chinese Remainder Theorem
        # x % interval1 means inverse_mod(interval0, interval1)
        crt = (offset * interval0 * (x % interval1)) % step
        filler = 0
        if sign > 0 and offset > 0 or sign < 0 and offset < 0:
            gap = offset - crt
            filler = gap if 0 == gap % step else (gap // step + 1) * step
        start = self.start + crt + filler
        stop = stop_min(self.stop, other.stop) if sign > 0 else stop_max_inv(self.stop, other.stop)
        return type(self)(start, stop, step)

    # ===========================================================================
    # privates
    # ===========================================================================

    def _o2d(self, ordinal):
        return self.DATE_TYPE.fromordinal(ordinal)

    def _d2o(self, date):
        # Note: supports Date, datetime.date, and datetime.datetime
        return date.toordinal()


################################################################################
