#!/usr/bin/env bash
bibsched purge
bibsched start
bibindex -s5m -u admin
bibrank -s5m -u admin
bibreformat -s5m -o HB,HD -u admin
bibsort -s5m -u admin
webcoll -s5m -u admin
