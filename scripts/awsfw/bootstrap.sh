#!/bin/bash

set -e
set -u

pip install --upgrade boto

. /tmp/awsfw_vars

/usr/local/lib/s3curl.pl --id ${AWS_ACCESS_KEY_ID} --key ${AWS_SECRET_ACCESS_KEY} -- -o /usr/local/bin/awsfw_dns.py https://aws-c4-003358414754.s3.amazonaws.com/bootstrap/awsfw_dns.py
/usr/local/lib/s3curl.pl --id ${AWS_ACCESS_KEY_ID} --key ${AWS_SECRET_ACCESS_KEY} -- -o /etc/init.d/awsfw_dns https://aws-c4-003358414754.s3.amazonaws.com/bootstrap/awsfw_dns.initd
/usr/local/lib/s3curl.pl --id ${AWS_ACCESS_KEY_ID} --key ${AWS_SECRET_ACCESS_KEY} -- -o /tmp/awsfw_standalone https://aws-c4-003358414754.s3.amazonaws.com/bootstrap/awsfw_standalone

chmod 0400 /tmp/awsfw_vars
chmod 0750 /tmp/awsfw_standalone
chmod 0750 /usr/local/bin/awsfw_dns.py
chmod 0750 /etc/init.d/awsfw_dns

update-rc.d awsfw_dns defaults

nsname=$(/etc/init.d/awsfw_dns start 2>/dev/null)
echo $nsname | egrep -q "${name}.*\.${stackname}-${version}"
shortname=$(echo $nsname|cut -d. -f1)
domainname=$(echo $nsname|cut -d. -f2-)

echo $shortname > /etc/hostname
hostname $shortname

cat << EOF >> /etc/dhcp/dhclient.conf
interface "eth0" {
    supersede domain-name "${domainname}";
}
EOF

/etc/init.d/networking force-reload

/tmp/awsfw_standalone
