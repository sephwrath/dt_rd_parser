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

#nlp = spacy.load("en_core_web_trf")

class DTToken:
    def __init__(self, token, type, value):
        self.type = token.pos_
        self.processFn = None
        self.ordinal = None
        self.period = None
        self.point = None

class dt_token_types (Enum):
    NUMBER  = 0 # a whole number or decimal
    ORDINAL = 1
    FRACTION = 2 # a fractional number like 1/2
    PERIOD_IDENTIFIER = 3 # hours, minutes, seconds, days, months, years etc
    OFFSET_IDENTIFIER = 4 # words that apply an offset or adjustment to time periods
    DATE = 5
    TIME = 6
    LINKING_IDENTIFIER = 7 # words that join two or more time periods ie between, to - 

tokenLookup = {
    "century": DTToken("century", dt_token_types.PERIOD_IDENTIFIER, None),
    "centuries": DTToken("centuries", dt_token_types.PERIOD_IDENTIFIER, None),
    "decade": DTToken("decade", dt_token_types.PERIOD_IDENTIFIER, None),
    "decades": DTToken("decades", dt_token_types.PERIOD_IDENTIFIER, None),
    "year": DTToken("year", dt_token_types.PERIOD_IDENTIFIER, None),
    "years": DTToken("years", dt_token_types.PERIOD_IDENTIFIER, None),
    "month": DTToken("month", dt_token_types.PERIOD_IDENTIFIER, None),
    "months": DTToken("months", dt_token_types.PERIOD_IDENTIFIER, None),
    "week": DTToken("week", dt_token_types.PERIOD_IDENTIFIER, None),
    "weeks": DTToken("weeks", dt_token_types.PERIOD_IDENTIFIER, None),
    "day": DTToken("day", dt_token_types.PERIOD_IDENTIFIER, None),
    "days": DTToken("days", dt_token_types.PERIOD_IDENTIFIER, None),
    "hour": DTToken("hour", dt_token_types.PERIOD_IDENTIFIER, None),
    "hours": DTToken("hours", dt_token_types.PERIOD_IDENTIFIER, None),
    "minute": DTToken("minute", dt_token_types.PERIOD_IDENTIFIER, None)
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
        
class DateTimeElements:
    def __init__(self):
        self.yr = None
        self.mo = None
        self.dy = None
        self.hr = None
        self.mi = None
        self.sd = None
        self.ms = None

class TimeSpan:
    def __init__(self):
        self.start = datetime.datetime()
        self.end = datetime.datetime()