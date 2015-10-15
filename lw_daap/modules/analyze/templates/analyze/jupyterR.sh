#!/bin/sh
# This file is part of Lifewatch DAAP.
# Copyright (C) 2015 Ana Yaiza Rodriguez Marrero.
#
# Lifewatch DAAP is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lifewatch DAAP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lifewatch DAAP. If not, see <http://www.gnu.org/licenses/>.

export DEBIAN_FRONTEND=noninteractive
echo "deb http://cran.rstudio.com/bin/linux/ubuntu trusty/" > /etc/apt/sources.list.d/cran
apt-get update
apt-get -y install build-essential python3-dev python3-pip python-virtualenv libzmq3-dev r-base
useradd -m jup

R_INSTALLER=`mktemp`
cat > $R_INSTALLER << EOF
dir.create(Sys.getenv("R_LIBS_USER"), showWarnings = FALSE, recursive = TRUE)
install.packages(c('rzmq','repr','IRkernel','IRdisplay'),
                 repos = c('http://cran.es.r-project.org/', 'http://irkernel.github.io/', getOption('repos')),
                 type = 'source')
IRkernel::installspec()
EOF

JUP_INSTALLER=`mktemp`
cat > $JUP_INSTALLER << EOF
unset XDG_RUNTIME_DIR
unset XDG_SESSION_ID

virtualenv --python=python3 .jupyter_venv
. .jupyter_venv/bin/activate
pip3 install jupyter
jupyter notebook --generate-config
CONFIG_FILE=\`jupyter --config-dir\`/jupyter_notebook_config.py

ID=\$(curl http://169.254.169.254/openstack/latest/meta_data.json | \
     python2 -c "import json; import sys; print json.load(sys.stdin)['uuid']")
echo "c.NotebookApp.base_url = '/\$ID'" >> \$CONFIG_FILE

mkdir ~/.R
cat > ~/.R/Makeconf << COF
CXX1X = g++ 
CXX1XSTD = -std=c++11
SHLIB_CXX1XLD = \$(CXX1X) \$(CXX1XSTD)
CXX1XPICFLAGS = -fpic
SHLIB_CXX1XLDFLAGS = -shared
COF

Rscript $R_INSTALLER 

jupyter notebook --no-browser --ip=0.0.0.0 &
EOF

chmod 755 $JUP_INSTALLER

su - jup -c $JUP_INSTALLER
