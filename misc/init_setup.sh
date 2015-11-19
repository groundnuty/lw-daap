#!/bin/bash
# location of the folder that gets shared between containers
. /home/lwosf/venv/bin/activate

CFG_SHARED_FOLDER=/home/lwosf/venv/var/invenio.base-instance
mkdir -p $CFG_SHARED_FOLDER

inveniomanage config create secret-key

cfgfile=$(inveniomanage config locate)
cat <<EOF >> "$cfgfile"
CFG_SITE_URL = u'http://193.146.75.141:80'
CFG_SITE_SECURE_URL = u'http://193.146.75.141:80'
CFG_DATABASE_HOST = u'db'
CFG_DATABASE_NAME = "lwosf"
CFG_DATABASE_USER = "lwosf"
CFG_EMAIL_BACKEND = u'flask_email.backends.console.Mail'
CFG_BIBSCHED_PROCESS_USER = u'`whoami`'
COLLECT_STORAGE = u'flask_collect.storage.link'
CFG_LOGDIR = u'/home/lwosf/logs'
CFG_BIBSCHED_LOGDIR = u'/home/lwosf/logs/'
CFG_TMPDIR = u'/tmp/lwosf-`hostname`'
DEPOSIT_STORAGEDIR = u'/home/lwosf/storage'
EOF

echo "Installing and collecting assets, this will take a few minutes..."
pushd $CFG_SHARED_FOLDER
echo '{"directory": "/static/vendors"}' > .bowerrc
inveniomanage bower > bower.json
CI=true bower install --silent
rm .bowerrc  bower.json
popd
inveniomanage collect
inveniomanage assets build

inveniomanage database init --user=root --password=root_password --yes-i-know
inveniomanage database create
