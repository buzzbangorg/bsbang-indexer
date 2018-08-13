#!/usr/bin/env python3

import argparse
import requests
from bioschemas_indexer import indexer


# MAIN
parser = argparse.ArgumentParser('Run a test query against the Solr instance')
parser.add_argument('query')
args = parser.parse_args()

_, solr = indexer.read_conf()
solrSuggester = 'http://' + solr['SOLR_SERVER'] + ':' + \
    solr['SOLR_PORT'] + '/solr/' + solr['SOLR_CORE'] + \
    '/suggest?suggest.dictionary=mySuggester&suggest=true&suggest.build=true&suggest.q='

# params = {'q': args.query}

r = requests.get(solrSuggester + args.query)
resp = r.json()
# print(r.text)

for word in resp["suggest"]["mySuggester"][args.query]["suggestions"]:
    print(word["term"])
