#!/usr/bin/env python3
import os
import json
import logging
import requests
import argparse
from bioschemas_indexer import indexer
from lxml import etree
from bioschemas_indexer.schema import SolrSchema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# FUNCTIONS
def add_to_schema_xml(json):
    solrSchemaPath = solrPath + 'schema'
    headers = {'Content-type': 'application/json'}
    logger.info('Posting json - [%s]', json)
    r = requests.post(solrSchemaPath, json=json, headers=headers)
    logger.info('Response json - [%s]', r.text)


def add_to_solrconfig_xml(json):
    solrSchemaPath = solrPath + 'config'
    headers = {'Content-type': 'application/json'}
    logger.info('Posting json - [%s]', json)
    r = requests.post(solrSchemaPath, json=json, headers=headers)
    logger.info('Response json - [%s]', r.text)


def add_solr_fields(configXml):
    for fieldElem in configXml.schema.findall('./field'):
        logger.info(fieldElem.attrib['name'] + ' ' + fieldElem.attrib['type'])
        addFieldConfigJson = {
            'add-field': {
                'name': fieldElem.attrib['name'],
                'type': fieldElem.attrib['type'],
                'multiValued': fieldElem.get('multiValued', default='true'),
                'indexed': fieldElem.get('indexed', default='true'),
                'stored': fieldElem.get('stored', default='true')
            }
        }
        add_to_schema_xml(addFieldConfigJson)

        addCopyFieldConfigJson = {
            'add-copy-field': {'source': fieldElem.attrib['name'], 'dest': '_text_'}
        }
        add_to_schema_xml(addCopyFieldConfigJson)


# MAIN
parser = argparse.ArgumentParser('Index extracted JSONLD into Solr.')
parser.add_argument('path_to_specs_dir',
                    help='Path to the directory used to store bioschemas specifications.')
args = parser.parse_args()

_, solr = indexer.read_conf()

specifications = [args.path_to_specs_dir +
                  x for x in os.listdir(args.path_to_specs_dir)]

solrPath = 'http://' + solr['SOLR_SERVER'] + ':' + solr['SOLR_PORT'] + \
    '/solr/' + solr['SOLR_CORE'] + '/'

# print(etree.tostring(configXml.schema, pretty_print=True))

configXml = SolrSchema(specifications)
add_solr_fields(configXml)
