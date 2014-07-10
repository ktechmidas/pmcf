#!/bin/bash

set -e
set -u

. /tmp/awsfw_vars

apt-get install -y python-pip xmlstarlet
pip install awscli

wget -P /usr/local/bin http://stedolan.github.io/jq/download/linux64/jq
chmod a+x /usr/local/bin/jq

apt-get install -y --no-install-recommends libdigest-hmac-perl gdebi
/usr/local/lib/s3curl.pl --id ${AWS_ACCESS_KEY_ID} --key ${AWS_SECRET_ACCESS_KEY} -- -o /tmp/awsfw_dns.sh https://aws-c4-003358414754.s3.amazonaws.com/bootstrap/awsfw_dns.sh
/usr/local/lib/s3curl.pl --id ${AWS_ACCESS_KEY_ID} --key ${AWS_SECRET_ACCESS_KEY} -- -o /tmp/awsfw_standalone https://aws-c4-003358414754.s3.amazonaws.com/bootstrap/awsfw_standalone

[[ -f /tmp/awsfw_vars ]] && chmod 0400 /tmp/awsfw_vars
chmod 0755 /tmp/awsfw_dns.sh
chmod 0755 /tmp/awsfw_standalone

/tmp/awsfw_dns.sh
exec /tmp/awsfw_standalone -d
