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
        self.range = dt.TimeSpan()
        # if parts of a date are missing this is the default date that is used to infer the values - ie "next tuesday" will use this date as the anchor
        self.implicit_anchor = dateTime.datetime.now()
        self.month_day_precidence = True

        self.start_expr = self.time_expression

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
    
    # DATE_EXPRESSION = YEAR | YEAR + MONTH | YEAR + MONTH + DAY | YEAR + DAY | MONTH + DAY | DAY
    def date_expression(self):
       
        mostSig = dt.PeriodType.YEAR
        # try and get as many of these matches as possible in order the highest you start with has to be followed by the next lowest
        rv = self.match('year', 'month', 'day')



        return rv
    
    # TIME_EXPRESSION = HOUR | HOUR + MINUTE | HOUR + MINUTE + SECOND | HOUR + SECOND | MINUTE + SECOND | SECOND
    def time_expression(self):
        rv = self.match()

        return rv
    
    # PERIOD_OFFSET_EXPRESSION = IMPLICIT_ANCHOR_OFFSET | (LEAD_MODIFIER)? + PERIOD + (TRAIL_MODIFIER)?
    def period_offset_expression(self):
        implicit_relative = ['yesterday', 'today', 'tomorrow']
        implicit_offset = ['next', 'last',]
        rv = self.match('period', 'lead_modifier')

        return rv
    
    # PERIOD = (NUMERIC_VALUE + KW_PERIOD_IDENTIFIER) *
    def period(self):
        rv = self.match('numeric_period_value')

        op = self.maybe_keyword(*dtConst.dt_perids.keys())

        return rv
    # NUMERIC_PERIOD_VALUE = (NUMERAL | FRACTION | DECIMAL)  + ((and | , | - | +)* + NUMERAL | FRACTION | DECIMAL)
    def numeric_period_value(self):
        rv = self.match('numeral', 'fraction', 'decimal')

   

    
    def numeral_num(self):
        chars = []
        chars.append(self.char('0-9'))

        while True:
            comma = self.maybe_char(',')
            char = self.maybe_char('0-9')
            if char is None:
                break

            chars.append(char)
        ordinal = self.maybe_keyword('st', 'nd', 'rd', 'th')

        rv = int(''.join(chars))
        return (rv, ordinal != None)
    
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
        year = self.maybe_match('numeral')

        decade = self.maybe_keyword(*(decade_str.keys()))

        if decade:
            if (year):
                year = year * 100 + decade_str[decade]
            year = decade_str[decade]

        if (m_bc_ad is None):
            m_bc_ad = self.maybe_keyword(*bc_ad)

        if (m_prefix or m_bc_ad):
            year = year * fn_bc_ad(m_bc_ad)
            return (year, "year")
        
        
        
        self.test_range(year, 999, 9999)
        
        






        rv = self.match('year')

        return rv
    
    # MONTH = month_str | month_num
    def month(self):
        months = dtConst.dt_months.keys()
        strMonth = self.maybe_keyword(*months)
        intMonth = None
        if strMonth:
            intMonth = dtConst.dt_months[strMonth]


    
    

    
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



