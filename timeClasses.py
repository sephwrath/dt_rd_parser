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
    def __init__(self, periodType, base, multiplier, hasPart, min, max ):
        self.periodType = periodType
        self.base = base
        self.multiplier = multiplier
        self.next = next
        self.hasPart = hasPart
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
        

class TimeSpan:
    def __init__(self, yr=None, mo=None, dy=None, hr=None, mi=None, sd=None, ms=None):
        self.start = [None, None, None, None, None, None, None]
        self.grain = PeriodType.YEAR
        self.end =  [None, None, None, None, None, None, None]
        self.end_grain = PeriodType.YEAR

        # defines wether to exclude the last second or millisecond from the end limit when returning the end of a time span
        # so will return 2009/12/31 23:59:59.999999 instead of 2010/1/1 0:0:0.0
        # Todo add getters to access start and end to enforce this
        self.exclude_end_limit = True
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
                # break when we have an existing date value or when we are going above the grain parameter
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
    
    def merge(self, other):
        for (idx, per) in enumerate(other.start):
            if per is not None:
                self.start[idx] = per
        for (idx, per) in enumerate(other.end):
            if per is not None:
                self.end[idx] = per
        return self
    
    def has_gaps(self):
        last_null = True
        change_count = 0
        for  per in self.start:
            if not((per is None) == last_null):
                change_count += 1
                last_null = not last_null
            if change_count > 2:
                return True
        last_null = True
        change_count = 0
        for per in self.end:
            if not((per is None) == last_null):
                change_count += 1
                last_null = not last_null
            if change_count > 2:
                return True
        return False
    
    def is_none(self):
        for per in self.start:
            if per is not None:
                return False
        for per in self.end:
            if per is not None:
                return False
        return True
    
    def __str__(self):
        return self.__print_date('start') + " - " + self.__print_date('end')
    
    def __print_date(self, arr='start'):
        dateStr = ""
        dt_obj = self.to_datetime(arr)
        return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
    
    def __eq__(self, __value: object) -> bool:
        if self.grain != __value.grain:
            return False
        for (idx, per) in enumerate(self.start):
            if per != __value.start[idx]:
                return False
        for (idx, per) in enumerate(self.end):
            if per != __value.end[idx]:
                return False
        return True

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)
    
    def set_end(self, yr, mo, dy, hr, mi, sd):
        return self.set_edge('end', self.grain, yr, mo, dy, hr, mi, sd)

    def set_edge(self, edge='start', grain=PeriodType.SECOND, *args):
        dt_edge = self.start if edge == 'start' else self.end
        for (idx, per_val) in enumerate(args):
            if (grain.value < idx):
                break
            dt_edge[idx] = per_val if per_val is not None else None

        return self

    def to_datetime(self, edge='start'):
        
        dt_edge = self.start if edge == 'start' else self.end

        def raise_(ex):
            raise ex
        
        dt = datetime.datetime((dt_edge[0] if dt_edge[0] is not None else raise_(ValueError("Year cannot be None"))),
                               (dt_edge[1] if dt_edge[1] is not None else 1),
                               (dt_edge[2] if dt_edge[2] is not None else 1),
                               (dt_edge[3] if dt_edge[3] is not None else 0),
                               (dt_edge[4] if dt_edge[4] is not None else 0),
                               (dt_edge[5] if dt_edge[5] is not None else 0))
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

    def apply_timedelta(self,edge, delta, grain):
        dt = self.to_datetime(edge)
        dt += delta
        self.set_edge(edge, grain, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

    def exclude_end_limit(self):
        dt = self.to_datetime('end')
        dt -=  datetime.timedelta(seconds=1)
        self.set_edge('end', PeriodType.SECOND, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)


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
                self.apply_timedelta('end', delta, self.grain)
            if edge != 'end':
                self.apply_timedelta('start', delta, self.grain)

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
        if self.grain.value < period.value:
            self.grain = period
        self.start[period.value] = start
        if end is not None:
            self.end[period.value] = end
        else:
            self.end[period.value] = self.start[period.value]
            self.offset_period(period, 1, 'end', False)
        self.__zero_from_grain()

    def __zero_from_grain(self):
        for idx in range(self.grain.value+1, 6):
            minVal = 1 if idx <= 2 else 0
            self.start[idx] = minVal
            self.end[idx] = minVal

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