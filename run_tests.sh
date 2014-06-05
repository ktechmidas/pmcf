#!/bin/bash

set -e

ret=0
force=no
envlist=py27,pep8

do_help() {
	ret="${1:1}"
	read -r -d '' HELP_MESSAGE <<-EOD
$0: setup a python venv for pmcf
Usage: $0 [-f]
	-f	Remove existing venv first
	-h	This help message
EOD
	if [ "$ret" != 0 ]; then
		echo "${HELP_MESSAGE}" >&2
	else
		echo "${HELP_MESSAGE}"
	fi
	exit $ret
}

set -- $(getopt e:fh "$@")
while [ $# -gt 0 ]
do
    case "$1" in
    (-f) force=yes;;
    (-h) do_help 0;;
    (-e) envlist=$2; shift;;
    (--) shift; break;;
    (-*) echo "$0: error - unrecognized option $1" 1>&2; do_help 1;;
    (*)  break;;
    esac
    shift
done

if [ "${force}" = yes ];then
	$(dirname $0)/tools/install_venv.sh -f
	rm -rf .tox coverage testreports
fi

echo "Running unit tests ..."

mkdir -p testreports
tox -e $envlist || ret=$(($ret|$?))

exit $ret
