import json
import itertools

# TODO: split data out between states and non-states
with open('json/locations.json') as f:
    places = json.load(f)

search = ['Garwood', 'NJ']

states = [place for place in places if place['featurecode'] == 'ADM1']      # All states

for string in search:

    # TODO: define function that encapsulates if logic for different search strings
    codes = [place['admincode']
             for place in places
             if place['name'] == string
             or string in place['alternatenames']]

    codes = list(set(codes))

    states = [state for state in states for code in codes if state['admincode'] in code]

states = [k for k, v in itertools.groupby(states)]                          # Remove duplicate references

cities = [place                                                             # All cities in filtered states
          for place in places
          for state in states
          if place['featureclass'] == 'P'
          and state['admincode'] in place['admincode']]

cities = [k for k, v in itertools.groupby(cities)]

city_candidates = []

for string in search:

    city_candidates.extend([city for city in cities
                            if city['name'] == string
                            or string in city['alternatenames']])

for city in city_candidates:
    print city['name'], city['admincode'], city['featurecode']


"""
Cities will be a different strategy. I think I will need to do an additive process rather than
a reductive one, adding all the matches for each string in the list and then determining the
highest-ranking populated place among those included.
"""