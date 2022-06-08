"""
Unit-tests for DateRange.
"""

import unittest
import math
import pickle
import random
from yyyymmdd import Date, DateRange
from .test_date import TEST_DATES

################################################################################

D1 = Date(TEST_DATES[0])
D2 = Date(TEST_DATES[1])

TEST_RANGES = dict(
    empty=DateRange.empty(),
    single=DateRange(D1, D1 + 1),
    short=DateRange(D1, D1 + 5),
    long=DateRange.full()[:50000],
)


################################################################################

class DateRangeTest(unittest.TestCase):
    """
    Tests DateRange class.
    """

    def test_basic(self):
        for r in TEST_RANGES.values():
            for step in (1, 2, 100):
                r = r.replace(step=step)
                datelist = list(r)

                # len:
                self.assertEqual(len(r), len(datelist))
                # reversed:
                self.assertEqual(list(reversed(r)), list(reversed(datelist)))

                if len(r) >= 2:
                    # step:
                    self.assertEqual(step, r[1] - r[0])

                if r:
                    self.assertEqual(r.start, next(iter(r)))

                    # getitem:
                    for idx in [0, 1, 10, -1]:
                        if idx < len(r):  # also negative idx
                            d = datelist[idx]
                            self.assertEqual(r[idx], d)
                            self.assertIn(d, r)
                            self.assertIn(d.as_datetime_date(), r)
                            self.assertEqual(1, r.count(d))
                            self.assertEqual(1, r.count(d.as_datetime_date()))
                        else:
                            self.assertRaises(IndexError, lambda: r[idx])

                    # contains, count, index:
                    for d in (D1, D2):
                        self.assertEqual(d in r, d in datelist)
                        self.assertEqual(d.as_datetime_date() in r, d in datelist)
                        self.assertEqual(r.count(d), datelist.count(d))
                        self.assertEqual(r.count(d.as_datetime_date()), datelist.count(d))
                        if d in datelist:
                            self.assertEqual(r.index(d), datelist.index(d))
                            self.assertEqual(r.index(d.as_datetime_date()), datelist.index(d))
                        else:
                            self.assertRaises(ValueError, r.index, d)
                            self.assertRaises(ValueError, r.index, d.as_datetime_date())

    def test_creation(self):
        start = D1
        stop = D1 + 20
        # Date
        r0 = DateRange(start, stop)
        # datetime.date
        r = DateRange(start.as_datetime_date(), stop.as_datetime_date())
        self.assertEqual(r0, r)
        # string
        r = DateRange(str(start), str(stop))
        self.assertEqual(r0, r)
        # int
        r = DateRange(int(str(start)), int(str(stop)))
        self.assertEqual(r0, r)
        # relative to today
        r = DateRange('-10', '+10')
        self.assertEqual(r, DateRange(Date.today() - 10, Date.today() + 10))

    def test_from_string(self):
        # a single date
        r = DateRange(D1, D1 + 1)
        self.assertEqual(r, DateRange.from_string(str(D1)))
        self.assertEqual(r, DateRange.from_string(str(r)))
        self.assertEqual(r, DateRange.from_string(D1.strftime('%Y-%m-%d')))
        # start and stop
        r = DateRange(D1, D1 + 100)
        self.assertEqual(r, DateRange.from_string(str(r)))
        self.assertEqual(r, DateRange.from_string('%s:%s' % (r.start, r.stop)))
        # start, stop and step
        r = DateRange(D1, D1 + 100, 7)
        self.assertEqual(r, DateRange.from_string(str(r)))
        self.assertEqual(r, DateRange.from_string('%s:%s:%s' % (r.start, r.stop, r.step)))
        # relatives and negatives
        r1 = DateRange('+30', -50, -2)
        r2 = DateRange.from_string('+30:-50:-2')
        self.assertEqual(r1, r2)
        self.assertEqual(len(r2), 40)
        # aliases
        self.assertEqual(DateRange.from_string('NONE'), DateRange.empty())
        self.assertEqual(DateRange.from_string('EMPTY'), DateRange.empty())
        self.assertEqual(DateRange.from_string('ALL'), DateRange.full())
        self.assertEqual(DateRange.from_string('FULL'), DateRange.full())
        for r in [DateRange.empty(), DateRange.full()]:
            self.assertEqual(r, DateRange.from_string(str(r)))

    def test_step(self):
        for n in (0, 1, 2, 100):
            for step in (1, 2, 10, 1000):
                r = DateRange(D1, D1 + n, step)
                self.assertEqual(len(r), math.ceil(n / step))
                for d1, d2 in zip(r[:-1], r[1:]):
                    self.assertEqual(d2 - d1, step)

    def test_negative_step(self):
        for n in (0, 1, 2, 100):
            for step in (1, 2, 10, 1000):
                r = DateRange(D1, D1 - n, -step)
                self.assertEqual(len(r), math.ceil(n / step))
                for d1, d2 in zip(r[:-1], r[1:]):
                    self.assertEqual(d2 - d1, -step)

    def test_equality(self):
        # empties are equal
        self.assertEqual(DateRange(D1, D1), DateRange(D1 + 5, D1 + 1))
        self.assertNotEqual(DateRange(D1, D1), DateRange(D1, D1 + 1))
        # singles with different stop are equal
        self.assertEqual(DateRange(D1, D1 + 1, 10), DateRange(D1, D1 + 9, 10))
        self.assertNotEqual(DateRange(D1, D1 + 1, 10), DateRange(D1, D1 + 9, 7))
        # singles with different step are equal
        self.assertEqual(DateRange(D1, D1 + 1), DateRange(D1, D1 + 100, 200))
        self.assertNotEqual(DateRange(D1, D1 + 1), DateRange(D1, D1 + 100, 70))

    def test_pickle(self):
        for r1 in TEST_RANGES.values():
            r2 = pickle.loads(pickle.dumps(r1))
            self.assertEqual(r1, r2)
            self.assertEqual(type(r1), type(r2))

    def test_mereology(self):
        random.seed(42)
        for _ in range(1000):
            d1 = DateRange.DATE_TYPE.fromordinal(random.randint(0, 1000000))
            d2 = d1 + random.randint(1, 100)
            dr = DateRange(d1, d2)  # non-empty
            self.assertTrue(DateRange.empty().is_proper_part(dr))
            self.assertTrue(DateRange.empty().is_part(dr))
            self.assertFalse(dr.is_proper_part(dr))
            self.assertTrue(dr.overlaps(dr))
            self.assertTrue(dr.is_part(dr))
            self.assertTrue(dr.underlaps(dr))
            self.assertTrue(dr | dr == dr)
            self.assertTrue((dr - dr) == [])

        self.assertFalse(DateRange.empty().overlaps(DateRange.empty()))

    def test_mereology2(self):
        self.assertTrue(
            DateRange.from_string("20220103:20220106").overlaps(
                DateRange.from_string("20220103:20220110")
            )
        )
        self.assertTrue(
            DateRange.from_string("20220103:20220106").underlaps(
                DateRange.from_string("20220103:20220110")
            )
        )
        self.assertTrue(
            DateRange.from_string("20220103:20220106").is_proper_part(
                DateRange.from_string("20220103:20220110")
            )
        )
        self.assertTrue(
            DateRange.from_string("20220103:20220106").is_part(
                DateRange.from_string("20220103:20220110")
            )
        )
        self.assertFalse(
            DateRange.from_string("20220103:20220110").is_proper_part(
                DateRange.from_string("20220103:20220106")
            )
        )
        self.assertFalse(
            DateRange.from_string("20220103:20220110").is_part(
                DateRange.from_string("20220103:20220106")
            )
        )
        self.assertTrue(
            DateRange.from_string("20220102:20220106").overlaps(
                DateRange.from_string("20220103:20220110")
            )
        )
        self.assertTrue(
            DateRange.from_string("20220102:20220106").underlaps(
                DateRange.from_string("20220103:20220110")
            )
        )
        self.assertFalse(
            DateRange.from_string("20220102:20220106").is_proper_part(
                DateRange.from_string("20220103:20220110")
            )
        )
        self.assertFalse(
            DateRange.from_string("20220102:20220106").is_part(
                DateRange.from_string("20220103:20220110")
            )
        )
        self.assertFalse(
            DateRange.from_string("20220103:20220110").is_proper_part(
                DateRange.from_string("20220102:20220106")
            )
        )
        self.assertFalse(
            DateRange.from_string("20220103:20220110").is_part(
                DateRange.from_string("20220102:20220106")
            )
        )
        self.assertEqual(
            DateRange.from_string("20220103:20220110")
            & DateRange.from_string("20211231:20220106"),
            DateRange.from_string("20220103:20220106"),
        )
        self.assertEqual(
            DateRange.from_string("20220103:20220110")
            - DateRange.from_string("20211231:20220106"),
            [DateRange.from_string("20220106:20220110")],
        )
        self.assertEqual(
            (
                DateRange.from_string("20220103:20220110")
                & DateRange.from_string("20211231:20220106")
            )
            | (
                DateRange.from_string("20220103:20220110")
                - DateRange.from_string("20211231:20220106")
            )[0],
            DateRange.from_string("20220103:20220110"),
        )
        self.assertEqual(
            DateRange.from_string("20220103:20220110")
            - DateRange.from_string("20220106:20220113"),
            [DateRange.from_string("20220103:20220106")],
        )
        self.assertEqual(
            DateRange.from_string("20220103:20220110")
            - DateRange.from_string("20220104:20220108"),
            [
                DateRange.from_string("20220103:20220104"),
                DateRange.from_string("20220108:20220110"),
            ],
        )
        self.assertEqual(
            DateRange.from_string("20220103:20220110")
            - DateRange.from_string("20220101:20220102"),
            [DateRange.from_string("20220103:20220110")],
        )
        self.assertEqual(
            DateRange.from_string("20220105:20220110")
            - DateRange.from_string("20220101:20220107"),
            [DateRange(20220107, 20220110)],
        )
        self.assertEqual(
            DateRange.from_string("20220101:20220107")
            - DateRange.from_string("20220105:20220110"),
            [DateRange(20220101, 20220105)],
        )

    def test_mereology_errors(self):
        dr1 = DateRange(Date("2014-01-01"), Date("2014-01-11"), 2)
        dr2 = DateRange(Date("2014-01-01"), Date("2014-01-05"), 2)
        self.assertTrue(dr1.overlaps(dr2))
        with self.assertRaises(NotImplementedError):
            dr1.is_adjacent(dr2)
        with self.assertRaises(NotImplementedError):
            dr1.underlaps(dr2)
        with self.assertRaises(NotImplementedError):
            dr1.is_proper_part(dr2)
        with self.assertRaises(NotImplementedError):
            dr1.is_part(dr2)
        with self.assertRaises(NotImplementedError):
            dr2.is_proper_part(dr1)
        with self.assertRaises(NotImplementedError):
            dr2.is_part(dr1)
        with self.assertRaises(NotImplementedError):
            dr1 - dr2
        with self.assertRaises(NotImplementedError):
            dr1 | dr2
        with self.assertRaises(ValueError):
            DateRange(Date("2014-01-01"), Date("2014-01-11")).union(
                DateRange(Date("2014-01-12"), Date("2014-01-16"))
            )


################################################################################
