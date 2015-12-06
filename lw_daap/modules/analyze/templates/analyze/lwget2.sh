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

RECID=$1
TOKEN=$2
DOMAIN="https://daap-prod.aeonium.eu"
ACCESS_TOKEN="?access_token=$TOKEN"
BASE_REQUEST="/api/analysis_files/$RECID$ACCESS_TOKEN"


REQUEST=$(curl -kLs $DOMAIN$BASE_REQUEST)
URLS=$(echo $REQUEST | \
    python -c 'import json,sys;obj=json.loads(sys.stdin.read());print("\n".join(f["url"] for f in obj));')
NAMES=$(echo $REQUEST | \
    python -c 'import json,sys;obj=json.loads(sys.stdin.read());print("\n".join(f["name"] for f in obj));')

IFS=$'\n' read -rd '' -a ARR_URLS <<< "$URLS"
IFS=$'\n' read -rd '' -a ARR_NAMES <<< "$NAMES"

IDX=0
for i in "${ARR_URLS[@]}"; do
    wget --no-check-certificate -O ${ARR_NAMES[$IDX]} $DOMAIN$i$ACCESS_TOKEN > /dev/null
    let "IDX++"
done

