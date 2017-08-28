import sys
import string
import json
import numpy
import math

from collections import Counter
from datetime import datetime
from itertools import combinations
from fuzzywuzzy import fuzz
from FeatureCode import FeatureCode

start = datetime.now()

# TODO: split data out between states and non-states
with open('json/states.json') as f:
    states = json.load(f)

with open('json/nonstates.json') as f:
    places = json.load(f)

print datetime.now() - start, ": Loading data"

# search = ['Crown Heights']                                         # Search string (split)

search = sys.argv[1].split(', ')

print datetime.now() - start, ": Creating states list"

state_candidates = []

for string in search:
    x = [
        state for state in states
        if string == state['admincode']
        or string == state['name']
        or string in state['alternatenames']
    ]
    if len(x) > 0:
        search.pop(search.index(string))
        state_candidates.extend(x)

if state_candidates:
    states = state_candidates

print datetime.now() - start, ": Filtering states list by search criteria"

if len(states) == 51:
    cities = filter(lambda x: x['featureclass'] == 'P', places)
else:
    cities = filter(lambda x: x['featureclass'] == 'P'
                    and any([s for s in states if s['admincode'] in x['admincode']])
                    , places)

print datetime.now() - start, ": Creating cities list from filtered states list"

city_candidates = []

for string in search:
    city_candidates.extend([
        city for city in cities
        if string == city['name']
        or string in city['alternatenames']
         ])

print datetime.now() - start, ": Filtering cities list for search string"

for city in city_candidates:
    print '\t', city['name'], city['admincode'], city['featurecode']

combos = combinations(city_candidates, 2)

for combo in combos:
    score = fuzz.partial_ratio(combo[0]['name'], combo[1]['name'])
    if 'score' not in combo[0]:
        combo[0]['score'] = score
    else:
        combo[0]['score'] += score
    if 'score' not in combo[1]:
        combo[1]['score'] = score
    else:
        combo[1]['score'] += score

scores = [c['score'] for c in city_candidates]
mean = numpy.mean(scores)
std = numpy.std(scores)

print datetime.now() - start, ": Using fuzzy matching to filter cities list"

print '\tMEAN', mean
print '\tSTD DEV', std

for city in city_candidates:
    print '\t', city['name'], city['score']

for i, c in enumerate(city_candidates):
    if (c['score'] - mean) / std < -1:
        del city_candidates[i]

codes = Counter([znk['admincode'] for znk in city_candidates])
maxcount = max([codes[i] for i in codes.keys()])
maxcodes = [x for x in codes.keys() if codes[x] == maxcount]

print datetime.now() - start, ": Retrieving most frequently occurring admin code(s)"

city_candidates = filter(lambda x: x['admincode'] in maxcodes, city_candidates)

print datetime.now() - start, ": Filtering city candidates based on most frequently occurring admin code(s)"

for city in city_candidates:
    print '\t', city['name'], city['admincode'], city['featurecode']

city_level = min(map(lambda x: FeatureCode[x['featurecode']].value, city_candidates))

city_candidates = [city for city in city_candidates if city['featurecode'] == FeatureCode(city_level).name]

print datetime.now() - start, ": Retrieving highest administrative division(s)"

for city in city_candidates:
    print '\t', city['name'], city['admincode'], city['featurecode']

# TODO: add population to place data; select highest populated area if all else fails
