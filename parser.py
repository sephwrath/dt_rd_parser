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
        self.offset = dt.TimePeriod()
        # cdt is the current date time variable used to store the current date time when when a time anchor is being parsed
        self.cdt = None
        self.range = dt.TimeSpan()
        # if parts of a date are missing this is the default date that is used to infer the values - ie "next tuesday" will use this date as the anchor
        self.implicit_anchor = dateTime.datetime.now()
        self.month_day_precidence = True
        self.northern_hemisphere = True

        self.start_expr = self.time_expression

        month_range = {
            'spring' : (3, 3),
            'summer' : (6, 3),
            'autumn' : (9,3),
            'fall': (9, 3),
            'winter': (12, 3),
        }

        if (not self.northern_hemisphere):
            for key in month_range.keys():
                month_range[key] = ((month_range[key][0]+ 6) % 12, 3)

    def set_start_expr(self, start_expr):
        self.start_expr = start_expr

    def start(self):
        return self.start_expr()
    
    # TIME_EXPRESSION = EXPLICIT_RANGE | IMPLICIT_RANGE -> explicit is from xxx to yyy implicit is a single time value ie in the mid 2000's
    def time_expression(self):
        # test for times first then if we don't have an anchor point check for an offset an use the default date
        rv = self.match('explicit_range', 'implicit_range')
        
        return rv
    
    # IMPLICIT_RANGE = (PERIOD_OFFSET_EXPRESSION)* + TIME_ANCHOR_PT + (PERIOD_OFFSET_EXPRESSION)* | (PERIOD_OFFSET_EXPRESSION)* + implicit_now 
    def implicit_range(self):
        implicit_now = ['ago', 'in history', 'from now', 'prior']
        rv = self.match('time_anchor_pt', 'period_offset_expression')

        return rv
    
    # EXPLICIT_RANGE = range_start + IMPLICIT_RANGE + range_separator  + IMPLICIT_RANGE
    def explicit_range(self):
        range_start = ['from', 'between', 'beginning', 'starting', 'begin', 'start', 'started', 'commencing', 'initialted']
        range_separator = ['and', 'to', 'through', 'thru', '-', 'ending', 'ended', 'end', ':', 'until']

        rv = self.match('implicit_range')

    def period_part(self):
        prefix = ['first part of', 'last part of', 'middle of']

    
    # TIME_ANCHOR_PT = DATE_EXPRESSION | STD_DATE | STD_TIME
    def time_anchor_pt(self):
        rv = self.match('date_expression')

        return rv
    
    # DATE_EXPRESSION = (YEAR)? + (MONTH)? + (DAY)? + (HOUR)? + (MINUTE)? + (SECOND)? + (MILLISECOND)?
    def date_expression(self):
       
        mostSig = dt.PeriodType.YEAR
        date_sep = ['/', '-', ',']
        time_sep = [':']

        self.cdt = dt.DateTimeElements()

        for type  in cdt.getUnsetArray():
            cdt.set(self.maybe_match('year'), cdt.yr)
            self.maybe_keyword(*date_sep)



       
        # try and get as many of these matches as possible in order the highest you start with has to be followed by the next lowest
        # the first missing bit gives the range and the starting point is backfilled with the implicit anchor time
        # ie Jan will give the range of the month on jan in the implicit anchor time year
        rv = self.maybe_match('year', 'month', 'day')

        # next, last - could these be part of the period offsets - 

        return rv
    
    
    # PERIOD_OFFSET_EXPRESSION = IMPLICIT_ANCHOR_OFFSET | (LEAD_MODIFIER)? + PERIOD + (TRAIL_MODIFIER)?
    def period_offset_expression(self):
        implicit_relative = ['yesterday', 'today', 'tomorrow']
        implicit_offset = ['next', 'last',]
        rv = self.match('period', 'lead_modifier')

        return rv
    
    # PERIOD = (NUMERIC_VALUE + KW_PERIOD_IDENTIFIER) * | target_period (monday, june, summer etc)
    def period(self):
        rv = self.match('numeric_period_value')

        op = self.maybe_keyword(*dtConst.dt_perids.keys())

        return rv
    # NUMERIC_PERIOD_VALUE = (NUMERAL | FRACTION | DECIMAL)  + ((and | , | - | +)* + NUMERAL | FRACTION | DECIMAL)
    def numeric_period_value(self):
        rv = self.match('numeral', 'fraction', 'decimal')

    
    # YEAR = yr_prefix + NUMERAL ie year one
    # YEAR = NUMERAL + yr_prefix ie 500 BC
    # YEAR = ORDINAL + yr_ord ie 1st century
    # YEAR = NUMERAL + ('s' | 'es' | '\'s') ie 2000's & 70's
    def year(self):
        
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
            mult_val = dt.periodDetails[mult].multiplier
            # subtract 1 as 5th century is 400 - 500
            year = (year - 1) * mult_val
            if (m_bc_ad is None):
                m_bc_ad = self.maybe_keyword(*bc_ad)
            year = year * fn_bc_ad(m_bc_ad)
            # return range of years
            return (year, mult)
        
        decade_tick = self.maybe_keyword('\'')
        bracket = self.maybe_keyword('(', '[', '{')
        year = self.maybe_match('numeral')

        year_plurals = self.maybe_keyword('\'s', 'es', 's')

        # eighteen fifties or the nineties
        decade = self.maybe_keyword(*(decade_str.keys()))
        if decade and decade_tick is None:
            
            if decade:
                if (year):
                    year = year * 100 + decade_str[decade]
                else:
                    year = current_century + decade_str[decade]

                return (year, 'decade')
            
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
            return (year, "year")
        
        # numbers just appearing without any decoration can only be years if they are between 1000 and 9999
        self.test_range(year, 1000, 9999)

        if year_plurals:
            return (year, 'decade')
        
        return (year, 'year')
    
    
    # MONTH = month_str | month_num | month_range
    def month(self):
        # returns a tuple of start month and the number of months in the range
        rv = None
        
        months = dtConst.dt_months.keys()
        strPeriod = self.maybe_keyword(*self.month_range.keys())
        strSep = self.maybe_char('-', ',')
        strMonth = self.maybe_keyword(*months)
        if strPeriod is None:
            strSep = self.maybe_char('-', ',')
            strPeriod = self.maybe_keyword(*self.month_range.keys())

        if strMonth:
            rv = (dtConst.dt_months[strMonth], 1)
        elif strPeriod:
            rv = self.month_range[strPeriod]
        else:
            intMonth = self.match('numeral')
            self.test_range(intMonth, 1, 12)

            rv = (intMonth, 1)

        return rv
    

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



