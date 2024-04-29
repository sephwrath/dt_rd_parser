from parserBase import ParserBase
from parseError import ParseError
import constants as dtConst

class NumberParser(ParserBase):
    def __init__(self):
        super().__init__()
        self.start_expr = self.ordinal

        self.single_num_keys = dtConst.SINGLE_NUMS.keys()
        self.ten_pref_keys = dtConst.TEN_PREFIXES.keys()
        self.big_prefix_keys = dtConst.BIG_PREFIXES.keys()
        self.direct_num_keys = dtConst.DIRECT_NUMS.keys()

        self.single_ordinal_keys = dtConst.ORDINAL_SINGLE.keys()
        self.all_ordinal_keys = dtConst.ALL_ORDINALS.keys()

        self.all_fraction_keys = dtConst.ALL_FRACTIONS.keys()

    def set_start_expr(self, start_expr):
        self.start_expr = start_expr

    def start(self):
        return self.start_expr()
    
    
    def any_number(self):
        rv = self.match('ordinal', 'fraction', 'decimal', 'numeral')

    # NUMBER_KEYS = (and | , | - | +)
    
    

    # FRACTION = FRACTION_TEXT | FRACTION_NUM
    # FRACTION_TEXT = all_fractions -> quarter -> 1/4 a tenth, two tenths, 2/4
    def fraction(self):
        numerator = self.maybe_match('numeral')
        if(numerator is None):
            self.keyword('a')
            numerator = 1
        
        divisor = self.maybe_keyword('/', 'over', 'by', 'divided by') 

        denominator = self.maybe_match('numeral')
        fractional = self.keyword(*self.all_fraction_keys)
        if (fractional):
            fraction = dtConst.ALL_FRACTIONS[fractional]
            if (denominator):
                denominator += int(fraction)
            else:
                denominator = int(fraction)

        if (numerator and denominator):
            self.test_range(denominator, 1)
            return numerator / denominator
        else:
            raise ParseError(
                        self.pos,
                        'Unable to parse fraction. Numerator: {}, Denominator: {}'.format(numerator, denominator),
                        self.text[self.pos]
                    )
        
            
        
    # ORDINAL = ORDINAL_TEXT | ORDINAL_NUM
    # ORDINAL_TEXT = all_ordinals -> second -> 2
    def ordinal(self):
        number = self.maybe_match('numeral')
        
        if (number):
            rv = self.maybe_keyword('st', 'nd', 'rd', 'th')
            if (rv):
                return number
            else:
                eat_and = self.maybe_keyword('and')
        
        ordinal = self.keyword(*self.all_ordinal_keys)
        if (ordinal):
            ord_val = dtConst.ALL_ORDINALS[ordinal]
            if (number):
                return number + int(ord_val)
            else:
                return ord_val

    def test_range(self, number, low=None, high=None):
        if low and high:
            if number < low or number > high:
                raise ParseError(
                        self.pos,
                        'Parsed value {} is outside of expected range of low {} and high {}.'.format(number, low, high),
                        self.text[self.pos]
                    )
        elif low:
            if number < low:
                raise ParseError(
                        self.pos,
                        'Parsed value {} is less than expected minimum of {}.'.format(number, low),
                        self.text[self.pos]
                    )
        elif high:
            if number > high:
                raise ParseError(
                        self.pos,
                        'Parsed value {} is greater than expected maximum of {}.'.format(number, high),
                        self.text[self.pos]
                    )

    # NUMERAL = (NUMERAL_TXT | NUMERAL_NUM | BIG_PREFIX_TEXT) + ((NUMBER_KEYS)* + (NUMERAL_TXT | NUMERAL_NUM | BIG_PREFIX_TEXT))*
    def __numeral(self, no_decoration=False):
        if no_decoration:
            numeral_num = "numeral_num_nd"
            numeral_text = "numeral_text_nd"
        else:
            numeral_num = "numeral_num"
            numeral_text = "numeral_text"

        
        total = 0
        start_a = self.maybe_keyword('a')
        if (start_a):
            prefix = self.maybe_match('big_prefix_text')
            if (prefix):
                total += prefix
        else :
            total = self.match(numeral_text, numeral_num)
            prefix = self.maybe_match('big_prefix_text')
            if (prefix):
                total = prefix * total

        while(True):
            kw = self.maybe_keyword('and')
            
            subsequent_tot = 0
            prefix = self.maybe_match('big_prefix_text')
            if (prefix):
                subsequent_tot += prefix
            else :
                subsequent_tot = self.maybe_match(numeral_text, numeral_num)
                if (subsequent_tot is None):
                    break
                prefix = self.maybe_match('big_prefix_text')
                if (prefix):
                    subsequent_tot = prefix * subsequent_tot
                
            total += subsequent_tot
        return total
    
    def numeral(self):
        return self.__numeral(False)
    
    def undecorated_numeral(self):
         return self.__numeral(True)
    
    
    # BIG_PREFIX_TEXT = big_prefixes -> billion -> 1,000,000,000
    def big_prefix_text(self):
        rv = self.keyword(*self.big_prefix_keys)
        if (rv):
            return dtConst.BIG_PREFIXES[rv]
    
    # NUMERAL_TXT = single_nums + (-)* + ten_prefs -> one twenty -> 120
    # NUMERAL_TXT = dir_single_nums -> one -> 1
    # NUMERAL_TXT = ten_prefs + (-)* + single_nums -> tewenty one -> 21
    # NUMERAL_TXT = ten_prefs -> twenty -> 20
    
    def numeral_text(self):
        return self.__numeral_text(True)
    def numeral_text_nd(self):
        return self.__numeral_text(False)
    def __numeral_text(self, decoration=True):

        # match the longer possible keywords first
        rv = self.maybe_keyword(*self.ten_pref_keys)
        if (rv):
            if decoration:
                self.maybe_char('-')
            ten_num = dtConst.TEN_PREFIXES[rv]
            rv = self.maybe_keyword(*self.single_num_keys)
            if (rv):
                single_num =  dtConst.SINGLE_NUMS[rv]
                return int(ten_num) + int(single_num)
            else:
                return int(ten_num)
        
        rv = self.keyword(*self.single_num_keys)
        if (rv):
            if decoration:
                self.maybe_char('-')
            single_num = dtConst.SINGLE_NUMS[rv]
            
            rv = self.maybe_keyword(*self.ten_pref_keys)
            if (rv):
                ten_num = dtConst.TEN_PREFIXES[rv]
                return int("{}{}".format(single_num, ten_num))
            else:
                return single_num
        
        dir_nums = dtConst.DIRECT_NUMS.keys()
        rv = self.maybe_keyword(*dir_nums)
        if (rv):
            return dtConst.DIRECT_NUMS[rv]
        
        
    def numeral_num(self):
        return self.__numeral_num(True)

    def numeral_num_nd(self):
        return self.__numeral_num(False)
    
    def __numeral_num(self, decoration=True):
        chars = []
        chars.append(self.char('0-9'))

        while True:
            if decoration:
                comma = self.maybe_char(',')
            char = self.maybe_char('0-9')
            if char is None:
                break

            chars.append(char)

        rv = int(''.join(chars))
        return rv
    

if __name__ == '__main__':
    parser = NumberParser()

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



