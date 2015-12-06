#!/bin/bash

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

RECID="{{ recid }}"
BASE_URL="{{ config.CFG_SITE_SECURE_URL }}"
TOKEN="{{ token.access_token }}"
ACCESS_TOKEN="?access_token=$TOKEN"
FILE_LIST_REQUEST="{{ url_for('recordfileslistresource', recid=recid) }}"

LW_USER=jupyter
USER_DIR=/home/jupyter

mkdir -p $USER_DIR

URL_NAMES=$(curl -kLs $BASE_URL$FILE_LIST_REQUEST$ACCESS_TOKEN | \
    python -c 'import json,sys;\
               obj=json.loads(sys.stdin.read());\
               print("\n".join("%s;%s" % (f["url"], f["name"]) for f in obj));')

for URL_NAME in $URL_NAMES; do
    FILE_REQUEST=$(echo $URL_NAME | cut -f1 -d";")
    FILE_NAME=$(echo $URL_NAME | cut -f2 -d";")
    curl -kLs $BASE_URL$FILE_REQUEST$ACCESS_TOKEN > $USER_DIR/$FILE_NAME
done

chown -R $LW_USER $USER_DIR
