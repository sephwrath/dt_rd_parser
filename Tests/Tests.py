
from ..timeClasses import TimeSpan, PeriodType
import datetime


now = datetime.datetime.now()


date_tests = {
    # date time formats
    "January 5" : TimeSpan(None, 1, 5).infer(now),
    "dec 25" : TimeSpan(None, 12, 25).infer(now),
    "may 27th" : TimeSpan(None, 5, 27).infer(now),
    "October 2006" : TimeSpan(2006, 10),
    "jan 3 2010" : TimeSpan(2010, 1, 3),
    "March 14, 2004" : TimeSpan(2004, 3, 14),
    "March 14th, 2004" : TimeSpan(2004, 3, 14),
    "3 jan 2000" : TimeSpan(2000, 1, 3),
    "17 april 85" : TimeSpan(1985, 4, 17),
    "5/27/1979" : TimeSpan(1979, 5, 27),
    "27/5/1979" : TimeSpan(1979, 5, 27),
    "1979-05-27" : TimeSpan(1979, 5, 27),
    "Friday" : TimeSpan().infer(now).next_wd('friday'),
    "5" : None,
    "4:00" : TimeSpan(None, None, None, 4).infer(now),
    "17:00" : TimeSpan(None, None, None, 17).infer(now),
    "0800"  : TimeSpan(None, None, None, None, 8).infer(now),
    "10:30" : TimeSpan(None, None, None, 10, 30).infer(now),
    "10:30:15" : TimeSpan(None, None, None, 10, 30, 15).infer(now),
    "10:30:15.123" : TimeSpan(None, None, None, 10, 30, 15).infer(now), # currently just ignore the milliseconds
    "10:30:15.123456": TimeSpan(None, None, None, 10, 30, 15).infer(now),
    "9/4/2000" : TimeSpan(2000, 9, 4),
    "9/4/2000 10:30" : TimeSpan(2000, 9, 4, 10, 30),
    "9/4/2000 10:30:15" : TimeSpan(2000, 9, 4, 10, 30, 15),
    "9 Apr 2000" : TimeSpan(2000, 4, 9),
    "9 Apr 2000 10:30" : TimeSpan(2000, 4, 9, 10, 30),
    "9 April 2000 10:30:15" : TimeSpan(2000, 4, 9, 10, 30, 15),
    "9-4-2000" : TimeSpan(2000, 9, 4),
    "9-4-2000 10:30pm" : TimeSpan(2000, 9, 4, 22, 30),
    "9-4-2000 22:30:15pm" : TimeSpan(2000, 9, 4, 22, 30, 15),
    # year tests
    "1984" : TimeSpan(1984),
    "spring of 1982" : TimeSpan(1982, 3, 20).set_end(1982, 6, 20),
    "the third quarter of '63" : TimeSpan(1963, 7, 1).set_end(1963, 10, 1),
    "the first part of the 19th century" : TimeSpan(1800, 1, 1).set_end(1810, 1, 1),
    "the turn of the century" : TimeSpan(2000, 1, 1).set_end(2001, 1, 1),
    "the close of the previous decade" : TimeSpan(1910, 1, 1).set_end(1920, 1, 1),
    #"four score and seven years ago", 
    "10,000BC" : TimeSpan(-10000),
    "the eighteenth century" : TimeSpan(1800, 1, 1).set_end(1900, 1, 1),
    "the twentyfirst century" : TimeSpan(2000, 1, 1).set_end(2100, 1, 1),
    "the twenty-first century" : TimeSpan(2000, 1, 1).set_end(2100, 1, 1),
    "the twenty first century" : TimeSpan(2000, 1, 1).set_end(2100, 1, 1),
    "(1957)" : TimeSpan(1957),
    "47 BCE" : TimeSpan(-47), 
    "2CE" : TimeSpan(2), 
    "1908AD" : TimeSpan(1908), 
    "190 AD" : TimeSpan(190), 
    "at the start of 1950" : TimeSpan(1950, 1),
    "the close of the 70's" : TimeSpan(1978).set_end(1980),
    "the year 204" : TimeSpan(204), 
    "summer of '89" : TimeSpan(1989, 6, 21).set_end(1989, 9, 21),
    "the fall of 2000" : TimeSpan(2000, 9, 1).set_end(2000, 12, 1),
    "spring 1420" : TimeSpan(1420, 3, 20).set_end(1420, 6, 20),
    "in the 70's" : TimeSpan(1970).set_end(1980), 
    "three months into 1987" : TimeSpan(1987, 3),
    "the 19th century" : TimeSpan(1800).set_end(1900), 
    "latter half of last year" : TimeSpan(None, 7).infer(now).offset_period(PeriodType.YEAR, -1).offset_period(PeriodType.MONTH, 6, 'end'),
    "last year" : TimeSpan().infer(now, grain=PeriodType.YEAR).offset_period(PeriodType.YEAR, -1), 
    "ten years ago" : TimeSpan().infer(now, grain=PeriodType.YEAR).offset_period(PeriodType.YEAR, -10),
    "a decade before today" : TimeSpan().infer(now, grain=PeriodType.DAY).offset_period(PeriodType.YEAR, -10),
    "one million years ago" : TimeSpan().inger(now).offset_period(PeriodType.YEAR, -1000000), 
    "a million years ago plus or minus 10,000 years" : TimeSpan().inger(now).offset_period(PeriodType.YEAR, -1001000, 'start').offset_period(PeriodType.YEAR, -999000, 'end'),
    "one million years in the past +/- 10000 years": TimeSpan().inger(now).offset_period(PeriodType.YEAR, -1000000).offset_period(PeriodType.YEAR, -10000, 'start').offset_period(PeriodType.YEAR, 10000, 'end'), 
    "between 5000 and 10000 years ago": TimeSpan().inger(now).offset_period(PeriodType.YEAR, -10000, 'start').offset_period(PeriodType.YEAR, -5000, 'end'),
    "the year of our lord 2050" : TimeSpan(2050),
    "circa 1080" : TimeSpan(1080),
    # month tests
    "next quarter" : TimeSpan().infer(now, grain=PeriodType.MONTH).offset_period(PeriodType.MONTH, 3), # not correct
    "april next year" : TimeSpan(None, 4).infer(now).offset_period(PeriodType.YEAR, 1),
    "march 1974" : TimeSpan(1974, 3),
    "march just gone": TimeSpan(None, 3).infer(now), # not correct
    "end of last month" : TimeSpan(None, 3).infer(now),
    "last month",
    "first half of June",
    "the start of the second week in August",
    "between July and August next year",
    "mid June - mid October",
    "the middle of next month",
    "the middle of this month",
    "the week after christmas",
    "over the next two weeks",
    # week tests
    "monday next week",
    "next tues",
    "first monday next april",
    "sunday",
    "sunday two weeks from now",
    "after a fortnight",
    "later half of next week",
    "in five to ten business days",
    "next weekend",
    "this weekend",
    "after the 15th",
    "before the 7th of next month",
    "we ran on Monday",
    "we run on Monday",
    "we are running Monday",
    "we have a run on Monday",
    "we have run, on Monday",
    # time tests
    "midnight on the 9th of april",
    "5pm on the 9th of april",
    "two hours after noon"
    "thursday",
    "november",
    "friday 13:00",
    "mon 2:35",
    "4pm",
    "6 in the morning",
    "friday 1pm",
    "sat 7 in the evening",
    "yesterday",
    "today",
    "tomorrow",
    "this tuesday",
    "next month",
    "this morning",
    "last night",
    "this second",
    "yesterday at 4:00",
    "last friday at 20:00",
    "last week tuesday",
    "tomorrow at 6:45pm",
    "afternoon yesterday",
    "thursday last week",
    "3 years ago",
    "5 months before now",
    "7 hours ago",
    "7 days from now",
    "1 week hence",
    "in 3 hours",
    "1 year ago tomorrow",
    "3 months ago saturday at 5:00 pm",
    "7 hours before tomorrow at noon",
    "3rd wednesday in november",
    "3rd month next year",
    "3rd thursday this september",
    "4th day last week",
    
}



if __name__ == "__main__" :
    docs = []
    for  text in date_tests:
        
        doc = nlp(text)
        for date in doc.ents:
            if date.label_ == "DATE" or date.label_ == "TIME":
                print(date)

