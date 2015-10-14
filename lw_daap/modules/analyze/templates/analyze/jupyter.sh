#!/bin/sh

export DEBIAN_FRONTEND=noninteractive
apt-get -y install build-essential python3-dev python3-pip python-virtualenv libzmq3-dev
useradd -m jup

JUP_INSTALLER=`mktemp`
cat > $JUP_INSTALLER << EOF
unset XDG_RUNTIME_DIR
unset XDG_SESSION_ID

virtualenv --python=python3 jupyter
. jupyter/bin/activate
pip3 install jupyter
jupyter notebook --generate-config
CONFIG_FILE=\`jupyter --config-dir\`/jupyter_notebook_config.py

ID=\$(curl http://169.254.169.254/openstack/latest/meta_data.json | \
     python2 -c "import json; import sys; print json.load(sys.stdin)['uuid']")
echo "c.NotebookApp.base_url = '/\$ID'" >> \$CONFIG_FILE

jupyter notebook --no-browser --ip=0.0.0.0 &
EOF

chmod 755 $JUP_INSTALLER

su - jup -c $JUP_INSTALLER
