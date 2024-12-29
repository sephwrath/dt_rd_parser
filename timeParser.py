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
        self.implicit_grain = dt.PeriodType.SECOND
        self.month_day_precidence = 'month'
        self.northern_hemisphere = True

        self.start_expr = self.time_expression

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
        #self.offset = dt.TimePeriod()
        # keeps track of the number of dates that have been parsed - parsing a second date updates the end of the range
        self.date_count = 0
        self.range = dt.TimeSpan()
        self.part_mod = False
    
    def set_refrence_date(self, date: dateTime.datetime, grain:dt.PeriodType=dt.PeriodType.SECOND):
        self.implicit_grain = grain
        self.implicit_anchor = date

    def set_start_expr(self, start_expr):
        self.start_expr = start_expr

    def start(self):
        self.__reset()
        return self.start_expr()
    
    # TIME_EXPRESSION = EXPLICIT_RANGE | IMPLICIT_RANGE -> explicit is from xxx to yyy implicit is a single time value ie in the mid 2000's
    def time_expression(self):
        # test for times first then if we don't have an anchor point check for an offset an use the default date
        #rv = self.match('explicit_range', 'implicit_range')
        range_start = ['the', 'around', 'from', 'between', 'beginning', 'starting', 'begin', 'start', 'started', 'commencing', 'initialted']
        range_separator = ['and', 'to', 'through', 'thru', '-', 'ending', 'ended', 'end', ':', 'until']
        #implicit_now = ['ago', 'in history', 'from now', 'prior']
        #implicit_match = self.maybe_keyword(*implicit_now)

        self.maybe_keyword(*range_start)

        offset_start = self.maybe_match('period_offset_expression')
        rv_start = self.maybe_match('date_expression')

        # if we don't have a date use an implicit date
        if (rv_start is None):
            rv_start = self.range.from_datetime(self.implicit_anchor, self.implicit_grain)

        if (offset_start):
            self.modify_range_by_offset(offset_start[1], offset_start[0])
        
        range_kwd = self.maybe_keyword(*range_separator)

        if range_kwd is not None:
            offset_end = self.maybe_match('period_offset_expression')
            rv_end = self.match('date_expression')
            if (offset_end):
                self.modify_range_by_offset(offset_end[1], offset_end[0])

        if (self.part_mod == False):
            self.range.offset_period(self.range.grain, 1, 'end')

        return self.range

    
    # IMPLICIT_RANGE = (PERIOD_OFFSET_EXPRESSION)* + DATE_EXPRESSION + (PERIOD_OFFSET_EXPRESSION)* | (PERIOD_OFFSET_EXPRESSION)* + implicit_now 
    def implicit_range(self):
        implicit_now = ['ago', 'in history', 'from now', 'prior']
        start_offset = self.maybe_match('period_offset_expression')
        implicit_match = self.maybe_keyword(*implicit_now)

        if implicit_match is not None:
            rv = self.match('date_expression', 'period_offset_expression')
        else:
            end_offset = self.match('period_offset_expression')
            rv = self.match('date_expression')

        return rv
    
    # EXPLICIT_RANGE = range_start + IMPLICIT_RANGE + range_separator  + IMPLICIT_RANGE
    def explicit_range(self):
        pass



    # PERIOD_OFFSET_EXPRESSION = IMPLICIT_ANCHOR_OFFSET | (LEAD_MODIFIER)? + PERIOD + (TRAIL_MODIFIER)?
    # PART_MODIFIER = ("the")* + (start | end | middle | approx)
    # DIR_MODIFIER = (forward | backward | same)
    
    def period_offset_expression(self) -> tuple[bool, list[tuple[dt.PeriodDetail, float]]]:
        implicit_relative = ['yesterday', 'today', 'tomorrow']

        implicit_offset_forward = ['next', 'following', 'after']
        implicit_offset_backward = ['previous', 'last']
        implicit_offset_same = ['this', 'current', 'same']

        ignore = self.maybe_keyword('that', 'the')
        direction  = None

        part_mod = self.maybe_match('part_modifier')
        if (part_mod is not None):
            ignore = self.keyword(*part_join_words)


        lead_mod = self.maybe_keyword(*implicit_offset_forward)
        if lead_mod is not None:
            direction = 1
        else:
            lead_mod = self.maybe_keyword(*implicit_offset_backward)
            if lead_mod is not None:
                direction = -1
            else:
                lead_mod = self.maybe_keyword(*implicit_offset_same)
                if lead_mod is not None:
                    direction = 0

        prev_mod_part = ['leading up', 'old', 'previous', 'prior', 'ago', 'before','earlier', 'previously','foregoing','andtecedent', 'advance', 'preceding']
        next_mod_part = ['leading on', 'following', 'after', 'new', 'subsequent', 'succeeding', 'later', 'subsequent', 'after', 'ensuing', 'afterwards', 'thereafter']

        period = self.match('period')
        prev_kwd = self.maybe_keyword(*prev_mod_part)

        if prev_kwd is not None:
            direction = False
        else:
            next_kwd = self.maybe_keyword(*next_mod_part)
            if next_kwd is not None:
                direction = True

        if direction is None:
            raise ParseError(self.pos + 1, 'No period_offset_expression found.', self.text[self.pos])

        return (direction, period)
    
    def modify_range_by_offset(self, period : list[tuple[dt.PeriodDetail, float]], direction: int):
        ''' modify the range by the period'''
        if self.date_count == 0:
            if direction > 0:
                end_mod = 'both'
            else:
                end_mod = 'start'
        else:
            if direction < 0:
                end_mod = 'both'
            else:
                end_mod = 'end' 

        for period_part in period:
            periodType = dt.Period.get(period_part[0]).periodType
            self.range.offset_period(periodType, period_part[1]*direction, end_mod)
    
    # PERIOD = (PERIOD_PART) * | target_period (monday, june, summer etc)
    # possibly don't need target as that should be covered by the date expressions
    def period(self) -> list[tuple[dt.PeriodDetail, float]]:
        periodArr = []
        while(True):
            periodPt = self.maybe_match('period_part')
            if periodPt == None:
                break
            else:
                periodArr.append(periodPt)

        if len(periodArr) == 0:
            raise ParseError(self.pos + 1, 'No period found.', self.text[self.pos])

        return periodArr
    
    # PERIOD_PART = (NUMERAL | FRACTION | DECIMAL) (period)
    # we want to match a whole period - not just a number raise if we don't get both parts
    def period_part(self) -> tuple['dt.PeriodDetail', float]:
        numeric_val = self.maybe_match('numeral', 'fraction')
        if (numeric_val is None):
            numeric_val = 1

        op = self.keyword(*dt.Period.getPeriodTranslationKeys())
        if (not op or not numeric_val):
            raise ParseError(self.pos + 1, 'No period found.', self.text[self.pos])
        return (dt.Period.getPeriodFromKey(op), numeric_val)

    
    # DATE_EXPRESSION = (YEAR)? + (MONTH)? + (DAY)? + (HOUR)? + (MINUTE)? + (SECOND)? + (MILLISECOND)?
    # some or part of an time anchor point could be a whole date/time or
    # a date/time missing the first or last parts of the expression - missing the most significant part ie year will result in the year being
    # inferred later either using the other date or the implicit anchor date which can be set before parsing as a class parameter
    # missing the last lest significant parts will mean the range will be inferred ie 1970 will be inferred to be 1970-01-01 to 1970-12-31
    def date_expression(self):
        getPd = lambda pd : dt.Period.get(pd) if pd is not None and pd in dt.Period.periodDetails else None
        
        parsed_items = ['year', 'day_month', 'time']

        parse_length = len(parsed_items)

        part_mod = None
        while(len(parsed_items) > 0):
            if part_mod == None:
                part_mod = self.maybe_match('part_modifier')
            date_val = self.maybe_match(*parsed_items)
            if date_val == None:
                break
            elif date_val[0] == 'year':
                if self.date_count == 0:
                    # set the start and end dates to be the same then mod end date with the offset period
                    self.range.set_yrs(date_val[1], date_val[1])
                    pd = getPd(date_val[2])
                    if pd is not None and pd.periodName != 'year':
                        self.range.offset_period(pd.periodType, pd.multiplier, 'end')
                else:
                    self.range.set_edge_pt('end', dt.PeriodType.YEAR, date_val[1])
            elif date_val[0] == 'day_month':
                if date_val[1] != None:
                    month_val = date_val[1]
                    if self.date_count == 0:
                        self.range.set_mos(month_val[1][0])
                        if (month_val[1][1] > 1):
                            self.range.offset_period(dt.PeriodType.MONTH, month_val[1][1], 'end')
                    else:
                        self.range.set_edge_pt('end', dt.PeriodType.MONTH, month_val[1][0])
                        
                if date_val[2] != None:
                    day_val = date_val[2]
                    
                    if self.date_count == 0:
                        self.range.set_days(day_val[1])
                    else:
                        self.range.set_edge_pt('end', dt.PeriodType.DAY, day_val[1])

            elif date_val[0] == 'time':
                if self.date_count == 0:
                    self.range.merge(date_val[1])
                else:
                    self.range.merge(date_val[1], dt.EdgeType.END)
            else:
                break

            parsed_items.remove(date_val[0])

        # no dates were parsed
        if len(parsed_items) == parse_length:
            raise ParseError(self.pos + 1, 'No date_expression found.', self.text[self.pos])
        else:
            if (self.date_count == 0):
                self.range.infer(self.implicit_anchor)
            self.date_count += 1
        
        # check that there are no breaks between ranges
        if self.range.has_gaps():
            raise ParseError(self.pos + 1, 'Gaps in parsed datetime.', self.text[self.pos])
       
        # try and get as many of these matches as possible in order the highest you start with has to be followed by the next lowest
        # the first missing bit gives the range and the starting point is backfilled with the implicit anchor time
        # ie Jan will give the range of the month on jan in the implicit anchor time year
                
        
        self.apply_part_modifier(part_mod, 1)

        # next, last - could these be part of the period offsets - 

        return self.range
    
    def apply_part_modifier(self, part_mod : tuple[str, float]):
        # change the period based on the part modifier 
        if part_mod != None:
            self.part_mod = True
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
    
    def part_modifier(self) -> tuple[str, float]:
        start_mod = ['preliminary', 'start', 'initial', 'first part', 'beginning', 'opening', 'early', 'dawn', 'first']
        end_mod = ['final', 'end', 'closing', 'close', 'beginning', 'opening', 'early', 'dawn', 'latter', 'last part', 'last']
        middle_mod = ['middle', 'mid', 'centre', 'central', 'halfway', 'midway']
        approx_mod = ['around', 'circa', 'c.a.', 'ca', 'about', 'near', 'approximately', 'soon']

        # TODO - add fractional components ie first third of the year, closing quarter of the month
        ignore_start = self.maybe_keyword('at the', 'the')
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
        ignore_end = self.maybe_keyword('of', 'in')
        

    def date_separator(self):
        date_sep = ['/', '-', ',']
        self.maybe_keyword(*date_sep)
    
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

        self.date_separator()

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
            raise ParseError(self.pos + 1, 'No year found.', self.text[self.pos])
        
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
    
    def day_month(self):
        result = None
        # if the day has precidence match it first
        if self.month_day_precidence == 'month':
            order = ['month_then_day', 'day_then_month', 'month_only']
        else:
            order = ['day_then_month', 'month_then_day', 'month_only']
        result = self.match(*order)
        return result

    def month_then_day(self):
        monthRv = self.match('month')
        dayRv = self.match('day')
        return ('day_month', monthRv, dayRv)
    
    def day_then_month(self):
        dayRv = self.match('day')
        monthRv = self.match('month')
        return ('day_month', monthRv, dayRv)
    
    def month_only(self):
        monthRv = self.match('month')
        return ('day_month', monthRv, None)
    
    
    # MONTH = month_str | month_num | month_range
    def month(self):
        match_name = 'month'
        # returns a tuple of start month and the number of months in the range
        rv = None
        self.date_separator()
        
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

        self.date_separator()

        day_names = dtConst.dt_week_days.keys()
        dayName = self.maybe_keyword(*day_names)

        dayNum = self.match('ordinal', 'undecorated_numeral')
        self.test_range(dayNum, 1, 31)

        return (match_name,  dayNum)

    def time(self):
        match_name = 'time'
        ret_time = dt.TimeSpan()
        time_am_pm = ['am', 'pm', 'a.m.', 'p.m.', 'a.m', 'p.m']

        self.date_separator()

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
            raise ParseError(self.pos + 1, 'No time found.', self.text[self.pos])

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



