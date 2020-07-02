#!etc/bin/python3
"""
File name: date_picker.py
Author: Johannes Roling
Date created: 11/28/2018
Date last modified: 04/10/2019
Python Version: 3.6.3

This module should help to handle timestamps.
If you are familiar with the ISO Format from datetime or time use this library.

"""

from builtins import Exception
from datetime import datetime as dt
from datetime import timedelta
from calendar import monthrange

month_name = (
    'Jan', 'Feb', 'Mar', 'Apr',
    'Mai', 'Jun', 'Jul', 'Aug',
    'Sep', 'Okt', 'Nov', 'Dez')
CONST_SEP = 'T'


class Timestamp:
    """ This class helps to handle timestamps in an isoformat.

    The class uniform the methods beneath and should be easy to understand.
    On the parameters self.timestamp_start and self.timestamp_end you can use
    the functions of datetime.datetime.

    """

    __slots__ = ['timestamp_start', 'timestamp_end', 'span', 'quarter']

    def __init__(
            self, start, end, span=None,
            quarter=None):
        """Initialize the class timestamp.

        :param start: The start date of the time-span
        :param end: The end date of the time-span
        :param span: first or second half of the year, if given else None
        :param quarter: quarter of the year, if given else None

        :type start: datetime.datetime()
        :type end: datetime.datetime()
        :type span: int
        :type quarter: int

        """
        if start > end:
            self.timestamp_start = end
            self.timestamp_end = start
        else:
            self.timestamp_start = start
            self.timestamp_end = end
        self.span = span
        self.quarter = quarter

    def __str__(self):
        """Formeted ouput of start and end time.

        Format: '%Y-%m-%dT%H:%M:%S, %Y-%m-%dT%H:%M%S'

        """

        return self.start() + ',' + self.end()

    def __add__(self, other):
        """Adds minutes to the timestamp_start and timestamp_end.

        **Span and Quarter will to not be recalculate**
        :param other: minutes to add
        :return: timestamp
        """
        start = self.timestamp_start + timedelta(minutes=other)
        end = self.timestamp_end + timedelta(minutes=other)
        # todo __sub__: recalculation of the span and quarter
        return Timestamp(start, end, self.span, self.quarter)

    def __sub__(self, other):
        """Subtracts minutes from the timestamp_start and timestamp_end.

        **Span and Quarter will to not be recalculate**
        :param other: minutes to substract
        :return: timestamp
        """
        start = self.timestamp_start - timedelta(minutes=other)
        end = self.timestamp_end - timedelta(minutes=other)
        # todo __sub__: recalculation of the span and quarter
        return Timestamp(start, end, self.span, self.quarter)

    def __iter__(self):
        yield 'timestampStart', self.start()
        yield 'timestampEnd', self.end()

    def __lt__(self, other):
        if not isinstance(other, Timestamp):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.timestamp_start < other.timestamp_start and self.timestamp_end < other.timestamp_end

    def __le__(self, other):
        if not isinstance(other, Timestamp):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.timestamp_start <= other.timestamp_start or self.timestamp_end <= other.timestamp_end

    def __eq__(self, other):
        if not isinstance(other, Timestamp):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.timestamp_start == other.timestamp_start and self.timestamp_end == other.timestamp_end

    def __ne__(self, other):
        if not isinstance(other, Timestamp):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.timestamp_start != other.timestamp_start and self.timestamp_end != other.timestamp_end

    def __gt__(self, other):
        if not isinstance(other, Timestamp):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.timestamp_start > other.timestamp_start and self.timestamp_end > other.timestamp_end

    def __ge__(self, other):
        if not isinstance(other, Timestamp):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.timestamp_start >= other.timestamp_start or self.timestamp_end >= other.timestamp_end

    def start(self):
        """Returns a str of the start date in an isoformat.

        :return: formatted str of the start date ('%Y-%m-%dT%H:%M%S')
        :rtype: str
        """
        return self.timestamp_start.isoformat(
            sep=CONST_SEP, timespec='seconds')

    def start_unix(self):
        """Returns a str of the start date in an unix format.

        :return: formatted str of the start date ('%S')
        :rtype: str
        """
        return str(int(self.timestamp_start.timestamp()))

    def add_start(self, add):
        """Adds minutes to the timestamp_start.

        When the start timestamp is bigger than the end timestamp, the function swaps start and end.
        **Span and Quarter will to not be recalculate**
        :param add: minutes to add
        :return: timestamp
        """
        start = self.timestamp_start + timedelta(minutes=add)
        if start > self.timestamp_end:
            return Timestamp(self.timestamp_end, start, self.span, self.quarter)
        # todo add_start: recalculation of the span and quarter
        return Timestamp(start, self.timestamp_end, self.span, self.quarter)

    def sub_start(self, sub):
        """Subtracts minutes from the timestamp_start.

        **Span and Quarter will to not be recalculate**
        :param sub: minutes to substract
        :return: timestamp
        """
        start = self.timestamp_start - timedelta(minutes=sub)
        if start > self.timestamp_end:
            return Timestamp(self.timestamp_end, start, self.span, self.quarter)
        # todo sub_start: recalculation of the span and quarter
        return Timestamp(start, self.timestamp_end, self.span, self.quarter)

    def end(self):
        """Returns a str of the end date in an isoformat.

        :return: formatted str of the end date ('%Y-%m-%dT%H:%M%S')
        :rtype: str
        """
        return self.timestamp_end.isoformat(
            sep=CONST_SEP, timespec='seconds')

    def end_unix(self):
        """Returns a str of the end date in an unix format.

        :return: formatted str of the end date ('%S')
        :rtype: str
        """
        return str(int(self.timestamp_end.timestamp()))

    def add_end(self, add):
        """Adds minutes to the timestamp_end.

        **Span and Quarter will to not be recalculate**
        :param add: minutes to add
        :return: timestamp
        """
        end = self.timestamp_end + timedelta(minutes=add)
        if end < self.timestamp_start:
            return Timestamp(end, self.timestamp_start, self.span, self.quarter)
        # todo add_end: recalculation of the span and quarter
        return Timestamp(self.timestamp_start, end, self.span, self.quarter)

    def sub_end(self, sub):
        """Subtracts minutes from the timestamp_end.

        When the start timestamp is smaller than the end timestamp, the function swaps start and end.
        **Span and Quarter will to not be recalculate**
        :param sub: minutes to substract
        :return: timestamp
        """
        end = self.timestamp_end - timedelta(minutes=sub)
        if end < self.timestamp_start:
            return Timestamp(end, self.timestamp_start, self.span, self.quarter)
        # todo sub_end: recalculation of the span and quarter
        return Timestamp(self.timestamp_start, end, self.span, self.quarter)


def this_year_ts():
    """Returns the time-span of the this year from the 1st jan. at 0 o'clock till the first of this januar next year.

    **Example:**
    Date of the example:2018-10-29
    print(date_picker.this_year_ts())
    '2018-01-01T00:00:00,2019-01-01T00:00:00'

    :returns: class timestamp

    """

    timestamp_start = dt(
        dt.now().year,
        1, 1)

    timestamp_end = dt(
        dt.now().year + 1,
        1, 1)

    return Timestamp(timestamp_start, timestamp_end)


def completed_month_this_year():
    """Returns the time-span of the this year from the 1st jan. at 0 o'clock till the first of this month.

    **Example:**
    Date of the example:2018-10-29
    print(date_picker.completed_month_this_year())
    '2018-01-01T00:00:00,2018-10-01T00:00:00'

    :returns: class timestamp

    """
    timestamp_start = dt(
        dt.now().year,
        1, 1)

    timestamp_end = dt(
        dt.now().year,
        dt.now().month,
        1)

    if '-01-01T00:00:00' in timestamp_end.isoformat(sep='T', timespec='seconds'):
        timestamp_start = dt(dt.now().year - 1, 1, 1)
        timestamp_end = dt(dt.now().year, dt.now().month, 1)

    return Timestamp(timestamp_start, timestamp_end)


def last_year_ts():
    """Returns the time-span of the last enclosed year.

    From the 1st jan. at 0 o'clock till the 1st jan of the following year at 0 o'clock.

    **Example:**
    Date of the example: 2018-03-02
    print(date_picker.last_year_ts())
    '2017-01-01T00:00:00,2018-01-01T00:00:00'

    :returns: class timestamp

    """

    last_year = dt.now().year - 1

    timestamp_start = dt(
        last_year,
        1, 1)

    timestamp_end = dt(
        dt.now().year,
        1, 1)

    return Timestamp(timestamp_start, timestamp_end)


def last_half_year_ts():
    """Returns the time span of the last enclosed half-year from

    1. the 1st jan. at 0 o'clock till the 1st jun. of the year at 0 o'clock.
    2. the 1st jun. at 0 o'clock from the last year till the 1st jan. of the following year at 0 o'clock.

    Supports span in the timestamp class

    **Example:**
    Date of the example: 2018-03-02
    print(date_picker.lastHalfYearTS())
    '2017-06-01T00:00:00,2018-01-01T00:00:00'

    :returns: class timestamp

    """

    time_span = {
        1: (1, 6),
        2: (6, 1)
    }

    year = dt.now().year
    span = 2 if (dt.now().month <= 6) else 1

    timestamp_start = dt(
        year if (span == 1) else year - 1,
        time_span[span][0], 1)

    timestamp_end = dt(
        year,
        time_span[span][1], 1)

    return Timestamp(timestamp_start, timestamp_end, span=span)


def last_quarter_ts():
    """Returns the time-span of the last enclosed quarter from

    1. the 1st jan. at 0 o'clock till the 1st apr. of the year at 0 o'clock.
    2. the 1st apr. at 0 o'clock till the 1st jul. of the year at 0 o'clock.
    3. the 1st jul. at 0 o'clock till the 1st okt. of the year at 0 o'clock.
    4. the 1st okt. at 0 o'clock from the last year till the 1st jan. of the year at 0 o'clock.

    Supports quarter in the timestamp class

    **Example:**
    Date of the example: 2018-03-02
    print(date_picker.lastQuarterTS())
    '2017-10-01T00:00:00,2018-01-01T00:00:00'

    :returns: class timestamp

    """

    time_span = {
        1: (10, 1),
        2: (1, 4),
        3: (4, 7),
        4: (7, 10)
    }

    year = dt.now().year
    month = dt.now().month
    span = 0

    if month <= 3:
        span = 1
    elif month <= 6:
        span = 2
    elif month <= 9:
        span = 3
    elif month <= 12:
        span = 4

    timestamp_start = dt(
        year if (span != 1) else year - 1,
        time_span[span][0], 1)

    timestamp_end = dt(
        year,
        time_span[span][1], 1)

    return Timestamp(timestamp_start, timestamp_end, quarter=span)


def last_month_ts():
    """"Returns the time span of the last month

    from the 1st at 0 o'clock till the 1st of the following month at 0 o'clock.

    **Example:**
    Date of the example: 2018-03-02
    print(date_picker.last_month_ts())
    '2018-02-01T00:00:00,2018-03-01T00:00:00'

    :returns: class timestamp

    """

    year = dt.now().year
    month = dt.now().month

    timestamp_end = dt(year, month, 1)
    tmp = timestamp_end - timedelta(7)
    timestamp_start = timestamp_end - timedelta(monthrange(tmp.year, tmp.month)[1])

    return Timestamp(timestamp_start, timestamp_end)


def last_24_hours_ts():
    """Returns the time-span of the last 24 hours. Starttime is the local time now.

    **Example:**
    Date of the example: 2018-03-02 20:04:00
    print(date_picker.last7Days())
    '2018-02-23T20:04:00,2018-03-02T20:04:00'

    :returns: class timestamp

    """

    timestamp_end = dt.now()

    timestamp_start = timestamp_end - timedelta(hours=24)

    return Timestamp(timestamp_start, timestamp_end)


def last_7_days_ts():
    """Returns the time-span of the last seven days. Starttime is the local time now.

    **Example:**
    Date of the example: 2018-03-02 20:04:00
    print(date_picker.last7Days())
    '2018-02-23T20:04:00,2018-03-02T20:04:00'

    :returns: class timestamp

    """

    timestamp_end = dt.now()

    timestamp_start = timestamp_end - timedelta(days=7)

    return Timestamp(timestamp_start, timestamp_end)


def last_12_month_ts():
    """Returns the time-span of the last 365 days. Starttime is the local time now.

    **Example:**
    Date of the example: 2019-04-03T08:16:23
    print(date_picker.last_12_month_ts())
    '2018-04-03T08:16:23,2019-04-03T08:16:23'

    :returns: class timestamp

    """

    timestamp_end = dt.now()

    timestamp_start = timestamp_end - timedelta(days=365)

    return Timestamp(timestamp_start, timestamp_end)


def control(
        year: int, month: int = 1, day: int = 1, hour: int = 1,
        minute: int = 1, half: int = 1, quarter: int = 1, week: int = 1):
    """Control function. Controls if the given time is possible.

    :param year: the year to control
    :param month: the month
    :param day: the day
    :param hour: the hour
    :param minute: the minute
    :param half: first or second half of the year
    :param quarter: value 1-4, for the quarter of the year
    :param week: value 1 - the last week of the year

    :type year: int
    :type month: int
    :type day: int
    :type hour: int
    :type minute: int
    :type half: int
    :type quarter: int
    :type week: int

    :returns: True if the time-span is possible or false if impossible
    :rtype: bool

    """

    def last_week_in_the_year(p_year):
        last_week_day = 31
        while dt(p_year, 12, last_week_day).isocalendar()[1] == 1:
            last_week_day -= 1
        return dt(p_year, 12, last_week_day).isocalendar()[1]

    try:
        if not (1970 < year < dt.max.year):
            raise Exception(
                'The year ' + str(year) + ' is invalid.\nChoose a year between 1970 and ' + str(dt.max.year))
        if not (0 < month < 13):
            raise Exception('The month of the year is invalid.\nChoose between 1 and 12')
        if not (0 < day <= monthrange(year, month)[1]):
            raise Exception(
                'The day of the month is invalid.\nChoose between 1 and ' + str(monthrange(year, month)[1]))
        if not (0 <= hour < 24):
            raise Exception('hour value is over or under 24 hours')
        if not (0 <= minute < 60):
            raise Exception('min value is over or under 60 min')
        if not (0 < half < 3):
            raise Exception('The half of the year is invalid.\nChoose between 1 or 2')
        if not (0 < quarter < 5):
            raise Exception('The quarter of the year is invalid.\nChoose between 1,2,3 or 4')
        if not (0 < week < last_week_in_the_year(year)):
            raise Exception(
                'The week of the year is invalid.\nChoose between 1 and '
                + str(last_week_in_the_year(year)))

    except Exception as fail:
        print(fail)
        return True
    return False


def year_ts(year: int):
    """Returns the time-span of the given year from

    the 1st jan. at 0 o'clock till the 1st jan. of the following year at 0 o'clock.
    :param year: Year of the wanted time-span
    :type year: int

    **Example:**
    Date of the example: 2018-03-02
    print(date_picker.yearTS(2011))
    '2011-01-01T00:00:00,2012-01-01T00:00:00'

    :returns: class timestamp

    """

    if control(year):
        return None

    timestamp_start = dt(
        year,
        1, 1)

    timestamp_end = dt(
        year + 1,
        1, 1)

    return Timestamp(timestamp_start, timestamp_end, year)


def half_year_ts(year: int, half: int = 1):
    """Returns the time span of the give half of the year from

    1. the 1st jan. at 0 o'clock till the 1st jun. of the year at 0 o'clock.
    2. the 1st jun. at 0 o'clock from the last year till the 1st jan. of the following year at 0 o'clock.
    If the parameters are invalid :returns: None

    :param year: Year of the wanted time-span
    :param half: first or second half of the year
    :type half: int
    :type year: int

    Supports span in the timestamp class

    **Example:**
    Date of the example: 2018-03-02
    print(date_picker.halfYearTS(2011,2))
    '2011-06-01T00:00:00,2012-01-01T00:00:00'

    :returns: class timestamp

    """

    if control(year=year, half=half):
        return None

    time_span = {
        1: (1, 6),
        2: (6, 1)
    }

    timestamp_start = dt(
        year,
        time_span[half][0], 1)

    timestamp_end = dt(
        year if (half != 2) else year + 1,
        time_span[half][1], 1)

    return Timestamp(timestamp_start, timestamp_end, span=half)


def quarter_ts(year: int, quarter: int):
    """Returns the time-span of the given quarter and year from

    1. the 1st jan. at 0 o'clock till the 1st apr. of the year at 0 o'clock.
    2. the 1st apr. at 0 o'clock till the 1st jul. of the year at 0 o'clock.
    3. the 1st jul. at 0 o'clock till the 1st okt. of the year at 0 o'clock.
    4. the 1st okt. at 0 o'clock from the last year till the 1st jan. of the year at 0 o'clock.
    If the parameters are invalid :returns: None

    :param year: Year of the wanted time-span
    :param quarter: first, second, third or fourth quarter of the year
    :type year: int
    :type quarter: int

    **Example:**
    Date of the example: 2018-03-02
    print(date_picker(quarterTS(1990,1))
    '1990-01-01T00:00:00,1990-04-01T00:00:00'

    :returns: class timestamp

    """

    if control(year=year, quarter=quarter):
        return None

    time_span = {
        1: (1, 4),
        2: (4, 7),
        3: (7, 10),
        4: (10, 1)
    }

    timestamp_start = dt(
        year,
        time_span[quarter][0], 1)

    timestamp_end = dt(
        year if (quarter != 4) else year + 1,
        time_span[quarter][1], 1)

    return Timestamp(timestamp_start, timestamp_end, quarter=quarter)


def month_ts(year: int, month: int):
    """Returns the time span of the given month and year from

     the 1st at 0 o'clock till the 1st of the following month at 0 o'clock.

     :param year: Year of the wanted time-span
     :param month: month of the year
     :type year: int
     :type month: int

     **Example:**
     Date of the example: 2018-03-02
     print(date_pciker(monthTS(1990,12))
     '1990-11-01T00:00:00,1991-12-01T00:00:00'

     :returns: class timestamp

     """

    if control(year, month):
        return None

    timestamp_start = dt(year, month, 1)
    timestamp_end = timestamp_start + timedelta(monthrange(year, month)[1])

    return Timestamp(timestamp_start, timestamp_end)


def calender_week_ts(year: int, week: int):
    """Returns the time span of the given week and year from

    the Monday at 0 o'clock till the next Monday of the following week at 0 o'clock.

    :param year: Year of the wanted time-span
    :param week: week of the year
    :type year: int
    :type week: int

    **Example:**
    Date of the example: 2018-03-02
    date_picker.monthTS(1990,52)
    '1990-12-24T00:00:00,1990-12-31T00:00:00'

    :returns: class timestamp

    """

    if control(year=year, week=week):
        return None

    d = dt(year, 1, 1)
    if d.weekday() <= 3:
        d = d - timedelta(d.weekday())
    else:
        d = d + timedelta(7 - d.weekday())
    dlt = timedelta(days=(week - 1) * 7)
    dates_cw = d + dlt, d + dlt + timedelta(days=7)

    timestamp_start = dates_cw[0]

    timestamp_end = dates_cw[1]

    return Timestamp(timestamp_start, timestamp_end)


def day_ts(start_year: int, start_month: int, start_day: int):
    """Returns the time span of the given day, month and year from

    0 o'clock till the following day at 0 o'clock.

    :param start_year: Start Year of the wanted time-span
    :param start_month: month of the year
    :param start_day: day of the month

    :type start_year: int
    :type start_month: int
    :type start_day: int

    **Example:**
    Date of the example: 2018-03-02
    print(date_picker.day_ts(2000,12,31))
    '2000-12-31T00:00:00,2001-01-01T00:00:00'

    :returns: class timestamp

    """

    if control(start_year, start_month, start_day):
        return None

    timestamp_start = dt(start_year, start_month, start_day)
    timestamp_end = timestamp_start + timedelta(1)

    return Timestamp(timestamp_start, timestamp_end)


def day_period_ts(
        start_year: int, start_month: int, start_day: int,
        end_year: int, end_month: int, end_day: int):
    """Returns the time span of the given start day, month and year from

    0 o'clock till the end day, month, year at 0 o'clock.

    :param start_year: Start Year of the wanted time-span
    :param start_month: month of the year
    :param start_day: day of the month

    :param end_year: End year of the wanted time-span
    :param end_month: month of the year
    :param end_day: day of the month

    :type start_year: int
    :type start_month: int
    :type start_day: int

    :type end_year: int
    :type end_month: int
    :type end_day: int

    **Example:**
    Date of the example: 2018-03-02
    print(date_picker.day_period_ts(2000,12,31,2001,1,15))
    '2000-12-31T00:00:00,2001-01-15T00:00:00'

    :returns: class timestamp

    """

    if (control(start_year, start_month, start_day)
            or control(end_year, end_month, end_day)):
        return None

    timestamp_start = dt(start_year, start_month, start_day)
    timestamp_end = dt(end_year, end_month, end_day)

    try:
        if timestamp_start > timestamp_end:
            raise Exception('Start date is behind end date')
    except Exception as fail:
        print(fail)
        return None

    return Timestamp(timestamp_start, timestamp_end)


def period_ts(
        start_year: int, start_month: int, start_day: int,
        start_hour: int, start_min: int,
        end_year: int, end_month: int, end_day: int,
        end_hour: int, end_min: int):
    """Returns the time span of the given start min, hour, day, month and year start and end time.

    :param start_year: Year of the wanted time-span
    :param start_month: month of the year
    :param start_day: day of the month
    :param start_hour: hour of the day
    :param start_min: min of the hour

    :param end_year: End year of the wanted time-span
    :param end_month: month of the year
    :param end_day: day of the month
    :param end_hour: hour of the day
    :param end_min: min of the hour

    :type start_year: int
    :type start_month: int
    :type start_day: int
    :type start_hour: int
    :type start_min: int

    :type end_year: int
    :type end_month: int
    :type end_day: int
    :type end_hour: int
    :type end_min: int

    **Example:**
    Date of the example: 2018-03-02
    print(date_picker.period_ts(2000,12,31,11,24,2001,1,15,10,45))
    '2000-12-31T11:24:00,2001-01-15T11:24:00'

    :returns: class timestamp

    """

    if (control(start_year, start_month, start_day, start_hour, start_min)
            or control(end_year, end_month, end_day, end_hour, end_min)):
        return None

    timestamp_start = dt(start_year, start_month, start_day, start_hour, start_min)
    timestamp_end = dt(end_year, end_month, end_day, start_hour, start_min)

    try:
        if timestamp_start > timestamp_end:
            raise Exception('Start date is behind end date')
    except Exception as fail:
        print(fail)
        return None

    return Timestamp(timestamp_start, timestamp_end)


def one_hour_before_ts(
        end_year: int, end_month: int, end_day: int,
        end_hour: int, end_min: int = 0):
    """Returns a start date one hour before the give dates.

    :param end_year: Year of the wanted time-span
    :param end_month: month of the year
    :param end_day: day of the month
    :param end_hour: hour of the day
    :param end_min: min of the hour

    :type end_year: int
    :type end_month: int
    :type end_day: int
    :type end_hour: int
    :type end_min: int

    **Example:**
    Date of the example: 2018-03-02
    print(date_picker.one_hour_before_ts(2000,12,31,11,24)
    '2000-12-31T10:24:00,2000-12-31T11:24:00'

    :returns: class timestamp

    """

    if control(end_year, end_month, end_day, end_hour, end_min):
        return None

    timestamp_end = dt(end_year, end_month, end_day, end_hour, end_min)
    timestamp_start = timestamp_end - timedelta(hours=1)

    return Timestamp(timestamp_start, timestamp_end)


def now_year() -> int:
    """Returns the actual year as int
    :return: the actual year
    :rtype: int
    """

    return dt.now().year


def now_month() -> int:
    """Returns the actual month as int
    :return: the actual month
    :rtype: int
    """

    return dt.now().month


def str_to_timestamp(start, end, sep=' '):
    """Returns a timestamp-class object

    :param start: ISO Format timestamp string with a separator between date and time or a datetime.datetime obj
    :param end: ISO Format timestamp string with a separator between date and time or a datetime.datetime obj
    :param sep: Separator between the date and time (Default "T" or space) or
                list with to separators [sep_start, sep_end]

    **Example:**
    Date of the example: 2018-03-02
    date_picker.str_to_timestamp('2000-12-31T10:24', '2000-12-31U11:24', ['T','U'])
    <...date_picker.timestamp object at 0x...>

    :returns: class timestamp


    """
    # separation of the separators
    if isinstance(sep, list):
        sep_start = sep[0]
        sep_end = sep[1]
    else:
        sep_start = sep_end = sep

    if isinstance(start, dt):
        # Check if given parameter is already a datetime object
        timestamp_start = start
    elif isinstance(start, int):
        # Convert int to Datetime object
        timestamp_start = int_to_datetime(start)
    else:
        # Convert String to Datetime object
        timestamp_start = str_to_datetime(start, sep=sep_start)

    if isinstance(end, dt):
        # Check if given parameter is already a datetime object
        timestamp_end = end
    elif isinstance(end, int):
        # Convert int to Datetime object
        timestamp_end = int_to_datetime(end)
    else:
        # Convert String to Datetime object
        timestamp_end = str_to_datetime(end, sep=sep_end)

    return Timestamp(timestamp_start, timestamp_end)


def int_to_datetime(date_int):
    """Converts a int into string into datetime object

    :param date_int: int with the order YYYYMMDD or YYYYMMDDHHMMSS
    :return: datetime object
    """
    date_str = str(date_int)
    if len(date_str) > 8:
        try:
            return str_to_datetime(date_str[0:8] + ' ' + date_str[8:])
        except:
            print('Int was not in the right order try YYYYMMDDHHMMSS')
    else:
        try:
            return str_to_datetime(date_str[0:8])
        except:
            print('Int was not in the right order try YYYYMMDD')


def str_to_datetime(date_string: str, sep: str = ' '):
    """Converts a string to a datetime.datetime object

    :param date_string: Date and/or time in string format
    :type date_string: str
    :param sep: The separator between
    :type sep: str

    **Example**
    Date of the Example: 2019-10-04
    date_picker.str_to_datetime('2019#10*04T12')
    datetime.datetime(2019, 10, 4, 12, 0)

    :return: datetime.datetime object with the given date and/or time in the string
    """

    def is_numeric(value: str) -> bool:
        """Returns True if the string is numeric else False

        :param value: String that have to be checked
        :type value: str

        :return: True if value is numeric else False
        :rtype: bool
        """
        try:
            float(value)
            return True
        except ValueError:
            return False

    def drop_char(string: str) -> str:
        """Returns a string without letters

        :param string: a string
        :type string: str

        :return: the string only with numeric content
        :rtype: str
        """
        tmp = ''
        for c in string:
            if is_numeric(c):
                tmp += c
        return tmp

    dati_form = {'time': {2: '%H', 4: '%H%M', 6: '%H%M%S'},
                 'date': {6: '%y%m%d', 8: '%Y%m%d'}}
    de_dati_form = {'time': {2: '%H', 4: '%H%M', 6: '%H%M%S'},
                 'date': {6: '%d%m%y', 8: '%d%m%Y'}}

    date_string = date_string.replace(sep, 'T')
    date_length = len(drop_char(date_string))

    if 'de' in date_string.lower():
        date_string = date_string.lower().replace('de', '').upper()
        sep = sep.upper()
        dati_form = de_dati_form

    try:
        if ('T' not in date_string) and (date_length > 8):
            print('There have to be a "T", a space or the selected separator:"', sep, '" between the day and the time')
            raise SyntaxError
    except SyntaxError as fail:
        print(fail)
        print('There are several formats supported, please use one of them.')
        print(dati_form)
        return None
    try:
        if 'T' in date_string:
            date, time = date_string.split('T')
            time = drop_char(time)
            time_format = dati_form['time'][len(time)]
        else:
            date = date_string
            time_format = ''
        date = drop_char(date)
        date_format = dati_form['date'][len(date)]
        datetime_format = date_format + time_format

        datetime_obj = dt.strptime(drop_char(date_string), datetime_format)

    except KeyError:
        # todo if date is out of range cut to the last day in the month: (january day:32) cut to 31th of january
        print("Check your timestamps. Here an Example: '2019-01/01T00'")
        return None
    return datetime_obj
