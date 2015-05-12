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
..  module:: pmcf.provisioners.ansible
    :platform: Unix
    :synopsis: module containing ansible provisioner class

..  moduleauthor:: Mark Bradley <mark.bradley@piksel.com>
"""

import logging
import time
from troposphere import Join, Ref

from pmcf.provisioners.base_provisioner import BaseProvisioner

LOG = logging.getLogger(__name__)


class AnsibleProvisioner(BaseProvisioner):
    """
    Ansible Provisioner class

    This class assembles userdata suitable for use by cloud-init, and provides
    methods to boot strap an ansible-playbook run.
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
        if args.get('bucket'):
            s3_res.append("arn:aws:s3:::%s/%s/%s.tar.gz" % (
                args['bucket'],
                args['environment'],
                args['stackname']
            ))
        if len(s3_res) > 0:
            statement['Statement'].append({
                "Effect": "Allow",
                "Action": ["s3:GetObject"],
                "Resource": s3_res,
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
            '#!/bin/bash\n',
            'error_exit() {\n',
            '   sleep 3600\n',
            '   cfn-signal -e 1 -r "$1" \'',
            Ref(args['WaitHandle']),
            '\'\n',
            '   exit 1\n',
            '}\n\n',
            'setup_disks() {\n',
            '    ret=0\n',
            '    disks=$(ls /dev/xvd[b-z] 2>/dev/null)\n',
            '    if test -n "${disks}"; then\n',
            '        apt-get install -y lvm2 || ret=$?\n',
            '        umount /mnt\n',
            '        pvcreate ${disks} || ret=$(($ret|$?))\n',
            '        vgcreate data ${disks} || ret=$(($ret|$?))\n',
            '        extents=$(vgs --noheadings -o vg_free_count) || ',
            'ret=$(($ret|$?))\n',
            '        lvcreate -l ${extents} -n mnt data || ret=$(($ret|$?))\n',
            '        mkfs.ext4 -m 1 /dev/data/mnt || ret=$(($ret|$?))\n',
            '        grep -q xvdb /etc/fstab || echo -en ',
            '"/dev/xvdb\t/mnt\tauto\tdefaults,nobootwait,',
            'comment=cloudconfig\t0\t2\n" >> /etc/fstab\n',
            '        sed -i "s~xvdb~data/mnt~" /etc/fstab || ',
            'ret=$(($ret|$?))\n',
            '        mount -a || ret=$(($ret|$?))\n',
            '    fi\n',
            '    return $ret\n',
            '}\n\n',
            'setup_disks || error_exit "Failed to setup disks"\n',
            'apt-get -y install python-setuptools python-pbr python-daemon ',
            'python-pystache\n',
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

        if args.get('playbook'):
            ansibletarget = args['playbook']
        else:
            ansibletarget = args.get('name') + ".yml"

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
            "ansible_playbook: %s\n" % ansibletarget,
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
                "startup": ["bootstrap", {"ConfigSet": "ansible"}],
                "ansible": ["ansibleLoad", "ansiblePre", "ansibleRun"],
            },
            "bootstrap": {
                "packages": {
                    "apt": {
                        "ansible": [],
                        "python-boto": [],
                    }
                },
                "files": {
                    "/etc/ec2_facts.yaml": {
                        "content": Join("", facts),
                        "mode": "000644",
                        "owner": "root",
                        "group": "root"
                    },
                    "/etc/ansible/hosts": {
                        "content": "localhost\n",
                        "mode": "000644",
                        "owner": "root",
                        "group": "root"
                    }
                }
            },
            "ansibleLoad": {
                "sources": {
                    "/var/tmp/ansible-run": "https://%s.%s/%s/%s.tar.gz" % (
                        args['bucket'],
                        "s3.amazonaws.com",
                        args['environment'],
                        args['stackname']
                    )
                }
            },
            "ansiblePre": {
                "commands": {
                    "01-run_ansible": {
                        "command": "ansible-playbook --syntax-check " +
                                   "/var/tmp/ansible-run/%s" % (
                                       ansibletarget
                                   ),
                        "ignoreErrors": "false",
                    }
                }
            },
            "ansibleRun": {
                "commands": {
                    "01-run_ansible": {
                        "command": "ansible-playbook " +
                                   "/var/tmp/ansible-run/%s" % (
                                       ansibletarget
                                   ),
                    },
                    "02-clean_ansible": {
                        "command": "rm -rf /var/tmp/ansible-run"
                    }
                }
            },
            "trigger": {
                "commands": {
                    "01-echo": {
                        "command": "echo %d" % time.time(),
                        "ignoreErrors": "true",
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
            },
            "AWS::CloudFormation::Init": init
        }

        return ret


__all__ = [
    AnsibleProvisioner,
]
