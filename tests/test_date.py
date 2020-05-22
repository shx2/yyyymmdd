"""
Unit-tests for Date.
"""

import unittest
import random
import datetime
from datetime import date as DTDATE
from yyyymmdd import Date


################################################################################

TEST_DATES = [
    '20140425', '20170123', '20011024', '20240412', '19980505', '19940731', '20130724', '20000312', '20060830', '19960514', '20081104', '20020312', '20170330', '20260518', '20170930', '20050901', '20000922', '19940708', '20010719', '20070520', '20050529', '19970322', '20051115', '20200416', '20281215', '19910312', '20080920', '20230106', '20210424', '20011017', '20010107', '20220824', '20110514', '20000422', '20150314', '20041203', '19991011', '20170927', '19990621', '19990714', '20030214', '20080925', '20130726', '20170717', '20041108', '20290616', '19920105', '20250718', '19940731', '20080731',
    '10000425', '9250311', '1980628', '1270711', '13180408', '4840627', '1801030', '3300819', '10610406', '8720420', '15851008', '411120', '5161115', '8300329', '800207', '6770827', '18180226', '10340518', '3201011', '11370217', '4830224', '8260406', '11811101', '11940619', '1731124', '8560830', '15150428', '9911231', '15800716', '5631229', '1090522', '1540630', '15271029', '2581107', '1960921', '8690411', '12101118', '14530618', '16211012', '3600922', '3791229', '13080115', '6570513', '15301225', '200127', '14610625', '14131126', '6040526', '8410401', '2000511',
    '92781225', '23510906', '89171107', '84251221', '81120125', '84820722', '35420206', '83530221', '67410721', '24550108', '65030724', '47860321', '88510827', '55071024', '98220303', '87060120', '87691023', '90980920', '38660911', '84830902', '58650826', '50330118', '40410309', '96900225', '39801211', '60910520', '72370818', '68250106', '28260221', '98870806', '98550310', '84060816', '77630226', '31510206', '91120115', '24681231', '25240528', '57751010', '33230531', '33480223', '51530227', '58011225', '36290416', '41610520', '40691102', '27130412', '82390826', '26280222', '87391230', '25141114',
]


################################################################################

class DateTest(unittest.TestCase):
    """
    Tests Date class.
    """

    def test_basic(self):
        for x in TEST_DATES:
            d = Date(x)
            self.assertEqual(str(d), x)
            self.assertEqual(d.yyyy, x[:-4])
            self.assertEqual(d.mm, x[-4:-2])
            self.assertEqual(d.dd, x[-2:])
            self.assertEqual(d.year, int(x[:-4]))
            self.assertEqual(d.month, int(x[-4:-2]))
            self.assertEqual(d.day, int(x[-2:]))
            self.assertEqual(d, Date.fromordinal(d.toordinal()))
            self.assertGreater(d, Date.fromordinal(d.toordinal() - 1))
            self.assertLess(d, Date.fromordinal(d.toordinal() + 1))
            self.assertEqual(d, Date(d))
            self.assertEqual(d, Date(d.as_datetime_date()))
            self.assertEqual(DTDATE, type(d.as_datetime_date()))

        self.assertEqual(Date.min.as_datetime_date(), DTDATE.min)
        self.assertEqual(Date.max.as_datetime_date(), DTDATE.max)

    def test_creation(self):
        for x in TEST_DATES:
            # from string
            d = Date(x)
            # from string, secondary format:
            self.assertEqual(d, Date('%s-%s-%s' % (d.yyyy, d.mm, d.dd)))
            # from int:
            self.assertEqual(d, Date(int(x)))
            # from parts:
            self.assertEqual(d, Date(d.year, d.month, d.day))
            # from Date
            self.assertEqual(d, Date(d))

    def test_aliases_and_delta(self):
        today = Date('today')
        yest = Date('yesterday')
        tomorrow = Date('tomorrow')
        self.assertLess(yest, today)
        self.assertLess(today, tomorrow)
        self.assertEqual(tomorrow - 1, today)
        self.assertEqual(today - 1, yest)
        self.assertEqual(tomorrow, today + 1)
        self.assertEqual(today, yest + 1)
        self.assertEqual(tomorrow - today, 1)
        self.assertEqual(today - yest, 1)
        self.assertEqual(yest - tomorrow, -2)
        self.assertEqual(Date('MIN').as_datetime_date(), DTDATE.min)
        self.assertEqual(Date('MAX').as_datetime_date(), DTDATE.max)

    def test_replace(self):
        d = Date('20000510')
        self.assertEqual(d.replace(), d)
        self.assertEqual(d.replace(year=3000).day, d.day)
        self.assertEqual(d.replace(year=3000).month, d.month)
        self.assertEqual(d.replace(year=3000).year, 3000)
        self.assertEqual(d.replace(month=11).day, d.day)
        self.assertEqual(d.replace(month=11).month, 11)
        self.assertEqual(d.replace(month=11).year, d.year)
        self.assertEqual(d.replace(day=11).day, 11)
        self.assertEqual(d.replace(day=11).month, d.month)
        self.assertEqual(d.replace(day=11).year, d.year)
        self.assertEqual(d.replace(year=3000, month=11, day=22), Date(30001122))
        self.assertEqual(type(d.replace(year=3000, month=11, day=22)), Date)

    def test_add(self):
        for x in TEST_DATES:
            d = Date(x)
            for dt in (10, 100, 1000, -1000, -100, -10):
                d2 = d + dt
                self.assertEqual((d2.as_datetime_date() - d.as_datetime_date()).days, dt)
                self.assertEqual(d2, DTDATE.fromordinal(d.toordinal() + dt))

    def test_subtraction_int(self):
        for x in TEST_DATES:
            d = Date(x)
            for dt in (10, 100, 1000, -1000, -100, -10):
                d2 = d - dt
                self.assertEqual((d2.as_datetime_date() - d.as_datetime_date()).days, -dt)
                self.assertEqual(d2, DTDATE.fromordinal(d.toordinal() - dt))

    def test_subtraction_date(self):
        for x1 in TEST_DATES[:20]:
            for x2 in TEST_DATES[:20]:
                d1 = Date(x1)
                d2 = Date(x2)
                self.assertEqual(d1 - d2, (d1.as_datetime_date() - d2.as_datetime_date()).days)

    def test_year_start_end(self):
        for x in TEST_DATES:
            d = Date(x)
            ys = d.year_start()
            ye = d.year_end()
            self.assertEqual(ys.year, d.year)
            self.assertEqual(ys.month, 1)
            self.assertEqual(ys.day, 1)
            self.assertEqual(ye.year, d.year)
            self.assertEqual(ye.month, 12)
            self.assertEqual(ye.day, 31)

    def test_month_start_end(self):
        for x in TEST_DATES:
            d = Date(x)
            ms = d.month_start()
            self.assertEqual(ms.year, d.year)
            self.assertEqual(ms.month, d.month)
            self.assertEqual(ms.day, 1)

            # naively find month end
            z = d.as_datetime_date()
            while (z + datetime.timedelta(days=1)).month == z.month:
                z += datetime.timedelta(days=1)
            me = d.month_end()
            self.assertEqual(me.year, d.year)
            self.assertEqual(me.month, d.month)
            self.assertEqual(me.year, z.year)
            self.assertEqual(me.month, z.month)
            self.assertEqual(me.day, z.day)


################################################################################

def _generate_test_dates():
    """
    This function is run manually to generate TEST_DATES.
    """
    margin = datetime.timedelta(days=1000)
    print('TEST_DATES = [')
    for d1, d2 in [
            (19900101, 20300101),
            (DTDATE.min + margin, 19000101),
            (21000101, DTDATE.max - margin)
            ]:
        o1 = Date(d1).toordinal()
        o2 = Date(d2).toordinal()
        print('    ', end='')
        for i in range(50):
            o = random.randint(o1, o2)
            print('%r, ' % str(Date.fromordinal(o)), end='')
        print()
    print(']')


################################################################################
