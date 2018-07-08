import os
import logging
import pymongo
import requests
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
            mongodb = {x: y for x, y in parser.items(section_name)}
        if section_name == 'SolrServer':
            solr = {x: y for x, y in parser.items(section_name)}
    return mongodb, solr


def connect_db(mongodb):
    client = pymongo.MongoClient(
        mongodb['MONGODB_SERVER'],
        int(mongodb['MONGODB_PORT'])
    )
    try:
        client.server_info()
    except pymongo.errors.ServerSelectionTimeoutError as e:
        logger.error("MongoDB not connected at %s:%s", mongodb[
                     'MONGODB_SERVER'], mongodb['MONGODB_PORT'])
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


def get_speclist():
    specfiles = os.listdir("specifications/")
    specs = []
    for file in specfiles:
        filename = os.path.splitext(file)
        if filename[1] == ".json":
            specs.append(filename[0])
    return specs


def prettyprint(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            prettyprint(value, indent + 1)
        else:
            print('\t' * (indent + 1) + str(value), type(value))
