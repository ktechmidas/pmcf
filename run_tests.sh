#!/bin/bash

ret=0

echo "Running unit tests ..."
nosetests -v --cover-html \
	     --cover-html-dir=coverage --cover-inclusive \
	     --cover-erase || ret=$(($ret|$?))

echo "Running pep8 tests ..."
pep8 --show-source pmcf || ret=$(($ret|$?))
pep8 --show-source tests || ret=$(($ret|$?))

exit $ret
