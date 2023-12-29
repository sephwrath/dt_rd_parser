import spacy, re
from spacy.matcher import Matcher
from spacy.tokenizer import Tokenizer
from spacy.tokens import Doc, Token, Span

import requests
from enum import Enum

from spacy import displacy
#from dateparser import parse
#from timexy import Timexy
import en_core_web_trf

date_tests = [
    # date time formats
    "January 5",
    "dec 25",
    "may 27th",
    "October 2006",
    "jan 3 2010",
    "March 14, 2004",
    "March 14th, 2004",
    "3 jan 2000",
    "17 april 85",
    "5/27/1979",
    "27/5/1979",
    "1979-05-27",
    "Friday",
    "5",
    "4:00",
    "17:00",
    "0800",
    "10:30",
    "10:30:15",
    "10:30:15.123",
    "10:30:15.123456",
    "9/4/2000",
    "9/4/2000 10:30",
    "9/4/2000 10:30:15",
    "9 Apr 2000",
    "9 Apr 2000 10:30",
    "9 April 2000 10:30:15",
    "9-4-2000",
    "9-4-2000 10:30pm",
    "9-4-2000 22:30:15pm",
    # year tests
    "1984",
    "spring of 1982", 
    "the third quarter of '63", 
    "the first part of the 19th century", 
    "the turn of the century", 
    "the close of the previous decade", 
    "four score and seven years ago", 
    "10,000BC",
    "the eighteenth century",
    "the twentyfirst century",
    "the twenty-first century",
    "the twenty first century",
    "(1957)",
    "47 BCE", 
    "2CE", 
    "1908AD", 
    "190 AD", 
    "at the start of 1950", 
    "the close of the 70's", 
    "the year 204", 
    "summer of '89", 
    "the fall of 2000", 
    "spring 1420", 
    "in the 70's", 
    "three months into 1987", 
    "the 19th century", 
    "latter half of last year", 
    "last year", 
    "ten years ago", 
    "a decade before today", 
    "one million years ago", 
    "a million years ago plus or minus 10,000 years", 
    "one million years in the past +/- 10000 years", 
    "between 5000 and 10000 years ago",
    "the year of our lord 2050",
    "circa 1080",
    # month tests
    "next quarter",
    "april next year",
    "march 1974",
    "march just gone",
    "end of last month",
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
    
]



if __name__ == "__main__" :
    docs = []
    for  text in date_tests:
        
        doc = nlp(text)
        for date in doc.ents:
            if date.label_ == "DATE" or date.label_ == "TIME":
                print(date)

