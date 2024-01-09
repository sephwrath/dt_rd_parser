import datetime
import calendar
from enum import Enum
import constants as dtc

class PeriodType (Enum):
    YEAR = 0
    MONTH = 1
    DAY = 2
    HOUR = 3
    MINUTE = 4
    SECOND = 5
    MILLISECOND = 6

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
        if period == PeriodType.DAY :
            self.days += number
        elif period == PeriodType.MONTH :
            self.months += number
        elif period == PeriodType.YEAR :
            self.years += number
        elif period == PeriodType.HOUR :
            self.hours += number
        elif period == PeriodType.MINUTE :
            self.minutes += number
        elif period == PeriodType.SECOND :
            self.seconds += number
        elif period == PeriodType.MILLISECOND :
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
    def __init__(self, yr=None, mo=None, dy=None, hr=None, mi=None, sd=None, ms=None):
        self.start = [None, None, None, None, None, None, None]
        self.grain = None
        self.end =  [None, None, None, None, None, None, None]
        self.end_grain = None
        self.set_yrs(yr)
        self.set_mos(mo)
        self.set_days(dy)
        self.set_hours(hr)
        self.set_mins(mi)
        self.set_secs(sd)

    def infer(self, date : datetime.datetime, grain=None):
        """
        Fill in any missing date information that is missing with a date time reference
        only populate upto the first defined time period type

        Parameters:
            date (datetime.datetime): The date to infer the period values from.

        Returns:
            None
        """
        for (idx, per) in enumerate(self.start):
            if per is not None or (grain is not None and idx > grain) :
                # bread when we have an existing date value or when we are going above the grain parameter
                break
            else:
                if idx == PeriodType.YEAR:
                    self.set_yrs(date.year)
                elif idx == PeriodType.MONTH:
                    self.set_mos(date.month)
                elif idx == PeriodType.DAY:
                    self.set_days(date.day)
                elif idx == PeriodType.HOUR:
                    self.set_hours(date.hour)
                elif idx == PeriodType.MINUTE:
                    self.set_mins(date.minute)
                # no point inferning seconds or we have inferred the whole date
        return self
    
    def set_end(self, yr, mo, dy, hr, mi, sd):
        return self.set_edge('end', self.grain, yr, mo, dy, hr, mi, sd)

    def set_edge(self, edge='start', grain=PeriodType.SECOND, *args):
        dt_edge = self.start if edge == 'start' else self.end
        for (idx, per_val) in enumerate(args):
            if (grain <= idx):
                break
            dt_edge[idx] = per_val if per_val is not None else None

        return self

    def to_datetime(self, edge='start'):
        dt = datetime.datetime()
        dt_edge = self.start if edge == 'start' else self.end

        dt.year = (dt_edge[0] if dt_edge[0] is not None else 0)
        dt.month = (dt_edge[1] if dt_edge[1] is not None else 0)
        dt.day = (dt_edge[2] if dt_edge[2] is not None else 0)
        dt.hour = (dt_edge[3] if dt_edge[3] is not None else 0)
        dt.minute = (dt_edge[4] if dt_edge[4] is not None else 0)
        dt.second = (dt_edge[5] if dt_edge[5] is not None else 0)
        return dt
    
    def from_datetime(self, dt, grain=PeriodType.DAY):
        self.set_yrs(dt.year if grain >= PeriodType.YEAR else None)
        self.set_mos(dt.month if grain >= PeriodType.MONTH else None)
        self.set_days(dt.day if grain >= PeriodType.DAY else None)
        self.set_hours(dt.hour if grain >= PeriodType.HOUR else None)
        self.set_mins(dt.minute if grain >= PeriodType.MINUTE else None)
        self.set_secs(dt.second if grain >= PeriodType.SECOND else None)

    def offset_month(self, update_var, months):
        update_var[1] = update_var[1] - 1 + months
        update_var[0] = update_var[0] + update_var[1] // 12
        update_var[1] = update_var[1] % 12 + 1
        update_var[2] = min(update_var[2], calendar.monthrange(update_var[0],update_var[1])[1])

    def offset_period(self, period, offset, edge='both'):
        delta = None
        self.grain = period
        if (period == PeriodType.YEAR):
            if edge != 'start':
                self.end[0] += offset
            if edge != 'end':
                self.start[0] += offset
        elif (period == PeriodType.MONTH):
            if edge != 'start':
                self.offset_month(self.end, offset)
            if edge != 'end':
                self.offset_month(self.start, offset)
        if (period == PeriodType.DAY):
            delta = datetime.timedelta(days= offset)
        elif (period == PeriodType.HOUR):
            delta = datetime.timedelta(hours= offset)
        elif (period == PeriodType.MINUTE):
            delta = datetime.timedelta(minutes= offset)
        elif (period == PeriodType.SECOND):
            delta = datetime.timedelta(seconds= offset)
        if delta is not None:
            if edge != 'start':
                dt = self.to_datetime('end')
                dt.date += delta
                self.set_edge('end', self.grain, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

            if edge != 'end':
                dt = self.to_datetime('start')
                dt.date += delta
                self.set_edge('start', self.grain, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

        return self

    def next_wd(self, wd_str):
        if (wd_str in dtc.dt_week_days):
            curr_day = dtc.dt_week_days[wd_str]
            if (self.start[0] is not None and self.start[1] is not None and self.start[3] is not None):
                dt = self.to_datetime()
                next_day = dt.weekday()
                if (next_day <= curr_day):
                    next_day += (7 - curr_day)
                day_off = next_day - curr_day
                self.offset_period(PeriodType.DAY, day_off)
        return self
        

    def set_period(self, period, start, end):
        if start == None:
            return
        if self.grain < period:
            self.grain = period
        self.start[period] = start
        if end is not None:
            self.end[period] = end
        else:
            self.end[period] = self.start[period]
            self.offset_period(period, 1, 'end')
        self.__zero_from_grain()

    def __zero_from_grain(self):
        for idx in range(self.grain+1, 6):
            self.start[idx] = 0
            self.end[idx] = 0


    def set_yrs(self, yrS, yrE = None):
       self.set_period(PeriodType.YEAR, yrS, yrE)

    def set_mos(self, moS, moE = None):
        self.set_period(PeriodType.MONTH, moS, moE)

    def set_days(self, dayS, dayE = None):
        self.set_period(PeriodType.DAY, dayS, dayE)

    def set_hours(self, hrS, hrE = None):
        self.set_period(PeriodType.HOUR, hrS, hrE)

    def set_mins(self, minS, minE = None):
        self.set_period(PeriodType.MINUTE, minS, minE)

    def set_secs(self, secS, secE = None):
        self.set_period(PeriodType.SECOND, secS, secE)