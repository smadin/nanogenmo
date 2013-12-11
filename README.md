nanogenmo
=========

A simple script written for Darius Kazemi's #NaNoGenMo

By default, fetches random Wikipedia pages until it has ~10,000 words, then builds Markov chains from that data until it has ~50,000 words, broken into 12 "chapters". Can also follow links from the initial page instead of fetching new random pages, and use a user-specified search term for the initial page instead of picking randomly. Several other configuration options also available.

Requires PyMarkovChain (https://pypi.python.org/pypi/PyMarkovChain/1.7.5) and Wikipedia (https://pypi.python.org/pypi/wikipedia/1.0.3)
