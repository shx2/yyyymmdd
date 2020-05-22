"""
Convenient Date and DateRange classes.
"""

from .date import Date
from .range import DateRange

# we import .argparse, for the side effect
from . import argparse as _argparse

Date, DateRange, _argparse  # pyflakes
