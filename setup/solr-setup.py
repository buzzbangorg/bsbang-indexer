#!/usr/bin/env python3

from lxml import etree, builder
import requests
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SolrSchema:
    def __init__(self, specfile):
        self.E = builder.ElementMaker()
        self.ROOT = self.E.schema
        with open(specfile) as f:
            self.specifications = json.load(f)
        self.schema = self.build()

    def fields(self):
        result = []
        for specType, specValue in self.specifications.items():
                # print(specType, specValue)
            result.append(self.E("field", name=specType, type='string'))
        return result

    def build(self):
        return self.ROOT(*self.fields())

def post_to_solr(json):
    headers = {'Content-type': 'application/json'}
    logger.info('Posting json - [%s]', json)
    r = requests.post(solrSchemaPath, json=json, headers=headers)
    logger.info('Response json - [%s]', r.text)


solrPath = 'http://localhost:8983/solr/buzzbang/'
solrSchemaPath = solrPath + 'schema'

configXml = SolrSchema('../specifications/BioChemEntity.json')
# print(etree.tostring(configXml.schema, pretty_print=True))

for fieldElem in configXml.schema.findall('./field'):
    logger.info(fieldElem.attrib['name'] + ' ' + fieldElem.attrib['type'])
    addFieldConfigJson = {
        'add-field': {
            'name': fieldElem.attrib['name'],
            'type': fieldElem.attrib['type'],
            'multiValued': fieldElem.get('multiValued', default='false')
        }
    }

    post_to_solr(addFieldConfigJson)

    addCopyFieldConfigJson = {
        'add-copy-field': {'source': fieldElem.attrib['name'], 'dest': '_text_'}
    }

    post_to_solr(addCopyFieldConfigJson)
