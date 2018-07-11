#!/usr/bin/env python3

import argparse
import requests
from bioschemas_indexer import indexer


# MAIN
parser = argparse.ArgumentParser('Run a test query against the Solr instance')
parser.add_argument('query')
args = parser.parse_args()

_, solr = indexer.read_conf()
solrQueryPath = 'http://' + solr['SOLR_SERVER'] + ':' + \
    solr['SOLR_PORT'] + '/solr/' + solr['SOLR_CORE'] + '/select'

params = {'q': args.query, 'defType': 'edismax'}

r = requests.get(solrQueryPath, params=params)
print(r.url)
print(r.text)
