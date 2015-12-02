#!/bin/bash

check_bibsched_task () {
    bibsched status -t $1 -q | \
         egrep "(Running|Waiting) processes" | \
         cut -b44 | grep -v 0 > /dev/null
    return $?
}

bibsched status 2>&1 > /dev/null
st=$?

if [ $st -eq 0 ]; then
    bibsched status | grep "BibSched daemon status" | grep "UP" > /dev/null \
        || bibsched start

    bibsched purge

    check_bibsched_task bibindex || \
        (bibindex -s5m -u admin --continue-on-error;
         bibindex -s5m -u admin -w global --continue-on-error)

    for proc in bibrank bibsort webcoll; do
        check_bibsched_task $proc || $proc -s5m -u admin --continue-on-error
    done
fi
