#!/bin/bash 

virtualenv -q .venv
tools/with_venv.sh pip install --upgrade 'pip>=1.4'
tools/with_venv.sh pip install --upgrade setuptools
tools/with_venv.sh pip install --upgrade -r ${PWD}/requirements.txt -r ${PWD}/test-requirements.txt

