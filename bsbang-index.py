#!/usr/bin/env python3

import timeit
import time
import logging
import requests
import threading
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
            struct = {**struct, **sendSolr}

    if isinstance(d['@type'], list):
        for stype in d['@type']:
            open(d, stype, bioschemas)
    else:
        open(d, d['@type'], bioschemas)


def collect_data(mongodb):
    n = 100
    global last_id
    global struct
    global n_docs
    global q
    collection = indexer.connect_db(mongodb)
    n_docs = collection.count()
    bioschemas = indexer.get_speclist()
    data, last_id = indexer.read_mongodb(
        collection, page_size=n, last_id=last_id)
    for i in range(int(n_docs / n)+1):
        for item in data:
            flatten(item, bioschemas)
            q.append(struct)
            struct = {}
# 106713

def index_data(solr):
    global q
    global flag
    global n_docs
    while True:
        if len(q) == 0:
            continue
        jsonld = q[flag:-1]
        print("->", flag, len(q)-1)
        flag = len(q)
        # time.sleep(1)
        solr_endpoint = 'http://' + solr['SOLR_SERVER'] + ':' + \
            solr['SOLR_PORT'] + '/solr/' + solr['SOLR_CORE'] + '/'
        headers = {'Content-type': 'application/json'}
        logger.info('Posting doc')
        r = requests.post(solr_endpoint + 'update/json/docs' +
                          '?commit=true', json=jsonld, headers=headers)
        if r.status_code != 200:
            logger.error('Could not post to Solr: %s', r.text)
        if flag>n_docs:
            break


# MAIN
mongodb, solr = indexer.read_conf()
struct = {}
last_id = None
n_docs = 0
flag = 0
q = list()

start_time = timeit.default_timer()
T1 = threading.Thread(target=collect_data, args=(mongodb,))
T2 = threading.Thread(target=index_data, args=(solr,))
T1.start()
T2.start()
T1.join()
T2.join()
print(timeit.default_timer() - start_time)
