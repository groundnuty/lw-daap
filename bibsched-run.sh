#!/usr/bin/env bash
bibsched stop
bibsched start
bibsched purge 
bibindex -s5m -u admin --continue-on-error
bibrank -s5m -u admin --continue-on-error
bibsort -s5m -u admin --continue-on-error
webcoll -s5m -u admin --continue-on-error
