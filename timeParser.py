import math
from parserBase import ParserBase
from numberParser import NumberParser
from parseError import ParseError
import timeClasses as dt
import datetime as dateTime
import constants as dtConst

# part of the theory behind this parser is that you are always specifiying a range when describing a date or time for example "29th July 2001" isn't a point in time
# it's the range of values from the start of the day to the end of the day and even if you specified it down to seconds you are specifying from the start of the second to the end
class TimeParser(NumberParser):
    def __init__(self):
        super().__init__()
        # if parts of a date are missing this is the default date that is used to infer the values - ie "next tuesday" will use this date as the anchor
        self.implicit_anchor = dateTime.datetime.now()
        self.month_day_precidence = 'month'
        self.northern_hemisphere = True

        self.start_expr = self.date_expression

        self.month_range = {
            'spring' : (3, 3),
            'summer' : (6, 3),
            'autumn' : (9,3),
            'fall': (9, 3),
            'winter': (12, 3),
        }

        if (not self.northern_hemisphere):
            for key in self.month_range.keys():
                self.month_range[key] = ((self.month_range[key][0]+ 6) % 12, 3)

    def __reset(self):
        self.offset = dt.TimePeriod()
        self.range = dt.TimeSpan()

    def set_start_expr(self, start_expr):
        self.start_expr = start_expr

    def start(self):
        self.__reset()
        return self.start_expr()
    
    # TIME_EXPRESSION = EXPLICIT_RANGE | IMPLICIT_RANGE -> explicit is from xxx to yyy implicit is a single time value ie in the mid 2000's
    def time_expression(self):
        # test for times first then if we don't have an anchor point check for an offset an use the default date
        rv = self.match('explicit_range', 'implicit_range')
        
        return rv
    
    # IMPLICIT_RANGE = (PERIOD_OFFSET_EXPRESSION)* + DATE_EXPRESSION + (PERIOD_OFFSET_EXPRESSION)* | (PERIOD_OFFSET_EXPRESSION)* + implicit_now 
    def implicit_range(self):
        implicit_now = ['ago', 'in history', 'from now', 'prior']
        start_offset = self.maybe_match('period_offset_expression')
        implicit_match = self.maybe_match(*implicit_now)

        if implicit_match is not None:
            rv = self.match('date_expression', 'period_offset_expression')
        else:
            end_offset = self.match('period_offset_expression')
            rv = self.match('date_expression', 'period_offset_expression')

        return rv
    
    # EXPLICIT_RANGE = range_start + IMPLICIT_RANGE + range_separator  + IMPLICIT_RANGE
    def explicit_range(self):
        range_start = ['the', 'around', 'from', 'between', 'beginning', 'starting', 'begin', 'start', 'started', 'commencing', 'initialted']
        range_separator = ['and', 'to', 'through', 'thru', '-', 'ending', 'ended', 'end', ':', 'until']

        self.maybe_match(*range_start)
        rv_start = self.match('date_expression')
        self.match(*range_separator)
        rv_end = self.match('date_expression')

    def period_modifier(self):
        prefix = ['first part of', 'last part of', 'middle of', 'start of']

    # PERIOD_OFFSET_EXPRESSION = IMPLICIT_ANCHOR_OFFSET | (LEAD_MODIFIER)? + PERIOD + (TRAIL_MODIFIER)?
    def period_offset_expression(self):
        implicit_relative = ['yesterday', 'today', 'tomorrow']
        implicit_offset = ['next', 'last']
        rv = self.match('period', 'lead_modifier')

        return rv
    
    # PERIOD = (PERIOD_PART) * | target_period (monday, june, summer etc)
    # possibly don't need target as that should be covered by the date expressions
    def period(self) -> list[tuple[str, float]]:
        periodArr = []
        while(True):
            periodPt = self.maybe_match('period_part')
            if periodPt == None:
                break
            else:
                periodArr.append(periodPt)

        if len(periodArr) == 0:
            raise ParseError(self.pos, 'No period found.', self.text[self.pos])

        return periodArr
    
    # PERIOD_PART = (NUMERAL | FRACTION | DECIMAL) (period)
    # we want to match a whole period - not just a number raise if we don't get both parts
    def period_part(self) -> tuple[str, float]:
        numeric_val = self.match('numeral', 'fraction', 'decimal')
        op = self.keyword(*dt.Period.getPeriodTranslationKeys())
        if (not op or not numeric_val):
            raise ParseError(self.pos, 'No period found.', self.text[self.pos])
        return (dt.Period.getPeriodFromKey(op), numeric_val)

    
    # DATE_EXPRESSION = (YEAR)? + (MONTH)? + (DAY)? + (HOUR)? + (MINUTE)? + (SECOND)? + (MILLISECOND)?
    # some or part of an time anchor point could be a whole date/time or
    # a date/time missing the first or last parts of the expression - missing the most significant part ie year will result in the year being
    # inferred later either using the other date or the implicit anchor date which can be set before parsing as a class parameter
    # missing the last lest significant parts will mean the range will be inferred ie 1970 will be inferred to be 1970-01-01 to 1970-12-31
    def date_expression(self):
        getPd = lambda pd : dt.Period.get(pd) if pd is not None and pd in dt.Period.periodDetails else None
        date_sep = ['/', '-', ',']
        if self.month_day_precidence == 'month':
            parsed_items = ['year', 'month', 'day', 'time']
        else:
            parsed_items = ['year', 'day', 'month', 'time']

        part_mod = None
        while(len(parsed_items) > 0):
            if part_mod == None:
                part_mod = self.maybe_match('part_modifier')
            date_val = self.maybe_match(*parsed_items)
            if date_val == None:
                break
            elif date_val[0] == 'year':
                # set the start and end dates to be the same then mod end date with the offset period
                self.range.set_yrs(date_val[1], date_val[1])
                pd = getPd(date_val[2])
                if pd is not None and pd.periodName != 'year':
                    self.range.offset_period(pd.periodType, pd.multiplier, 'end')
            elif date_val[0] == 'month':
                self.range.set_mos(date_val[1][0])
                if (date_val[1][1] > 1):
                    self.range.offset_period(dt.PeriodType.MONTH, date_val[1][1], 'end')
            elif date_val[0] == 'day':
                self.range.set_days(date_val[1])
            elif date_val[0].value == 'time':
                self.range.merge(date_val[1])
            else:
                break

            self.maybe_keyword(*date_sep)

            # TODO -  test if day and month need to swap
            parsed_items.remove(date_val[0])
        
        # check that there are no breaks between ranges
        if self.range.has_gaps():
            self.range = dt.TimeSpan()
       
        # try and get as many of these matches as possible in order the highest you start with has to be followed by the next lowest
        # the first missing bit gives the range and the starting point is backfilled with the implicit anchor time
        # ie Jan will give the range of the month on jan in the implicit anchor time year
                
        # change the period based on the part modifier 
        if part_mod != None:

            part = dt.Period.get(self.range.grain.name.lower())
            partType = dt.Period.get(part.hasPart).periodType
            part_portion = math.floor(part_mod[1] * part.max)
            part_portion = 1 if part_portion < 1 else part_portion
            if part_mod[0] == 'start':
                self.range.offset_period(partType, part_portion, 'end')
            elif part_mod[0] == 'end':
                self.range.offset_period(self.range.grain, 1, 'both')
                self.range.offset_period(partType, -part_portion, 'start')
            elif part_mod[0] == 'middle':
                part_portion = math.floor(part_portion/2)
                part_portion = 1 if part_portion < 1 else part_portion
                self.range.offset_period(self.range.grain, 1, 'end')
                self.range.offset_period(partType, -part_portion, 'end')
                self.range.offset_period(partType, part_portion, 'start')
            elif part_mod[0] == 'approx':
                self.range.offset_period(self.range.grain, 1, 'end')
                self.range.offset_period(partType, part_portion, 'end')
                self.range.offset_period(partType, -part_portion, 'start')
        elif (self.range.is_point()):
            self.range.offset_period(self.range.grain, 1, 'end')

        # next, last - could these be part of the period offsets - 

        return self.range
    
    def part_modifier(self) -> tuple[str, float]:
        start_mod = ['preliminary', 'start', 'initial', 'first part', 'beginning', 'opening', 'early', 'dawn', 'first']
        end_mod = ['final', 'end', 'closing', 'close', 'beginning', 'opening', 'early', 'dawn', 'latter', 'last part', 'last']
        middle_mod = ['middle', 'mid', 'centre', 'central', 'halfway', 'midway']
        approx_mod = ['around', 'circa', 'c.a.', 'ca', 'about', 'near', 'approximately', 'soon']

        # TODO - add fractional components ie first third of the year, closing quarter of the month
        start_kw = self.maybe_keyword(*start_mod)
        if (start_kw):
            return ('start', 0.25)
        end_kw = self.maybe_keyword(*end_mod)
        if (end_kw):
            return ('end', 0.25)
        middle_kw = self.maybe_keyword(*middle_mod)
        if (middle_kw):
            return ('middle', 0.25)
        approx_kw = self.maybe_keyword(*approx_mod)
        if (approx_kw):
            return ('approx', 0.25)
        


    
    # YEAR = yr_prefix + NUMERAL ie year one
    # YEAR = NUMERAL + yr_prefix ie 500 BC
    # YEAR = ORDINAL + yr_ord ie 1st century
    # YEAR = NUMERAL + ('s' | 'es' | '\'s') ie 2000's & 70's
    def year(self):
        match_name = 'year'
        
        yr_prefix = ['year', 'yr']
        bc_ad = ['b.c.e.','b.c.e', 'bce', 'bc', 'b.c.', 'b.c', 'ad', 'a.d.', 'a.d', 'c.e.', 'c.e', 'ce']
        yr_ord = ['century', 'millenium', 'decade']
        decade_str = {
            "twenties": 20,
            "thirties": 30,
            "forties": 40,
            "fourties": 40,
            "fifties": 50,
            "sixties": 60,
            "seventies": 70,
            "eighties": 80,
            "nineties": 90,
        }
        current_century = self.implicit_anchor.year - (self.implicit_anchor.year % 100)

        fn_bc_ad = lambda x: -1 if x and x[0] == 'b' else 1

        m_prefix = self.maybe_keyword(*yr_prefix)
        m_bc_ad = self.maybe_keyword(*bc_ad)

        year = self.maybe_match('ordinal')
        if year:
            mult = self.keyword(*yr_ord)
            mult_val = dt.Period.get(mult).multiplier
            # subtract 1 as 5th century is 400 - 500
            year = (year - 1) * mult_val
            if (m_bc_ad is None):
                m_bc_ad = self.maybe_keyword(*bc_ad)
            year = year * fn_bc_ad(m_bc_ad)
            # return range of years
            return (match_name, year, mult)
        
        decade_tick = self.maybe_keyword('\'')
        bracket = self.maybe_keyword('(', '[', '{')
        year = self.maybe_match('undecorated_numeral')

        year_plurals = self.maybe_keyword('\'s', 'es', 's')

        # eighteen fifties or the nineties
        decade = self.maybe_keyword(*(decade_str.keys()))
        if decade and decade_tick is None:
            
            if decade:
                if (year):
                    year = year * 100 + decade_str[decade]
                else:
                    year = current_century + decade_str[decade]

                return (match_name, year, 'decade')
            
        if bracket:
            bracket = self.keyword(')', ']', '}')

        if year is None:
            raise ParseError(self.pos, 'No year found.', self.text[self.pos])
        
        if decade_tick:
            # '80's, '90s, '72
            year = current_century + year

        if (m_bc_ad is None):
            m_bc_ad = self.maybe_keyword(*bc_ad)

        if (m_prefix or m_bc_ad):
            year = year * fn_bc_ad(m_bc_ad)
            return (match_name, year, "year")
        
        # numbers just appearing without any decoration can only be years if they are between 1000 and 9999
        self.test_range(year, 1000, 9999)

        if year_plurals:
            return (match_name, year, 'decade')
        
        return (match_name, year, 'year')
    
    
    # MONTH = month_str | month_num | month_range
    def month(self):
        match_name = 'month'
        # returns a tuple of start month and the number of months in the range
        rv = None
        
        months = dtConst.dt_months.keys()
        strPeriod = self.maybe_keyword(*self.month_range.keys())
        strSep = self.maybe_keyword('-', ',')
        strMonth = self.maybe_keyword(*months)
        if strPeriod is None:
            strSep = self.maybe_keyword('-', ',')
            strPeriod = self.maybe_keyword(*self.month_range.keys())

        if strMonth:
            rv = (dtConst.dt_months[strMonth], 1)
        elif strPeriod:
            rv = self.month_range[strPeriod]
        else:
            intMonth = self.match('undecorated_numeral')
            self.test_range(intMonth, 1, 12)

            rv = (intMonth, 1)

        return (match_name, rv)
    
    def day(self):
        match_name = 'day'
        day_names = dtConst.dt_week_days.keys()
        dayName = self.maybe_keyword(*day_names)

        dayNum = self.match('ordinal', 'undecorated_numeral')
        self.test_range(dayNum, 1, 31)
        return (match_name,  dayNum)

    def time(self):
        match_name = 'time'
        ret_time = dt.TimeSpan()
        time_am_pm = ['am', 'pm', 'a.m.', 'p.m.', 'a.m', 'p.m']

        time_words = self.maybe_keyword(*dtConst.times_of_day.keys())
        
        time_sep = [':', '.']
        hour = self.maybe_match('undecorated_numeral')
        if (hour):
            self.maybe_keyword(*time_sep)
        
        minute = self.maybe_match('undecorated_numeral')
        if (minute):
            self.test_range(minute, 0, 59)
            self.keyword(*time_sep)
            ret_time.set_mins(minute)

        second = self.maybe_match('undecorated_numeral')
        if (second):
            self.test_range(second, 1, 59)
            self.keyword(*time_sep)
            ret_time.set_secs(second)

        am_pm = self.maybe_keyword(*time_am_pm)

        if (time_words is None):
            eat_sep = ['in the', 'at']
            self.maybe_keyword(*eat_sep)
            time_words = self.maybe_keyword(*dtConst.times_of_day.keys())


        if (hour):
            # 24hr time is sometimes stated without separattors 2400 hrs ets
            if (am_pm):
                self.test_range(hour, 1, 23)
                if (am_pm.startswith('p') and hour < 12):
                    hour = hour + 12
            else:
                if hour > 24:
                    mil_time = self.keyword(*["hr", "hrs", "hour", "hours"])
                    if mil_time:
                        hour = math.floor(hour / 100)
                        mins = hour % 100
                        ret_time.set_mins(mins)

                else:
                    self.test_range(hour, 0, 23)

            ret_time.set_hours(hour)

        elif (time_words):
            tod = dtConst.times_of_day[time_words]
            ret_time.set_hours(tod[0], tod[2])
            ret_time.set_mins(tod[1], tod[3])

        if (ret_time.is_none()):
            raise ParseError(self.pos, 'No time found.', self.text[self.pos])

        return (match_name, ret_time) 

if __name__ == '__main__':
    parser = TimeParser()

    while True:
        try:
            print(parser.parse(input('> ')))
        except KeyboardInterrupt:
            print()
        except (EOFError, SystemExit):
            print()
            break
        except (ParseError, ZeroDivisionError) as e:
            print('Error: %s' % e)



