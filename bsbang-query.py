#!/usr/bin/env python3

import argparse
import requests

solrQueryPath = 'http://localhost:8983/solr/buzzbang/select'

# MAIN
parser = argparse.ArgumentParser('Run a test query against the Solr instance')
parser.add_argument('query')
args = parser.parse_args()

params = {'q': args.query, 'defType': 'edismax'}

r = requests.get(solrQueryPath, params=params)
print(r.url)
print(r.text)
