import datetime
from enum import Enum

class PeriodType (Enum):
    YEAR = 3
    MONTH = 5
    DAY = 7
    HOUR = 8
    MINUTE = 9
    SECOND = 10
    MILLISECOND = 11

class PeriodDetail:
    def __init__(self, periodType, base, multiplier, partof, haspart, min, max ):
        self.periodType = periodType
        self.base = base
        self.multiplier = multiplier
        self.next = next
        self.min = min
        self.max = max

periodDetails = {
    "milleneum": PeriodDetail("milleneum", PeriodType.YEAR, 1000, "century", 1, 1000),
    "century": PeriodDetail("century", PeriodType.YEAR, 100, "decade", 1, 100),
    "decade": PeriodDetail("decade", PeriodType.YEAR, 10, "year", 1, 10),
    "year": PeriodDetail("year", PeriodType.YEAR, 1, "month", 1, 12),
    "quarter": PeriodDetail("quarter", PeriodType.MONTH, 3, "month", 1, 3),
    "season": PeriodDetail("season", PeriodType.MONTH, 3, "month", 1, 3),
    "month": PeriodDetail("month", PeriodType.MONTH, 1, "day", 1, 31),
    "fortnight": PeriodDetail("fortnight", PeriodType.DAY, 14, "day", 1, 14),
    "week": PeriodDetail("week", PeriodType.DAY, 7, "day", 1, 7),
    "day": PeriodDetail("day", PeriodType.DAY, 1, "hour", 1, 24),
    "morning": PeriodDetail("morning", PeriodType.HOUR, 1, "minute", 1, 60),
    "hour": PeriodDetail("hour", PeriodType.HOUR, 1, "minute", 1, 60),
    "minute": PeriodDetail("minute", PeriodType.MINUTE, 1, "second", 1, 60),
    "second": PeriodDetail("second", PeriodType.SECOND, 1, "millisecond", 1, 1000)
}



class TimePeriod:
    def __init__(self, years = None, months = None, days = None, hours = None, minutes = None, seconds = None, milliseconds = None):
        # save irregular time periods separately 
        self.years = years
        self.months = months
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.milliseconds = milliseconds

    def set_datetime(self, dt):
        self.years = dt.year
        self.months = dt.month
        self.days = dt.day
        self.hours = dt.hour
        self.minutes = dt.minute
        self.seconds = dt.second
        self.milliseconds = dt.microsecond
    
    def add(self, number, period: PeriodType):
        if period == PeriodType.DAYS :
            self.days += number
        elif period == PeriodType.MONTHS :
            self.months += number
        elif period == PeriodType.YEARS :
            self.years += number
        elif period == PeriodType.HOURS :
            self.hours += number
        elif period == PeriodType.MINUTES :
            self.minutes += number
        elif period == PeriodType.SECONDS :
            self.seconds += number
        elif period == PeriodType.MILLISECONDS :
            self.milliseconds += number
        


class TimeSpan:
    def __init__(self):
        self.start = datetime.datetime()
        self.end = datetime.datetime()