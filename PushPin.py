import json
import numpy
import logging

from collections import Counter
from itertools import combinations
from fuzzywuzzy import fuzz
from FeatureCode import FeatureCode

logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)


with open('json/states.json') as f:
    states = json.load(f)

# TODO: Add state property to non-states data objects
with open('json/nonstates.json') as f:
    places = json.load(f)

filtered_states = []
cities = []

search = []


def locate(search_string):
    global filtered_states
    global cities
    global search

    search = search_string.split(', ')

    filter_states()
    filter_cities()
    filter_states_by_city()

    if not cities:
        return None, None

    logger.info('Final Result:')

    for city in cities: logger.info('\t%s %s %s', city['name'], city['admincode'], city['featurecode'])

    city = dict(name=cities[0]['name'])
    state = dict(name=filtered_states[0]['name'], abbr=filtered_states[0]['admincode'])

    filtered_states = []
    cities = []

    return city, state

    # TODO: add population to place data; select highest populated area if all else fails


def filter_cities():
    global filtered_states
    global cities
    global search

    filter_cities_by_state()

    length = len(cities)

    filter_cities_by_search_string()

    if len(cities) == length:
        cities = []
        return
    elif len(cities) == 1:
        return

    for func in (
        fuzzy_match_city_names,
        filter_cities_by_admin_code,
        filter_cities_by_highest_admin_level,
    ):
        func()
        log_details()
        if len(cities) <= 1:
            break


def filter_states():
    global states
    global filtered_states
    global search

    logger.info("Filtering states list by search criteria")

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
        filtered_states = state_candidates
    else:
        filtered_states = states[:]


def filter_states_by_city():
    global filtered_states
    global cities

    logger.info("Filtering states list by final city results")

    filtered_states = [state for state in filtered_states if
                       any([c for c in cities if state['admincode'] in c['admincode']])]


def filter_cities_by_state():
    global filtered_states
    global places
    global cities

    logger.info("Creating cities list from filtered states list")

    if len(filtered_states) == 51:
        cities = filter(lambda x: x['featureclass'] == 'P', places)
    else:
        cities = filter(lambda x: x['featureclass'] == 'P'
                        and any([s for s in filtered_states if s['admincode'] in x['admincode']])
                        , places)


def filter_cities_by_search_string():
    global cities
    global search

    logger.info("Filtering cities list for search string")

    city_candidates = []

    for string in search:
        city_candidates.extend([
            city for city in cities
            if string == city['name']
            or string in city['alternatenames']
             ])

    if city_candidates:
        cities = city_candidates


def fuzzy_match_city_names():
    global cities

    logger.info("Using fuzzy matching to filter cities list")

    if len(cities) > 100:
        logger.info("Cities list too long, skipping")
        return

    city_candidates = cities[:]

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

    if std != 0:
        for i, c in enumerate(city_candidates):
            if (c['score'] - mean) / std < -1:
                del city_candidates[i]

    if city_candidates:
        cities = city_candidates

    logger.debug('\t%s %i', 'MEAN', mean)
    logger.debug('\t%s %i', 'STD DEV', std)


def filter_cities_by_admin_code():
    global cities

    logger.info("Filtering city candidates based on most frequently occurring admin code(s)")

    city_candidates = cities[:]

    codes = Counter([city['admincode'] for city in city_candidates])
    maxcount = max([codes[i] for i in codes.keys()])
    maxcodes = [x for x in codes.keys() if codes[x] == maxcount]

    logger.info("Retrieving most frequently occurring admin code(s)")

    city_candidates = filter(lambda x: x['admincode'] in maxcodes, city_candidates)

    if city_candidates:
        cities = city_candidates


def filter_cities_by_highest_admin_level():
    global cities

    logger.info("Retrieving highest administrative division(s)")

    city_candidates = cities[:]

    city_level = min(map(lambda x: FeatureCode[x['featurecode']].value, cities))

    city_candidates = [city for city in city_candidates if city['featurecode'] == FeatureCode(city_level).name]

    if city_candidates:
        cities = city_candidates


def log_details():
    logger.debug('\tCount: %i', len(cities))
    for city in cities[:12]: logger.debug('\t%s %s %s', city['name'], city['admincode'], city['featurecode'])
    if len(cities) > 12: logger.debug('\t...')