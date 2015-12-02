#!/bin/sh

sleep 1m
# call specific script for bibsched
/lwosf/deploy/app/bibsched.sh

KEY=$(inveniomanage config get SECRET_KEY)
if [ "x$KEY" = "xchange_me" ]; then
    inveniomanage config create secret-key
fi

exec "$@"
