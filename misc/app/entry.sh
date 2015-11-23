#!/bin/sh


# bibshed stuff
sleep 1m
KEY=$(inveniomanage config get SECRET_KEY)
if [ "x$KEY" = "xchange_me" ]; then
    inveniomanage config create secret_key
    bibsched start
    bibsched purge
    bibindex -s5m -u admin --continue-on-error
    bibindex -s5m -u admin -w global --continue-on-error
    bibrank -s5m -u admin --continue-on-error
    bibsort -s5m -u admin --continue-on-error
    webcoll -s5m -u admin --continue-on-error
fi


exec "$@"
