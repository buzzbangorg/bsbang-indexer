#!/usr/bin/env python3

import os
import sys
import json
import pprint
import logging
import pymongo
import hashlib
import requests
import canonicaljson
from lxml import etree
from six.moves.configparser import ConfigParser
from bioschemas_indexer.indexer import SolrIndexer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("indexer")


def get_speclist():
    specfiles = os.listdir("specifications/")
    specs = []
    for file in specfiles:
        filename = os.path.splitext(file)
        if filename[1] == ".json":
            specs.append(filename[0])
    return specs

def read_conf():
    config_file = "conf/settings.ini"
    parser = ConfigParser()
    parser.optionxform = str
    parser.read(config_file)
    for section_name in parser.sections():
        if section_name == 'MongoDBServer':
            mongodb = {x:y for x,y in parser.items(section_name)}
        if section_name == 'SolrServer':
            solr = {x:y for x,y in parser.items(section_name)}
    return mongodb, solr

def connect_db(mongodb):
    client = pymongo.MongoClient(
            mongodb['MONGODB_SERVER'],
            int(mongodb['MONGODB_PORT'])
        )
    try:
        client.server_info()
    except pymongo.errors.ServerSelectionTimeoutError as e:
        logger.error("MongoDB not connected at %s:%s", mongodb['MONGODB_SERVER'], mongodb['MONGODB_PORT'])
        sys.exit()
    logger.info("Connected to MongoDB")
    db = client[mongodb['MONGODB_DB']]
    collection = db[mongodb['MONGODB_COLLECTION']]

    return collection

def read_mongodb(collection, page_size, last_id=None):
    if last_id is None:
        cursor = collection.find().limit(page_size)
    else:
        cursor = collection.find({'_id': {'$gt': last_id}}).limit(page_size)
    data = [x for x in cursor]
    if not data:
        return None, None
    last_id = data[-1]['_id']

    return data, last_id

def prettyprint(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         prettyprint(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value), type(value))

def match_config(specfile, mongodata):
    with open(specfile) as f:
        specifications = json.load(f)
    matchdata = {key:mongodata[key] for key in specifications if key in mongodata}
    
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


# MAIN
mongodb, solr = read_conf()
collection = connect_db(mongodb)
solr_endpoint = 'http://' + solr['SOLR_SERVER'] + ':' + solr['SOLR_PORT'] + '/solr/' + solr['SOLR_CORE'] + '/'
bioschemas = get_speclist()

i=0
last_id = None
while i<1000:
    data, last_id = read_mongodb(collection, page_size=1, last_id=last_id)
    for item in data:
        struct = {}
        flatten(item, bioschemas)
        # prettyprint(struct)
        indexer = SolrIndexer(solr_endpoint, struct)
        indexer.index()
    i+=1
