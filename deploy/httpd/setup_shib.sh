#!/bin/sh

if [ -f /etc/ssl/certs/ssl-cert.pem ]; then
    cp /etc/ssl/certs/ssl-cert.pem /etc/shibboleth/sp-cert.pem
    chown _shibd:_shibd /etc/shibboleth/sp-cert.pem
fi

if [ -f /etc/ssl/private/ssl-cert.key ]; then
    cp /etc/ssl/private/ssl-cert.key /etc/shibboleth/sp-key.pem
    chown _shibd:_shibd /etc/shibboleth/sp-key.pem
fi

exec "$@"
