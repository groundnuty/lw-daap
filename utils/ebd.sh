#!/bin/bash

IP="$1"

if [ "x$IP" = "x" ]; then
    echo "GIMME SOME IP...."
    exit 1
fi


#
# INSTALL PREREQUISITES
#
sudo apt-get -y install build-essential git redis-server \
                        libmysqlclient-dev libxml2-dev libxslt-dev \
                        libjpeg-dev libfreetype6-dev libtiff-dev \
                        libffi-dev libssl-dev \
                        software-properties-common python-dev \
                        python-pip
sudo DEBIAN_FRONTEND=noninteractive apt-get -y install mysql-server
# nodejs installed from deb.nodesource.com
curl -sL https://deb.nodesource.com/setup | sudo bash -
sudo apt-get install -y nodejs
sudo su -c "npm install -g bower"
sudo npm install -g less@1.7.5 clean-css requirejs uglify-js bower
sudo pip install -U virtualenvwrapper pip

# Create a virtualenv to install all the python code there
. /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv portal-ebd

# Get the code
git clone https://github.com/aeonium/portal-ebd.git
# and work inside the portal-ebd dir
pushd portal-ebd

# install all requirements (this includes proper invenio version)
pip install -r requirements-devel.txt --exists-action i
# honcho and flower are included in requirements-devel
# pip install honcho flower
pip install -e .

# Basic invenio config
inveniomanage config create secret-key
inveniomanage config set CFG_EMAIL_BACKEND flask.ext.email.backends.console.Mail
inveniomanage config set CFG_BIBSCHED_PROCESS_USER $USER
# this is needed to make URLs work (not needed for localhost)
inveniomanage config set CFG_SITE_URL http://$IP:28080
inveniomanage config set CFG_SITE_SECURE_URL http://$IP:28080

# Bower used for managing css, js, etc
inveniomanage bower > bower.json
bower install

# Collect css, js, where flask expects to find it
inveniomanage config set COLLECT_STORAGE invenio.ext.collect.storage.link
inveniomanage collect
inveniomanage assets build

# Create the database
inveniomanage database init --user=root --yes-i-know
inveniomanage database create

# exit portal-ebd dir
popd


# This is the file that uses honcho to start the things
# includes the web, redis, celery and flower to check what's going on with celery
cat > Procfile << EOF
web: inveniomanage runserver -h 0.0.0.0
cache: redis-server
worker: celery worker --purge -E -A invenio.celery.celery --loglevel=DEBUG --workdir=\$VIRTUAL_ENV
workermon: flower --broker=redis://localhost:6379/1
EOF

# Create a "start.sh" script that can be reused later on
# starts bibsched and all the invenio legacy family
# and last starts with honcho the server
cat > start.sh << EOF
bibsched start
bibindex -s5m -u admin
bibrank -s5m -u admin
bibrank -f50000 -R -wwrd -s14d -L Sunday -u admin
bibreformat -s5m -o HB,HD -u admin
bibsort -R -s7d -L Sunday 01:00-05:00 -u admin
bibsort -s5m -u admin
#dbdump -s20h -L 22:00-06:00 --params="--max_allowed_packet=2G" -o /opt/portal-ebd/var/dbdump/ -n10 -u admin
inveniogc -a -s7d -L Sunday 01:00-05:00 -u admin
inveniogc -g -s1d -u admin
oairepositoryupdater -s1h -u admin
#There is no webcoll in invenio2.1
webcoll -s5m -u admin

honcho start
EOF

# start the thing
chmod +x start.sh
./start.sh
