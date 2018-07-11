#!/usr/bin/env python3

import argparse
import requests
from bioschemas_indexer import indexer


# MAIN
parser = argparse.ArgumentParser('Run a test query against the Solr instance')
parser.add_argument('query')
args = parser.parse_args()

_, solr = indexer.read_conf()
solrSpellCheckPath = 'http://' + solr['SOLR_SERVER'] + ':' + \
    solr['SOLR_PORT'] + '/solr/' + solr['SOLR_CORE'] + '/spell'

params = {'q': args.query}

r = requests.get(solrSpellCheckPath, params=params)
resp = r.json()
# print(r.text)

for word in resp["spellcheck"]["suggestions"][-1]["suggestion"]:
    print(word["word"])
