"""
Integration with ``apegears.ArgumentParser``, by registering Date and DateRange
argument type specs.
"""

try:

    from apegears import register_spec

except ImportError:

    # apegears not found
    pass

else:

    from .date import Date
    from .range import DateRange

    # ===============================================================================================
    #  Date
    # ===============================================================================================

    date_spec = dict(
        names=['date', 'd'],
        from_string=Date,
        help='Date, like: yyyymmdd, +days, -days, "yesterday", etc.',
        metavar='DATE',
    )
    register_spec(Date, date_spec)

    # ===============================================================================================
    #  DateRange
    # ===============================================================================================

    daterange_spec = dict(
        names=['dates', 'd'],
        from_string=DateRange.from_string,
        help='DateRange, like: "DATE:DATE" or "DATE:DATE:STEP"',
        metavar='DATE_RANGE',
    )
    register_spec(DateRange, daterange_spec)
