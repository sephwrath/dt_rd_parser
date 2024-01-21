special_days = {
    'christmas': (24, 12),
    'christmas': (25, 12),
    'boxing day': (26, 12),
    'summer solstace': (21, 6),
    'winter solstace': (22, 12)
}

dt_months = {
    'jan': 1,
    'january': 1,
    'feb': 2,
    'february': 2,
    'mar': 3,
    'march': 3,
    'apr': 4,
    'april': 4,
    'may': 5,
    'jun': 6,
    'june': 6,
    'jul': 7,
    'july': 7,
    'aug': 8,
    'august': 8,
    'sep': 9,
    'sept': 9,
    'september': 9,
    'oct': 10,
    'october': 10,
    'nov': 11,
    'november': 11,
    'dec': 12,
    'december': 12
}

dt_week_days = {
    'mon': 0,
    'monday': 0,
    'tue': 1,
    'tuesday': 1,
    'wed': 2,
    'wednesday': 2,
    'thu': 3,
    'thursday': 3,
    'fri': 4,
    'friday': 4,
    'sat': 5,
    'saturday': 5,
    'sun': 6,
    'sunday': 6
}

dt_month_days = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31
}


times_of_day = {
    'morning': (0, 0, 12, 0),
    'afternoon': (12 ,0, 18, 0),
    'evening': (18,0, 0, 0),
    'night': (19, 0, 6, 0),
    'dawn': (6, 0, 8, 0),
    'dusk': (17, 0, 19, 0),
    'midday': (11, 30, 12, 30),
    'midnight': (23, 30, 0, 30),
    'day': (6, 0, 18, 0),
    'noon': (12, 0, 12, 0)
}

start_skip = ['before', 'from', 'starting', 'beginning', 'began', 'between']
skip_words = ['at', 'the']

prev_mod = ['last', 'yesterday']
next_mod = ['next', 'tomorrow']
prev_mod_part = ['leading up', 'old', 'previous', 'prior', 'ago', 'before','earlier', 'previously','foregoing','andtecedent', 'advance', 'preceding']
next_mod_part = ['leading on', 'following', 'after', 'new', 'subsequent', 'succeeding', 'later', 'subsequent', 'after', 'ensuing', 'afterwards', 'thereafter']
start_mod = ['preliminary', 'start', 'initial', 'first part', 'beginning', 'opening', 'early', 'dawn']
end_mod = ['final', 'end', 'closing', 'close', 'beginning', 'opening', 'early', 'dawn', 'latter', 'last part', 'last [fraction]']
middle_mod = ['middle', 'mid', 'centre', 'central', 'halfway', 'midway']
approx_mod = ['around', 'circa', 'c.a.', 'ca', 'about', 'near', 'approximately', 'soon']



DIRECT_NUMS = {
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "ninteen": 19,
    "zero": 0,
    "ten": 10,
}

SINGLE_NUMS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
}

SPECIAL_NUMS = {
    "score":20,
    "dozen":12,
    "baker's dozen": 13,
    "duo": 2, 
    "few": 3, 
    "couple": 2,
    "pair": 2,
    "brace": 2,
    "pair": 2,
    "trio": 3,
    "grand": 1000,
    "myriad":10000,
    "great gross":1728,
    "small gross":120,
    "great hundred":120,
    "gross":144,
    "quartet":4
}

TEN_PREFIXES = {
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fourty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}

BIG_PREFIXES = {
    "hundred": 100,
    "thousand": 1000,
    "million": 1_000_000,
    "billion": 1_000_000_000,
    "trillion": 1_000_000_000_000,
}

FRACTIONS = {"half": 2, "halves": 2, "quarter": 4, "quarters": 4}

ORDINALS = {"first": 1, "second": 2}

SINGLE_ORDINAL_FRACTIONALS = {
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
}

DIRECT_ORDINAL_FRACTIONALS = {
    "tenth": "10",
    "eleventh": "11",
    "twelfth": "12",
    "thirteenth": "13",
    "fourteenth": "14",
    "fifteenth": "15",
    "sixteenth": "16",
    "seventeenth": "17",
    "eighteenth": "18",
    "nineteenth": "19",
    "twentieth": "20",
    "thirtieth": "30",
    "fourtieth": "40",
    "fiftieth": "50",
    "sixtieth": "60",
    "seventieth": "70",
    "eightieth": "80",
    "ninetieth": "90",
}

# first second etc
ALL_ORDINALS = ORDINALS.copy()
ALL_ORDINALS.update(SINGLE_ORDINAL_FRACTIONALS)
ALL_ORDINALS.update(DIRECT_ORDINAL_FRACTIONALS)

opf = SINGLE_ORDINAL_FRACTIONALS.copy()
opf.update(DIRECT_ORDINAL_FRACTIONALS)
opf.update(FRACTIONS)
ONLY_PLURAL_FRACTIONS = {k + "s": v for k, v in opf.items() if not k.endswith('s')}
ONLY_PLURAL_FRACTIONS.update({k: v for k, v in opf.items() if k.endswith('s')})

ALL_FRACTIONS = ONLY_PLURAL_FRACTIONS.copy()
ALL_FRACTIONS.update(SINGLE_ORDINAL_FRACTIONALS)
ALL_FRACTIONS.update(DIRECT_ORDINAL_FRACTIONALS)
ALL_FRACTIONS.update(opf)

DIRECT_SINGLE_NUMS = DIRECT_NUMS.copy()
DIRECT_SINGLE_NUMS.update(SINGLE_NUMS)

ORDINAL_SINGLE = ORDINALS.copy()
ORDINAL_SINGLE.update(SINGLE_ORDINAL_FRACTIONALS)
