#!/usr/bin/env bash
#
# Version 0.1b
# Next TODO
#   -Config SSL Apache
#   -Remove HARDCODE celeryd config args
#   -Set custom conf args for redis-server
#

die () {
   echo >&2 "$@"
   exit 1
}

[ "$#" -eq 1 ] || die "Usage: $(basename $0) http://<site url>:<site port>"
#
# INSTALL PREREQUISITES
#
sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get -y install build-essential git redis-server \
		   libmysqlclient-dev libxml2-dev libxslt-dev \
		   libjpeg-dev libfreetype6-dev libtiff-dev \
		   libffi-dev libssl-dev \
		   software-properties-common python-dev \
		   python-pip apache2 libapache2-mod-wsgi libapache2-mod-xsendfile \
		   libapache2-mod-shib2 \
	           supervisor
sudo DEBIAN_FRONTEND=noninteractive apt-get -y install mysql-server
curl -sL https://deb.nodesource.com/setup | sudo bash -
sudo apt-get install -y nodejs
sudo su -c "npm install -g bower"
sudo npm install -g less@1.7.5 clean-css requirejs uglify-js bower
sudo pip install -U virtualenvwrapper pip


#
# PRECONFIGURE
#
CFG_LWDAAP_VIRTUALENV=lwdaap
CFG_LWDAAP_REPOSITORY=https://github.com/aeonium/lw-daap.git
CFG_LWDAAP_WORKDIR=$HOME/lwdaap
CFG_LWDAAP_DATABASE_NAME=lwdaap
CFG_LWDAAP_DATABASE_USER=lwdaap
CFG_LWDAAP_DATABASE_HOST=localhost
CFG_LWDAAP_DATABASE_PORT=3306
CFG_LWDAAP_SITE_URL=$1
CFG_LWDAAP_SITE_SECURE_URL=$(echo $1 | sed 's/http/https/')
CFG_LWDAAP_USER=${USER:=$(whoami)}

#
# INSTALL
#
source $(which virtualenvwrapper.sh)
mkvirtualenv $CFG_LWDAAP_VIRTUALENV
git clone $CFG_LWDAAP_REPOSITORY $CFG_LWDAAP_WORKDIR
pushd $CFG_LWDAAP_WORKDIR
pip install -r requirements.txt --exists-action i
pip install -e .

#
# INVENIO CONFIG
# Invenio configuration values:
#    http://invenio-software.org/code-browser/invenio.base.config-module.html
#
inveniomanage config create secret-key
CFG_FILE=$(inveniomanage config locate)
cat << EOF >> $CFG_FILE
CFG_EMAIL_BACKEND = u'flask.ext.email.backends.console.Mail'
COLLECT_STORAGE = u'invenio.ext.collect.storage.link'
CFG_BIBSCHED_PROCESS_USER = u'$CFG_LWDAAP_USER'
CFG_DATABASE_HOST = u'$CFG_LWDAAP_DATABASE_HOST'
CFG_DATABASE_PORT = u'$CFG_LWDAAP_DATABASE_PORT'
CFG_DATABASE_NAME = u'$CFG_LWDAAP_DATABASE_NAME'
CFG_DATABASE_USER = u'$CFG_LWDAAP_DATABASE_USER'
CFG_SITE_URL = u'$CFG_LWDAAP_SITE_URL'
CFG_SITE_SECURE_URL = u'$CFG_LWDAAP_SITE_SECURE_URL'
DEBUG = True
DEBUG_TB_ENABLED = False
ASSETS_DEBUG = True
ASSETS_AUTO_BUILD = True
EOF
#
# INSTALL AND COLLECT ASSETS
#
inveniomanage bower -i bower-base.json > bower.json
echo '{"directory": "lw_daap/base/static/vendors"}' > .bowerrc
CI=true bower install
inveniomanage collect

#
# CREATE DATABASE
#
inveniomanage database init --user=root --yes-i-know
inveniomanage database create

#
# CONFIGURE APACHE
#
inveniomanage apache create-config > /dev/null
sudo a2enmod rewrite
sudo a2enmod xsendfile
sudo a2enmod ssl
sudo a2enmod shib2
sudo cp ${VIRTUAL_ENV}/var/invenio.base-instance/apache/invenio-apache-vhost.conf /etc/apache2/sites-available/lwdaap.conf
sudo sed -i '/Listen 80/s/^#//g' /etc/apache2/sites-available/lwdaap.conf
sudo a2dissite *default*
sudo a2ensite lwdaap
sudo cp ${VIRTUAL_ENV}/var/invenio.base-instance/apache/invenio-apache-vhost-ssl.conf /etc/apache2/sites-available/lwdaap-ssl.conf
sudo sed -i '/Listen 443/s/^#//g' /etc/apache2/sites-available/lwdaap-ssl.conf
sudo sed -i 's#^SSLCertificateFile.*#SSLCertificateFile /etc/ssl/certs/ssl-cert-snakeoil.pem#' /etc/apache2/sites-available/lwdaap-ssl.conf
sudo sed -i 's#^\#SSLCertificateKeyFile.*#SSLCertificateKeyFile /etc/ssl/private/ssl-cert-snakeoil.key#' /etc/apache2/sites-available/lwdaap-ssl.conf
# ShibRequireAll not supported on Apache 2.4+: This command is subsumed by Apache 2.4's own support for controlling authorization rule composition.
sudo sed -i 's/^\(.*ShibRequireAll.*\)/#\1/' /etc/apache2/sites-available/lwdaap-ssl.conf
sudo a2ensite lwdaap-ssl
sudo truncate -s 0 /etc/apache2/ports.conf

#
# CELERY
#

cat $CFG_LWDAAP_WORKDIR/deploy/barehost/supervisor/celerybeat.conf \
    sed "s#%VIRTUAL_ENV%#$VIRTUAL_ENV#g" | \
    sed "s#%CFG_LWDAAP_USER%#$CFG_LWDAAP_USER#g" | \
    sudo tee /etc/supervisor/conf.d/celerybeat.conf
cat $CFG_LWDAAP_WORKDIR/deploy/barehost/supervisor/celeryd.conf \
    sed "s#%VIRTUAL_ENV%#$VIRTUAL_ENV#g" | \
    sed "s#%CFG_LWDAAP_USER%#$CFG_LWDAAP_USER#g" | \
    sudo tee /etc/supervisor/conf.d/celeryd.conf
sudo service supervisord start
sudo mkdir -p /var/log/celery
sudo mkdir -p /var/run/celery
sudo chown $USER /var/log/celery
sudo chown $USER /var/run/celery

#
# REDIS
#
sudo service redis-server restart


#
# BIBSCHED
#
cat << EOF > bibsched-run.sh
#!/usr/bin/env bash
bibsched purge
bibsched start
bibindex -s5m -u admin
bibrank -s5m -u admin
bibreformat -s5m -o HB,HD -u admin
bibsort -s5m -u admin
webcoll -s5m -u admin
EOF
chmod +x bibsched-run.sh
./bibsched-run.sh

#
# SOME SOFTLINKS
#
ln -s ${VIRTUAL_ENV}/var/log ./log
ln -s $(inveniomanage config locate 2> /dev/null) ./invenio.cfg
popd

sudo service apache2 restart
echo "INSTALL DONE"
