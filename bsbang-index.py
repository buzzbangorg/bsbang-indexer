#!/usr/bin/env python3

import timeit
import logging
import requests
from multiprocessing import Process, Queue
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


def collect_data(mongodb, q):
    n = 1000
    global last_id
    global struct
    collection = indexer.connect_db(mongodb)
    bioschemas = indexer.get_speclist()
    len_db = 50
    for i in range(len_db):
        data, last_id = indexer.read_mongodb(
            collection, page_size=n, last_id=last_id)
        for item in data:
            flatten(item, bioschemas)
            q.put(struct)
            struct = {}
        logger.info("collected %d docs", n)
        i += 1
    q.put(False)


def index_data(solr, q):
    while True:
        # print(q.qsize())
        jsonld = []
        for i in iter(q.get, False):
            jsonld.append(i)
        solr_endpoint = 'http://' + solr['SOLR_SERVER'] + ':' + \
            solr['SOLR_PORT'] + '/solr/' + solr['SOLR_CORE'] + '/'
        headers = {'Content-type': 'application/json'}
        logger.info('Posting doc')
        r = requests.post(solr_endpoint + 'update/json/docs' +
                          '?commit=true', json=jsonld, headers=headers)
        if r.status_code != 200:
            logger.error('Could not post to Solr: %s', r.text)
        if q.empty() == True:
            break


# MAIN
############################################################
mongodb, solr = indexer.read_conf()
struct = {}
last_id = None
############################################################
start_time = timeit.default_timer()
############################################################
q = Queue()
process_one = Process(target=collect_data, args=(mongodb, q))
process_two = Process(target=index_data, args=(solr, q))
process_one.start()
process_two.start()
q.close()
q.join_thread()

process_one.join()
process_two.join()
############################################################
print(timeit.default_timer() - start_time)
