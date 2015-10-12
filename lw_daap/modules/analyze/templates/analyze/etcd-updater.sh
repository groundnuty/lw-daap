#!/bin/sh
#
# This script will just send to the etcd a heads-up
# from the node. Should be added to a cron or similar
#

ETCD_URL="{{ etcd_url }}"
TTL="{{ ttl }}"
ROOT="{{ root }}"

# get id and IP from meta-data
ID=$(curl http://169.254.169.254/openstack/latest/meta_data.json | \
     python2 -c "import json; import sys; print json.load(sys.stdin)['uuid']")
IP=$(curl http://169.254.169.254/latest/meta-data/local-ipv4)

# XXX missing AuthN
curl -L $ETCD_URL/v2/keys/$ROOT/$ID -XPUT -d value=$IP -d ttl=$TTL &> /dev/null
