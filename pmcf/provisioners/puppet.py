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
        :returns: str.
        """

        script = [
            '#!/bin/bash\n',
            'error_exit() {\n',
            '   sleep 3600\n',
            '   cfn-signal -e 1 -r "$1" \'',
            Ref(args['WaitHandle']),
            '\'\n',
            '   exit 1\n',
            '}\n\n',
            'err=""\n',
            'apt-get -y install python-setuptools\n',
            'easy_install https://s3.amazonaws.com/cloudformation-examples/',
            'aws-cfn-bootstrap-latest.tar.gz\n',
            'if cfn-init --region ',
            Ref("AWS::Region"),
            ' -c startup -s ',
            Ref("AWS::StackId"),
            ' -r %s' % args['resource'],
            '; then\n',
            'cfn-signal -e 0 -r Success \'',
            Ref(args['WaitHandle']),
            '\'\n',
            'else\n',
            '    error_exit "Failed to run cfn-init"\n',
            'fi\n',
        ]

        return Join('', script)

    def cfn_init(self, args):
        """
        Return metadata suitable for consumption by cfn_init

        :param config: Config items for userdata
        :type config: dict.
        :param args: instance definition
        :type args: dict.
        :returns: dict.
        """

        init = {
            "configSets": {
                "startup": ["bootstrap"],
            },
            "bootstrap": {
                "packages": {
                    "apt": {
                        "puppet": [],
                        "python-boto": [],
                    }
                },
                "files": {
                    "/etc/facter/facts.d/localfacts.yaml": {
                        "content": Join("", [
                            "ec2_stack: ",
                            Ref("AWS::StackId"),
                            "\n",
                            "ec2_region: ",
                            Ref("AWS::Region"),
                            "\n",
                            "ec2_resource: %s\n" % args['resource'],
                            "app: %s\n" % args['name'],
                            "stage: %s\n" % args['environment'],
                        ]),
                        "mode": "000644",
                        "owner": "root",
                        "group": "root"
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
            init['configSets']['infra'] = [
                'infraLoad',
                'infraPuppetRun',
            ]
            init['configSets']['startup'].append({"ConfigSet": "infra"})
            init['infraLoad'] = {
                "sources": {
                    "/etc/puppet": "https://%s.%s/%s/%s/hiera.tar.gz" % (
                        args['bucket'],
                        "s3.amazonaws.com",
                        "artifacts",
                        "infrastructure",
                    ),
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
            init['infraPuppetRun'] = {
                "commands": {
                    "01-run_puppet": {
                        "command": "puppet apply --modulepath " +
                                   "/var/tmp/puppet/modules " +
                                   "--logdest syslog --detailed-exitcodes " +
                                   "/var/tmp/puppet/manifests/site.pp",
                        "ignoreErrors": "true",
                    },
                    "02-run_puppet_again": {
                        "command": "puppet apply --modulepath " +
                                   "/var/tmp/puppet/modules " +
                                   "--logdest syslog --detailed-exitcodes " +
                                   "/var/tmp/puppet/manifests/site.pp",
                    },
                    "03-clean_puppet": {
                        "command": "rm -rf /var/tmp/puppet"
                    }
                }
            }

        if args.get('application'):
            init['configSets']['app'] = [
                'deployRun',
            ]
            init['configSets']['startup'].append({"ConfigSet": "app"})
            init['deployRun'] = {
                "commands": {
                    "01-run_deploy": {
                        "command": "/srv/apps/bin/deploy deploy %s %s %s" % (
                            args['name'],
                            args['environment'],
                            args['application']
                        )
                    }
                }
            }

        ret["AWS::CloudFormation::Init"] = init
        return ret


__all__ = [
    PuppetProvisioner,
]
