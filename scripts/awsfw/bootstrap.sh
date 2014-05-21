#!/bin/bash

set -e
set -u

. /tmp/awsfw_vars

apt-get install -y --no-install-recommends libdigest-hmac-perl gdebi
/usr/local/lib/s3curl.pl --id ${AWS_ACCESS_KEY_ID} --key ${AWS_SECRET_ACCESS_KEY} -- -o /tmp/awsfw_standalone https://aws-c4-003358414754.s3.amazonaws.com/bootstrap/awsfw_standalone
chmod 0755 /tmp/awsfw_standalone
exec /tmp/awsfw_standalone
