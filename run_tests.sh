#!/bin/bash

ret=0

tools_path=${tools_path:-$(dirname $0)/tools}
venv_path=${venv_path:-${tools_path}}
venv_dir=${venv_name:-/../.venv}
TOOLS=${tools_path}
VENV=${venv:-${venv_path}/${venv_dir}}

test -d ${VENV} || ${TOOLS}/install_venv.sh

source ${VENV}/bin/activate

echo "Running unit tests ..."

mkdir -p testreports

nosetests "$@" || ret=$(($ret|$?))


echo "Running pep8 tests ..."
pep8 --show-source pmcf || ret=$(($ret|$?))
pep8 --show-source tests || ret=$(($ret|$?))

exit $ret
