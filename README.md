# bsbang-indexer
Repository for Apache Solr indexing in Buzzbang Bioschemas crawler

**THIS IS NOT YET COMPLETE, PLEASE DO NOT USE YET**

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

**Step 3: Install MongoDB if necessary**

Install MongoDB on your system.

Setup the MongoDB server using MongoDBServer settings in the conf/settings.ini file.

Start and check if the MongoDB server is up using the following commands in another terminal - 
```
service mongodb start
service mongodb status
``` 

**Step 4: Put initialization arguments in the config/setting.ini file**

The defaults are probably going to be fine but you might want to check them.


**Step 5: Install Solr**

** Past this point, we still need to implement indexing of data into Solr **

Install Solr on your system.

Once installed, you may check the running status using the command - ```service solr status``` and you can access the UI in your browser at ```localhost:8983/```

**Step 6: Create a Solr core named buzzbang**

```
sudo su - solr -c "/opt/solr/bin/solr create -c buzzbang"
```

If you used a different installation location for Solr, use that particular Solr bin path to create a core.  

```
cd $SOLR/bin
./solr create -c buzzbang
```

TIP: To delete a Solr core permanently, point your browser to the following link - 

```
http://localhost:8983/solr/admin/cores?action=UNLOAD&core=buzzbang
```  

**Step 7: Setup and configure buzzbang**

```
cd bsbang-crawler-ng/setup
./solr-setup.py <path-to-bsbang-config-file> --solr-core-url <URL-of-solr-endpoint>

```

Example:

```
./solr-setup.py ../config/solr-setup.xml --solr-core-url http://localhost:8983/solr/buzzbang/
```

## Running the tests
TBD

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests to us.

## License
This project is licensed under the Apache-2.0 License - see the LICENSE file for details


## Mind Map
- [ ] MongoDB Pagnation
- [ ] MongoDB to Solr
