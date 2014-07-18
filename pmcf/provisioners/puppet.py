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
import time
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

    def provisioner_policy(self, args):
        """
        Policy that a provisioner needs for an instance.  Not called unless
        wants_profile() returns True.

        :param args: provisioner arguments
        :type args: dict.
        :returns: None or dict.
        """
        s3_res = []
        if args.get('infrastructure'):
            s3_res.append("arn:aws:s3:::%s/artifacts/%s/%s/%s/%s" % (
                args['bucket'],
                "infrastructure",
                args['stackname'],
                args['environment'],
                args['infrastructure']
            ))
            s3_res.append("arn:aws:s3:::%s/artifacts/%s/%s" % (
                args['bucket'],
                "infrastructure",
                "hiera.tar.gz"
            ))
        if args.get('application'):
            s3_res.append("arn:aws:s3:::%s/artifacts/%s/%s/%s/%s" % (
                args['bucket'],
                "application",
                args['stackname'],
                args['environment'],
                args['application']
            ))
        if len(s3_res) > 0:
            return {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": ["s3:GetObject"],
                    "Resource": s3_res,
                }]
            }
        return None

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
                            "stack: %s\n" % args['stackname'],
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
            init['configSets']['infraUpdate'] = [
                'infraLoad',
                'infraPuppetRun',
                'infraPuppetFinal',
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
                        args['stackname'],
                        args['environment'],
                        args['infrastructure']
                    )
                }
            }
            init['trigger'] = {
                "commands": {
                    "01-echo": {
                        "command": "echo %d" % time.time(),
                        "ignoreErrors": "true",
                    }
                }
            }
            init['infraPuppetRun'] = {
                "commands": {
                    "01-run_puppet": {
                        "command": "puppet apply --modulepath " +
                                   "/var/tmp/puppet/modules " +
                                   "--environment first_run " +
                                   "--logdest syslog " +
                                   "/var/tmp/puppet/manifests/site.pp",
                        "ignoreErrors": "true",
                    }
                }
            }
            init['configSets']['puppetFinal'] = [
                'infraPuppetFinal',
            ]
            init['infraPuppetFinal'] = {
                "commands": {
                    "01-run_puppet": {
                        "command": "puppet apply --modulepath " +
                                   "/var/tmp/puppet/modules " +
                                   "--logdest syslog --detailed-exitcodes " +
                                   "/var/tmp/puppet/manifests/site.pp",
                    },
                    "02-clean_puppet": {
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
                            args['stackname'],
                            args['application'],
                            args['environment'],
                        )
                    }
                }
            }
        if args.get('infrastructure'):
            init['configSets']['startup'].append({"ConfigSet": "puppetFinal"})

        ret["AWS::CloudFormation::Init"] = init
        return ret


__all__ = [
    PuppetProvisioner,
]
