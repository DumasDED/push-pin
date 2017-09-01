from setuptools import setup

from os import path

here = path.abspath(path.dirname(__file__))


setup(
    name='PushPin',

    version='0.0.1',

    description='Tool for deriving accurate locations from strings',

    url='https://github.com/DumasDED/push-pin',

    author='Dumas.DED',
    author_email='Dumas.DED@Gmail.com',

    license='MIT',

    keywords='string location search',

    py_modules=['PushPin', 'FeatureCode'],

    install_requires=['fuzzywuzzy'],

    data_files=[('lib/python/site-packages/json', ['json/states.json', 'json/nonstates.json', 'json/locations.json'])]
)