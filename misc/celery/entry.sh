#!/bin/sh

#
# Create an initial proxy
#
VO=$(inveniomanage config get CFG_DELEGATION_VO)
PROXY_FILE=$(inveniomanage config get CFG_LWDAAP_ROBOT_PROXY)

voms-proxy-init --voms $VO --rfc --out  $PROXY_FILE


#
# execute celery (or whatever comes)
#
exec "$@"
