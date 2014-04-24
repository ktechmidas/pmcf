#!/bin/bash

echo "Running unit tests ..."
nosetests -v

echo "Running pep8 tests ..."
pep8 pmcf
pep8 tests
