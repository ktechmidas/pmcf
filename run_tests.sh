#!/bin/bash

ret=0

echo "Running unit tests ..."

mkdir -p testreports

tox -e py27,pep8 || ret=$(($ret|$?))

exit $ret
