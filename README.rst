=========
yyyymmdd
=========

Convenient Date and DateRange classes.


``Date``
====================================

A ``yyyymmdd``-formatted date.

``Date`` is a subclass of ``datetime.date``, and is mostly (but not fully) compatible with it.

It supports flexible creation of ``Date`` objects, e.g.: from a yyyymmdd string, from
delta (number of days relative to today), aliases ('yesterday', 'today', 'MIN', 'MAX', etc.),
from a ``datetime.date`` object, etc.

It defines convenient date arithmetic: ``Date +/- int => Date``, ``Date - Date => int``.

Here is an example::

    >>> from yyyymmdd import Date
    >>> import datetime
    >>>
    >>> Date.today()
    Date(20200522)
    >>> Date('-7')  # a week ago
    Date(20200515)
    >>> Date(20191123) == Date('20191123') == Date('2019-11-23') == Date(datetime.date(2019, 11, 23))
    True
    >>> Date(20191123).replace(month=1, day=1)
    Date(20190101)
    >>> Date('19991231') + 1
    Date(20000101)
    >>> Date('tomorrow') - Date('yesterday')
    2
    >>> Date('tomorrow') - 1 == Date('today')
    True
    >>> x = Date(20191123)
    >>> x.yyyy + x.mm + x.dd
    '20191123'



``DateRange``
====================================

A ``DateRange`` is a `range <https://docs.python.org/3.8/library/functions.html#func-range>`_ -like type,
whose elements are ``Date`` objects.

This class mostly follows the semantics of the builtin ``range`` type.  E.g.,
stop is exclusive, behavior of steps, negative steps, slicing,
``range1 == range2`` iff ``tuple(range1) == tuple(range2)``, etc.

Creation of ``DateRange`` objects is flexible.  ``start`` and ``stop`` parameters are converted
to ``Date`` automatically.  See ``Date`` class for values which can be converted.


Here is an example::

    from yyyymmdd import Date, DateRange

    >>> from yyyymmdd import Date, DateRange
    >>>
    >>> len(DateRange('today', 'today'))  # empty
    0
    >>> DateRange.from_string('yesterday:yesterday') == DateRange.empty()
    True
    >>> len(DateRange.from_string('-7:-1'))  # start and stop are relative to today
    6
    >>> DateRange.from_string('2020501')  # a singleton range
    DateRange(2020501, 2020502)
    >>> x = DateRange.from_string('2020401:2020515:7')  # 1-week step
    >>> list(x)
    [Date(2020401), Date(2020408), Date(2020415), Date(2020422), Date(2020429), Date(2020506), Date(2020513)]
    >>> x[0], x[-1]
    (Date(2020401), Date(2020513))
    >>> x[1:3]
    DateRange(2020408, 2020422, 7)
    >>> Date(2020422) in x
    True
    >>> list(DateRange.from_string('2020515:2020401:-7'))  # negative step
    [Date(2020515), Date(2020508), Date(2020501), Date(2020424), Date(2020417), Date(2020410), Date(2020403)]
    >>> DateRange.from_string('20200101:%+31')  # "%" means "the date on the other side"
    DateRange(20200101, 20200201)
    >>> DateRange.from_string('%-365:20200101')  # "%" means "the date on the other side"
    DateRange(20190101, 20200101)



``ArgumentParser`` integration, powered by ``apegears``
========================================================

The ``Date`` and ``DateRange`` types can be used as cli argument types, when using
`apegears' <https://pypi.org/project/apegears/>`_ ``ArgumentParser``.

Here is an example::

    >>> from yyyymmdd import Date, DateRange
    >>> from apegears import ArgumentParser
    >>>
    >>> parser = ArgumentParser()
    >>> parser.add_optional('x', type=Date)
    >>> parser.add_optional('dates', 'd', type=DateRange)

    >>> print(parser.parse_args('-x 20191123 --dates yest:tomorrow'.split()))
    Namespace(dates=DateRange(20200521, 20200523), x=Date(20191123))  # if today is 20200522

    >>> print(parser.parse_args('-h'.split()))
    usage: [-h] [-x DATE] [--dates DATE_RANGE]

    optional arguments:
      -h, --help            show this help message and exit
      -x DATE               Date, like: yyyymmdd, +days, -days, "yesterday", etc.
      --dates DATE_RANGE, -d DATE_RANGE
                            DateRange, like: "DATE:DATE" or "DATE:DATE:STEP"

If you prefer using the standard ``argparse.ArgumentParser``, you can define Date arguments using ``type=Date``, and
DateRange arguments using ``type=DateRange.from_string``.  This isn't as powerful as using ``apegears``
(no default argument names, no default help message, no default metavar, etc.).


Installation
====================================

Using pip::

    pip install yyyymmdd
