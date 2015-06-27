#!/bin/bash 

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

force=no
set -- $(getopt fh "$@")
while [ $# -gt 0 ]
do
    case "$1" in
    (-f) force=yes;;
    (-h) do_help 0;;
    (--) shift; break;;
    (-*) echo "$0: error - unrecognized option $1" 1>&2; do_help 1;;
    (*)  break;;
    esac
    shift
done

if [ "${force}" = yes ];then
	rmvirtualenv pmcf
	rm -rf doc/build
fi

mkvirtualenv pmcf
workon pmcf
python setup.py install
