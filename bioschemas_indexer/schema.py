import os
import json
from lxml import builder


class SolrSchema:

    def __init__(self, specdir):
        self.E = builder.ElementMaker()
        self.ROOT = self.E.schema
        self.fields = []
        for specfile in specdir:
            self.fields.extend(self.add_fields(specfile))
        self.schema = self.build()

    def add_fields(self, specfile):
        result = []
        with open(specfile) as f:
            specname = os.path.splitext(os.path.basename(specfile))[0]
            self.specifications = json.load(f)

        for specType, specValue in self.specifications.items():
            # print(specType, specValue)
            result.append(self.E("field", name=specname +
                                 '.' + specType, type='string'))
        return result

    def build(self):
        return self.ROOT(*self.fields)
