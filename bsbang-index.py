#!/usr/bin/env python3

import json
import timeit
import logging
from bioschemas_indexer import indexer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("indexer")


def match_config(specfile, mongodata):
    with open(specfile) as f:
        specifications = json.load(f)
    matchdata = {key: mongodata[key]
                 for key in specifications if key in mongodata}
    return matchdata


def flatten(d, bioschemas):
    def open(d, stype, bioschemas):
        global struct
        if stype in bioschemas:
            specfile = 'specifications/' + stype + '.json'
            sendSolr = {}
            _sendSolr = match_config(specfile, d)
            for key, value in _sendSolr.items():
                if isinstance(value, dict):
                    sendSolr[stype + '.' + key] = stype
                    flatten(value, bioschemas)
                elif isinstance(value, list):
                    if isinstance(value[0], dict):
                        continue
                        # TBD LATER
                else:
                    sendSolr[stype + '.' + key] = value
            # prettyprint(sendSolr)
            struct = {**struct, **sendSolr}

    if isinstance(d['@type'], list):
        for stype in d['@type']:
            open(d, stype, bioschemas)
    else:
        open(d, d['@type'], bioschemas)


def solr_indexer(solr_endpoint, jsonld):
    headers = {'Content-type': 'application/json'}
    # logger.info('Posting %s', self.jsonld)
    r = requests.post(solr_endpoint + 'update/json/docs' +
                      '?commit=true', json=jsonld, headers=headers)
    if r.status_code != 200:
        logger.error('Could not post to Solr: %s', r.text)


# MAIN
mongodb, solr = indexer.read_conf()
collection = indexer.connect_db(mongodb)
solr_endpoint = 'http://' + solr['SOLR_SERVER'] + ':' + \
    solr['SOLR_PORT'] + '/solr/' + solr['SOLR_CORE'] + '/'
bioschemas = indexer.get_speclist()

i = 0
last_id = None
while i < 1:
    data, last_id = indexer.read_mongodb(
        collection, page_size=1, last_id=last_id)
    for item in data:
        struct = {}
        # start_time = timeit.default_timer()
        flatten(item, bioschemas)
        # print(timeit.default_timer() - start_time)
        # prettyprint(struct)
        indexer.solr_indexer(solr_endpoint, struct)
    i += 1
