#!/usr/bin/env python3

import timeit
import logging
import requests
from bioschemas_indexer import indexer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("indexer")


def flatten(d, bioschemas):
    def open(d, stype, bioschemas):
        global struct
        if stype in bioschemas:
            specfile = 'specifications/' + stype + '.json'
            sendSolr = {}
            _sendSolr = indexer.match_config(specfile, d)
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


def collect_data(mongodb):
    n = 1000
    global last_id
    collection = indexer.connect_db(mongodb)
    bioschemas = indexer.get_speclist()
    data, last_id = indexer.read_mongodb(
        collection, page_size=n, last_id=last_id)
    sendSolr = []
    for item in data:
        global struct
        flatten(item, bioschemas)
        sendSolr.append(struct)
        struct = {}

    logger.debug("Retrieved %d MongoDB entries", n)

    return sendSolr


def index_data(solr, jsonld):
    """
    Index the given jsonld into the Solr instance.

    :param solr:
    :param jsonld:
    :return: True on success, False on failure
    """

    solr_endpoint = 'http://' + solr['SOLR_SERVER'] + ':' + \
        solr['SOLR_PORT'] + '/solr/' + solr['SOLR_CORE'] + '/'
    headers = {'Content-type': 'application/json'}
    # logger.info('Posting %s', self.jsonld)
    r = requests.post(solr_endpoint + 'update/json/docs' +
                      '?commit=true', json=jsonld, headers=headers)
    if r.status_code != 200:
        logger.error('Could not post to Solr: %s', r.text)
        return False
    else:
        return True


# MAIN
mongodb, solr = indexer.read_conf()
struct = {}
last_id = None
collection = indexer.connect_db(mongodb)
n_docs = collection.count()
total_indexed = 0

# logger.info('Indexing %d MongoDB entries', n_docs)

start_time = timeit.default_timer()
for i in range(int(n_docs / 1000)+1):
    sendSolr = collect_data(mongodb)

    if index_data(solr, sendSolr):
        total_indexed += len(sendSolr)
        logger.info("Indexed %d of %d MongoDB entries", total_indexed, n_docs)

print(timeit.default_timer() - start_time)
