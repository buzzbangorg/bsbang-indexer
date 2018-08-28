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

**Step 5: Setup config/settings.ini and configure if necessary**

You will only need to edit this file if you have configured Solr or MongoDB on non-default ports
, or if you have changed the database or collection name where the crawl is stored.

```
cd $BUZZBANG/config
cp settings.ini.example settings.ini
```

**Step 6: Setup the Buzzbang core**

```
./bsbang-solr-setup.py <specifications-path> 
```

Next, open SolrUI on a browser and select the core where the data is to be indexed. Check the directory location where the Solr core data is going to be saved and relace the solrconfig.xml in that directory with conf/solrconfig.xml file. This will enable the de-duplication mode in solr indexing. You may need root access to replace this file.

Example:

```
./bsbang-solr-setup.py specifications
```

**Step 7: Use the query and spell check module**

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
