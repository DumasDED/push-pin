import json
import itertools


def name_match(pl, st, precision):
    if len(st) == 2:
        return pl['admincode'] == st                                        # Two-letter strings == state abbrs.
    elif precision == 0:
        return st in pl['name'] or st in pl['alternatenames']               # String in name or alternate names
    elif precision == 1:
        return st == pl['name'] or st in pl['alternatenames']               # String matches name or in alternate names
    else:
        return st == pl['name']                                             # String matches name


# TODO: split data out between states and non-states
with open('json/locations.json') as f:                                      # Load from JSON
    places = json.load(f)

search = ['Crown Heights']                                                  # Search string (split)

states = [place for place in places if place['featurecode'] == 'ADM1']      # All states

for string in search:
    codes = [place['admincode'] for place in places if name_match(place, string, 1)]
    codes = list(set(codes))
    states = [state for state in states for code in codes if state['admincode'] in code]

states = [k for k, v in itertools.groupby(states)]                          # Remove duplicate references

cities = [place for place in places for state in states                     # All cities in filtered states
          if place['featureclass'] == 'P'
          and state['admincode'] in place['admincode']]

cities = [k for k, v in itertools.groupby(cities)]                          # Remove duplicate references

city_candidates = []

for string in search:
    city_candidates.extend([city for city in cities if name_match(city, string, 1)])

for city in city_candidates:
    print city['name'], city['admincode'], city['featurecode']

# TODO: incorporate enum of prioritized PPL feature codes to allow selection of highest ranking PPL
# TODO: add population to place data; select highest populated area if all else fails
