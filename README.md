# bsbang-indexer
Apache Solr indexer for the [Buzzbang crawl data format](https://github.com/buzzbangorg/buzzbang-doc/wiki/Buzzbang-crawl-data-format)

## Getting Started
**Step 1: Create a virtual environment and clone this repo**

```
pip3 install virtualenv
python3 -m venv buzzbang
source buzzbang/bin/activate
git clone https://github.com/buzzbangorg/bsbang-crawler-ng.git
cd bsbang-crawler-ng
```

**Step 2: Install Python dependencies**

```
pip3 install -r requirements.txt
```

**Step 3: Install Solr if necessary**

Once installed, you may check the running status using the command - ```service solr status``` and you can access the UI in your browser at ```localhost:8983/```

**Step 4: Create a Solr core named buzzbang**

```
./solr start
./solr create -c buzzbang
```  

**Step 5: Configure the buzzbang core**

***Configure Solr core to prevent duplication***

We want to configure the buzzbang core to do deduplication of entries.  This won't matter for the first indexing run,
but will be important on subsequent runs to prevent double indexing.

In `$SOLR/server/solr/buzzbang/conf`, locate the entry that looks like

```
  <!--
     <updateRequestProcessorChain name="dedupe">
       <processor class="solr.processor.SignatureUpdateProcessorFactory">
         <bool name="enabled">true</bool>
         <str name="signatureField">id</str>
         <bool name="overwriteDupes">false</bool>
         <str name="fields">name,features,cat</str>
         <str name="signatureClass">solr.processor.Lookup3Signature</str>
       </processor>
       <processor class="solr.LogUpdateProcessorFactory" />
       <processor class="solr.RunUpdateProcessorFactory" />
     </updateRequestProcessorChain>
    -->
```

and uncomment it.  

***Configure Solr core to enable suggester module***

Solr can provide suggestions as we type-in our query using the Suggester module, jsut as google does. To enable it in solr we have to put following XML in the solr-config.xml module. Note that, we need to include it in solr before we index any document and we should restart Solr after editing this file using `service solr restart`

Solr will internally build up a library for providing suggestions and it will use only those fields that has been mentioned in this XML. For eg: In the snippet provided below, we are asking Solr to use the "name" field for populating its suggester dictionary. We may provide as many fields as we want using this - 

``` <str name="field">name</str> ``` 

In `$SOLR/server/solr/buzzbang/conf`, paste the following XML - 

```
    <searchComponent name="suggest" class="solr.SuggestComponent">
      <lst name="suggester">
        <str name="name">mySuggester</str>
        <str name="lookupImpl">FuzzyLookupFactory</str>
        <str name="dictionaryImpl">DocumentDictionaryFactory</str>
        <str name="field">name</str>
        <str name="suggestAnalyzerFieldType">string</str>
      </lst>
    </searchComponent>

    <requestHandler name="/suggest" class="solr.SearchHandler"
                    startup="lazy" >
      <lst name="defaults">
        <str name="suggest">true</str>
        <str name="suggest.count">10</str>
      </lst>
      <arr name="components">
        <str>suggest</str>
      </arr>
    </requestHandler>
```


**Step 6: Setup config/settings.ini and configure if necessary**

You will only need to edit this file if you have configured Solr or MongoDB on non-default ports
, or if you have changed the database or collection name where the crawl is stored.

```
cd $BUZZBANG/conf
cp settings.ini.example settings.ini
```

**Step 7: Add fields to the Buzzbang core**

```
./bsbang-solr-setup.py <specifications-path> 
```

Next, open SolrUI on a browser and select the core where the data is to be indexed. Check the directory location where the Solr core data is going to be saved and relace the solrconfig.xml in that directory with conf/solrconfig.xml file. This will enable the de-duplication mode in solr indexing. You may need root access to replace this file.

Example:

```
./bsbang-solr-setup.py specifications
```

**Step 8: Use the query and spell check module**

```
./bsbang-query.py <words>
./bsbang-spellCheck.py <single-word>
```

Example:

```
./bsbang-query.py "treatment conditions"
./bsbang-spellCheck.py extrct
```

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests to us.

## License
This project is licensed under the Apache-2.0 License - see the LICENSE file for details


## Mind Map
- [x] MongoDB Pagnation
- [x] MongoDB to Solr
- [x] query parser
- [x] Spell Check
- [x] Suggester
- [x] Deduplication
- [ ] Automated fetching specification from the bioschemas.org
- [ ] Solr and MongoDB multithreading
- [ ] Setup deduplicaiton, spell-check and suggester using the solrconfig api 
