import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("indexer")


class SolrIndexer:
    def __init__(self, solr_endpoint, jsonld):
        self.jsonld = jsonld
        self.solr_endpoint = solr_endpoint

    def index(self):
        headers = {'Content-type': 'application/json'}
        logger.info('Posting %s', self.jsonld)
        r = requests.post(
            self.solr_endpoint + 'update/json/docs' + '?commit=true', json=self.jsonld, headers=headers)
        if r.status_code != 200:
            logger.error('Could not post to Solr: %s', r.text)
