import json
import itertools


with open('json/locations.json') as f:
    places = json.load(f)

search = ['Garwood', 'New Jersey']

states = [place for place in places if place['featurecode'] == 'ADM1']      # All states

for string in search:

    codes = [place['admincode']
             for place in places
             if place['name'] == string
             or string in place['alternatenames']]

    codes = list(set(codes))

    states = [state for state in states for code in codes if state['admincode'] in code]

states = [k for k, v in itertools.groupby(states)]                          # Remove duplicate references

for state in states:
    print state['name']

cities = [place for place in places if place['featureclass'] == 'P']        # All cities


"""
Cities will be a different strategy. I think I will need to do an additive process rather than
a reductive one, adding all the matches for each string in the list and then determining the
highest-ranking populated place among those included.
"""