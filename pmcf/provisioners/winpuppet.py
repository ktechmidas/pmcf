# Copyright (c) 2015 Piksel
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
..  module:: pmcf.provisioners.winpuppet
    :platform: Unix
    :synopsis: module containing puppet provisioner class for windows hosts

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import logging
import time
from troposphere import Join, Ref, Base64

from pmcf.provisioners.base_provisioner import BaseProvisioner

LOG = logging.getLogger(__name__)


class WindowsPuppetProvisioner(BaseProvisioner):
    """
    Puppet Provisioner class

    This class assembles userdata suitable for use by cloud-init, and provides
    methods to boot strap a puppet run.  Designed for use with the Sequoia
    delivery method on Windows hosts.
    """

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
        statement = {
            "Version": "2012-10-17",
            "Statement": []
        }
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
                "winhiera.tar.gz"
            ))
        if args.get('application'):
            s3_res.append("arn:aws:s3:::%s/artifacts/%s/%s/%s/%s" % (
                args['bucket'],
                "application",
                args['appname'],
                args['environment'],
                args['application']
            ))
        if len(s3_res) > 0:
            statement['Statement'].append({
                "Effect": "Allow",
                "Action": ["s3:GetObject"],
                "Resource": s3_res,
            })
        if args.get('find_nodes'):
            statement['Statement'].append({
                "Effect": "Allow",
                "Action": ["ec2:DescribeInstances"],
                "Resource": "*",
            })
        if args.get('eip'):
            statement['Statement'].append({
                "Effect": "Allow",
                "Action": [
                    "ec2:AssociateAddress",
                    "ec2:DescribeAddresses",
                ],
                "Resource": "*",
            })
        if args.get('metrics'):
            statement['Statement'].append({
                "Effect": "Allow",
                "Action": ["cloudwatch:PutMetricData"],
                "Resource": "*",
            })

        statement['Statement'].extend(args.get('custom_profile', []))

        if len(statement['Statement']) > 0:
            return statement
        return None

    def userdata(self, args):
        """
        Validates resource against local policy.

        :param args: provisioner arguments
        :type args: dict.
        :returns: str.
        """

        script = [
            "<script>\n",
            "cfn-init.exe -v -s ",
            Ref("AWS::StackId"),
            " -r %s -c startup" % args['resource'],
            " --region ",
            Ref("AWS::Region"),
            "\n",
            "cfn-signal.exe -e %ERRORLEVEL% ",
            Base64(Ref(args['WaitHandle'])),
            "\n",
            "</script>"
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

        facts = [
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
        ]
        if args.get('eip'):
            facts.append("ec2_elastic_ips: ")
            for ei in args['eip']:
                facts.append(Ref(ei))
                facts.append(",")
            facts.pop()
            facts.append("\n")

        for k in sorted(args.get('custom_facts', {}).keys()):
            if args['custom_facts'][k].startswith('='):
                facts.append("ec2_%s: " % k)
                facts.append(Ref("%s" % args['custom_facts'][k][1:]))
                facts.append("\n")
            else:
                facts.append("ec2_%s: %s\n" % (k, args['custom_facts'][k]))

        init = {
            "configSets": {
                "startup": ["bootstrap"],
            },
            "bootstrap": {
                "packages": {
                    "msi": {
                        "puppet": "https://%s/windows/puppet-3.7.5-x64.msi" % (
                            'downloads.puppetlabs.com'
                        ),
                    }
                },
                "files": {
                    "c:\\%s\\%s\\facter\\facts.d\\localfacts.yaml" % (
                        "ProgramData",
                        "PuppetLabs",
                    ): {
                        "content": Join("", facts),
                    },
                    "c:\\cfn\\cfn-hup.conf": {
                        "content": Join("", [
                            "[main]\n",
                            "stack=",
                            Ref("AWS::StackId"),
                            "\n",
                            "region=",
                            Ref("AWS::Region"),
                            "\n",
                            "interval=5\n",
                        ]),
                    },
                    "c:\\cfn\\hooks.d\\cfn-auto-reloader.conf": {
                        "content": Join("", [
                            "[cfn-auto-reloader-hook]\n",
                            "triggers=post.update\n",
                            "path=%s.%s.%s.AWS::CloudFormation::Init\n" % (
                                "Resources",
                                args['resource'],
                                "Metadata",
                            ),
                            "action=cfn-init.exe -v -s ",
                            Ref("AWS::StackId"),
                            " -r %s -c infraUpdate" % args['resource'],
                            " --region ",
                            Ref("AWS::Region"), "\n"
                        ]),
                    },
                },
                "commands": {
                    "1-stop-puppet-service": {
                        "command": "sc stop puppet",
                        "waitAfterCompletion": 0,
                    },
                    "2-disable-puppet-service": {
                        "command": "sc config puppet start= disabled",
                        "waitAfterCompletion": 0,
                    },
                },
                "services": {
                    "windows": {
                        "cfn-hup": {
                            "enabled": "true",
                            "ensureRunning": "true",
                            "files": [
                                "c:\\cfn\\cfn-hup.conf",
                                "c:\\cfn\\hooks.d\\cfn-auto-reloader.conf"
                            ]
                        }
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
            pup = "c:\\Program Files\\Puppet Labs\\Puppet\\bin\\puppet.bat"
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
                    "c:\\ProgramData\\PuppetLabs\\puppet\\etc":
                        "https://%s.%s/%s/%s/winhiera.tar.gz" % (
                            args['bucket'],
                            "s3.amazonaws.com",
                            "artifacts",
                            "infrastructure",
                        ),
                    "c:\\Windows\\Temp\\puppet":
                        "https://%s.%s/%s/%s/%s/%s/%s" % (
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
                        "waitAfterCompletion": 0,
                    }
                }
            }
            init['infraPuppetRun'] = {
                "commands": {
                    "01-run_puppet": {
                        "command":
                            "\"%s\" apply --modulepath " % pup +
                            "c:\\Windows\\Temp\\puppet\\modules " +
                            "--environment first_run " +
                            "c:\\Windows\\Temp\\puppet\\manifests\\site.pp",
                        "ignoreErrors": "true",
                        "waitAfterCompletion": 0,
                    }
                }
            }
            init['configSets']['puppetFinal'] = [
                'infraPuppetFinal',
            ]
            init['infraPuppetFinal'] = {
                "commands": {
                    "01-run_puppet": {
                        "command":
                            "\"%s\" apply --modulepath " % pup +
                            "c:\\Windows\\Temp\\puppet\\modules " +
                            "--detailed-exitcodes " +
                            "c:\\Windows\\Temp\\puppet\\manifests\\site.pp",
                        "waitAfterCompletion": 0,
                    },
                    "02-clean_puppet": {
                        "command": "rmdir /S /Q c:\\Windows\\Temp\\puppet",
                        "waitAfterCompletion": 0,
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
                        "waitAfterCompletion": 0,
                        "command":
                            "powershell -NoProfile -NonInteractive" +
                            " -NoLogo -ExecutionPolicy Bypass " +
                            "-Command c:\Piksel\msdeploy.ps1" +
                            " -service %s -stage %s -artifact %s" % (
                                args['appname'],
                                args['environment'],
                                args['application'],
                            )
                    }
                }
            }
        if args.get('infrastructure'):
            init['configSets']['startup'].append({"ConfigSet": "puppetFinal"})

        ret["AWS::CloudFormation::Init"] = init
        return ret


__all__ = [
    WindowsPuppetProvisioner,
]
