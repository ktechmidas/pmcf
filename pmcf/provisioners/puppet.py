# Copyright (c) 2014 Piksel
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
..  module:: pmcf.provisioners.puppet
    :platform: Unix
    :synopsis: module containing puppet implementation of provisioner class

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import logging
from troposphere import Join, Ref

from pmcf.provisioners.base_provisioner import BaseProvisioner

LOG = logging.getLogger(__name__)


class PuppetProvisioner(BaseProvisioner):

    def userdata(self, args):
        """
        Validates resource against local policy.

        :param args: provisioner arguments
        :type args: dict.
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        :returns: str.
        """

        return Join('', [
            "#!/bin/bash\n",
            "error_exit() {\n",
            "  cfn-signal -e 1 -r " + args['name'] + " '",
            Ref(args['WaitHandle']),
            "'\n",
            "  exit 1\n",
            "}\n",
            "apt-get -y install python-setuptools\n",
            "easy_install https://s3.amazonaws.com/cloudformation-examples/",
            "aws-cfn-bootstrap-latest.tar.gz\n",
            "cfn-init --region ",
            Ref("AWS::Region"),
            "-s ",
            Ref("AWS::StackId"),
            " -r " + args['name'],
            " || error_exit 'Failed to run cfn-init'\n",
            "for i in `seq 1 5`; do\n",
            "  puppet apply --modulepath /var/tmp/puppet/modules ",
            "/var/tmp/puppet/manifests/site.pp\n",
            "done\n",
            "cfn-signal -e $? -r " + args['name'] + " '",
            Ref(args['WaitHandle']),
            "'\n",
            "rm -rf /var/tmp/puppet\n",
        ])

    def cfn_init(self, args):
        """
        Return metadata suitable for consumption by cfn_init

        :param config: Config items for userdata
        :type config: dict.
        :param args: instance definition
        :type args: dict.
        :raises: :class:`NotImplementedError`
        :returns: dict.
        """

        return {
            "AWS::CloudFormation::Init": {
                "config": {
                    "packages": {
                        "apt": {
                            "puppet": [],
                        },
                    },
                    "files": {
                        "/var/tmp/puppet/": "https://%s/%s/artifacts/%s" % (
                            "s3.amazonaws.com",
                            args['bucket'],
                            args['artifact']
                        )
                    },
                },
            },
            "AWS::CloudFormation::Authentication": {
                "rolebased": {
                    "type": "s3",
                    "buckets": [args['bucket']],
                    "roleName": args['profile'],
                },
            },
        }


__all__ = [
    PuppetProvisioner,
]
