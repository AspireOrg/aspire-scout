Installation
-----
**Install RabbitMQ, Redis, and Mongodb, reconfigure config file accordingly.**

**Install these**
```
sudo apt-get install -y build-essential libssl-dev libffi-dev software-properties-common git lib32ncurses5-dev pkg-config libssl-dev libcurl4-openssl-dev
sudo add-apt-repository ppa:deadsnakes/ppa
sudo add-apt-repository ppa:tah83/secp256k1
sudo apt-get update
sudo apt-get install -y python3.5 python3.5-dev python3.5-venv libsecp256k1-dev
```

**Create virutal env:**
```
cd /vagrant
python3.5 -m venv ./virt
```

**Dependencies:**
```
cd /vagrant
source virt/bin/activate
pip install wheel
pip install -r requirements.txt
```

**Install NPM & Sass**
```
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.31.1/install.sh | bash
source ~/.profile
nvm install v13.6.0
npm install -g sass
cd virt/lib/python3.5/site-packages/
rm -R ./webassets
git clone https://github.com/miracle2k/webassets.git
cd webassets
python setup.py install
```

Deving Tips
-----
**Need this to load config:**
```
export AEOLUS_CONFIG=/path/to/project/config/development.py
```

**Initial Setup:**
``` 
cd /path/to/project
source ./virt/bin/activate
```

**Run Dev Web Server (single threaded):**
``` 
python run.py
```

**Run Prod Web Server (multiprocess):**
``` 
virt/bin/gunicorn -c gunicorn-config.py wsgi:backend
```

**Run Celery Worker:**
```
celery worker -A rush.tasks -Q queues,here,to,process
```

**Delete All Python Cache Files**
```
find . -name "*.pyc" -exec rm -f {} \;
```