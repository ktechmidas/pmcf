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
    :synopsis: module containing puppet provisioner class

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import logging
from troposphere import Join, Ref

from pmcf.provisioners.base_provisioner import BaseProvisioner

LOG = logging.getLogger(__name__)


class PuppetProvisioner(BaseProvisioner):

    def wants_profile(self):
        """
        Whether a provisioner implementation wants a profile to be created

        :returns: boolean.
        """

        return True

    def wants_wait(self):
        """
        Whether a provisioner implementation wants a wait condition created

        :returns: boolean.
        """

        return True

    def userdata(self, args):
        """
        Validates resource against local policy.

        :param args: provisioner arguments
        :type args: dict.
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        :returns: str.
        """

        script = [
            '#!/bin/bash\n',
            'error_exit() {\n',
            '   cfn-signal -e 1 -r "$1" \'',
            Ref(args['WaitHandle']),
            '\'\n',
            '   exit 1\n',
            '}\n\n',
            'err=""\n',
            'apt-get -y install python-setuptools\n',
            'easy_install https://s3.amazonaws.com/cloudformation-examples/',
            'aws-cfn-bootstrap-latest.tar.gz\n',
            'cfn-init --region ',
            Ref("AWS::Region"),
            ' -c startup -s ',
            Ref("AWS::StackId"),
            ' -r LC%s' % args['name'],
            ' || error_exit "Failed to run cfn-init"\n',
            '\nret=0\n',
        ]

        if args.get('infrastructure'):
            script.extend([
                'for i in `seq 1 5`; do\n',
                '   puppet apply --modulepath /var/tmp/puppet/modules ',
                '/var/tmp/puppet/manifests/site.pp\n',
                '   ret=$?\n',
                '   test $ret != 0 || break\n',
                'done\n\n',
                'if test $ret != 0; then\n',
                '   err="Failed to run puppet"\n',
                'fi\n',
            ])

        if args.get('application'):
            script.extend([
                '\n/srv/apps/bin/deploy deploy %s %s\n' % (
                    args['name'],
                    args['application']
                ),
                'ret=$(($ret|$?))\n',
                'err="$err Failed to install application"\n',
            ])

        script.extend([
            '\nif test "$ret" != 0; then\n',
            '   sleep 3600\n',
            '   error_exit "$err"\n',
            'else\n',
            '   cfn-signal -e $ret -r Success \'',
            Ref(args['WaitHandle']),
            "'\n",
            'fi\n',
            'rm -rf /var/tmp/puppet\n',
        ])

        return Join('', script)

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

        init = {
            "configSets": {
                "startup": ["bootstrap"]
            },
            "bootstrap": {
                "packages": {
                    "apt": {
                        "puppet": [],
                        "python-boto": [],
                    }
                }
            }
        }
        ret = {
            "AWS::CloudFormation::Authentication": {
                "rolebased": {
                    "type": "s3",
                    "buckets": [args['bucket']],
                    "roleName": args['role']
                }
            }
        }

        if args.get('infrastructure'):
            init['configSets']['startup'].append('infra')
            init['infra'] = {
                "sources": {
                    "/var/tmp/puppet": "https://%s.%s/%s/%s/%s/%s/%s" % (
                        args['bucket'],
                        "s3.amazonaws.com",
                        "artifacts",
                        "infrastructure",
                        args['name'],
                        args['environment'],
                        args['infrastructure']
                    )
                }
            }

        ret["AWS::CloudFormation::Init"] = init
        return ret


__all__ = [
    PuppetProvisioner,
]
