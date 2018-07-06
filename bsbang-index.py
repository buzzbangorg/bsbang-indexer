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


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("indexer")


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

def match_config(type, mongodata):
    with open(specfile) as f:
        specifications = json.load(f)
    matchdata = {key:mongodata[key] for key in specifications if key in mongodata}
    
    return matchdata

class SolrIndexer:
    def __init__(self, solr_endpoint, jsonld, solr):
        self.jsonld = jsonld
        self.solr_endpoint = solr_endpoint

    def index(self):
        headers = {'Content-type': 'application/json'}
        logger.info('Posting %s', self.jsonld)
        r = requests.post(
            self.solr_endpoint + 'update/json/docs' + '?commit=true', json=self.jsonld, headers=headers)
        if r.status_code != 200:
            logger.error('Could not post to Solr: %s', r.text)


# MAIN
mongodb, solr = read_conf()
collection = connect_db(mongodb)
i=0
last_id = None
while i<1:
    data, last_id = read_mongodb(collection, page_size=1, last_id=last_id)
    for item in data:
        specfile = 'specifications/' + item['@type'] + '.json'
        sendSolr = {}
        _sendSolr = match_config(specfile, item)
        for k,v in _sendSolr.items():
            sendSolr[item['@type'] + '.' + k] = v
    i+=1


solr_endpoint = 'http://' + solr['SOLR_SERVER'] + ':' + solr['SOLR_PORT'] + '/solr/' + solr['SOLR_CORE'] + '/'
logger.info('Indexing at Solr core %s', solr_endpoint)

def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

pretty(sendSolr, indent=0)

indexer = SolrIndexer(solr_endpoint, sendSolr, solr)
indexer.index()