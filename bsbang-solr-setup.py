#!/usr/bin/env python3
import os
import json
import logging
import requests
import argparse
from lxml import etree
from bioschemas_indexer.schema import SolrSchema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# FUNCTIONS
def post_to_solr(json):
    headers = {'Content-type': 'application/json'}
    logger.info('Posting json - [%s]', json)
    r = requests.post(solrSchemaPath, json=json, headers=headers)
    logger.info('Response json - [%s]', r.text)


# MAIN
parser = argparse.ArgumentParser('Index extracted JSONLD into Solr.')
parser.add_argument('path_to_specs_dir', help='Path to the directory used to store bioschemas specifications.')
args = parser.parse_args()

specifications = [args.path_to_specs_dir + x for x in os.listdir(args.path_to_specs_dir)]

solrPath = 'http://localhost:8983/solr/buzzbang/'
solrSchemaPath = solrPath + 'schema'

configXml = SolrSchema(specifications)
# print(etree.tostring(configXml.schema, pretty_print=True))

for fieldElem in configXml.schema.findall('./field'):
    logger.info(fieldElem.attrib['name'] + ' ' + fieldElem.attrib['type'])
    addFieldConfigJson = {
        'add-field': {
            'name': fieldElem.attrib['name'],
            'type': fieldElem.attrib['type'],
            'multiValued': fieldElem.get('multiValued', default='true')
        }
    }

    post_to_solr(addFieldConfigJson)

    addCopyFieldConfigJson = {
        'add-copy-field': {'source': fieldElem.attrib['name'], 'dest': '_text_'}
    }

    post_to_solr(addCopyFieldConfigJson)
