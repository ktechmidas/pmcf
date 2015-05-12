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

import json
import mock
from nose.tools import assert_equals
from troposphere import awsencode

from pmcf.provisioners.ansible import AnsibleProvisioner


def _mock_time():
    return 1000


class TestAnsibleProvisioner(object):
    def test_userdata_contains_expected_data(self):
        args = {
            'name': 'test',
            'stackname': 'test',
            'resource': 'LCtest',
            'WaitHandle': 'blah',
        }
        uri = "https://s3.amazonaws.com/cloudformation-examples/"
        script = {"Fn::Join": ["", [
            "#!/bin/bash\n",
            "error_exit() {\n",
            "   sleep 3600\n",
            "   cfn-signal -e 1 -r \"$1\" '",
            {
                "Ref": "blah"
            },
            "'\n",
            "   exit 1\n",
            "}\n\n",
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
            "apt-get -y install python-setuptools python-pbr python-daemon ",
            "python-pystache\n",
            "easy_install %s" % uri,
            "aws-cfn-bootstrap-latest.tar.gz\n",
            "if cfn-init --region ",
            {
                "Ref": "AWS::Region"
            },
            " -c startup -s ",
            {
                "Ref": "AWS::StackId"
            },
            " -r LCtest",
            "; then\n",
            "cfn-signal -e 0 -r Success '",
            {
                "Ref": "blah"
            },
            "'\n",
            "else\n",
            "    error_exit \"Failed to run cfn-init\"\n",
            "fi\n"
        ]]}
        data = AnsibleProvisioner().userdata(args)
        data = json.loads(json.dumps(data, cls=awsencode))
        assert_equals(data, script)

    @mock.patch('time.time', _mock_time)
    def test_ci_contains_expected_data_custom_facts_ref(self):
        args = {
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'stackname': 'test',
            'appname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
            'custom_facts': {
                'a': 'b',
                'c': '=d',
            }
        }

        ci_data = {
            "AWS::CloudFormation::Authentication": {
                "rolebased": {
                    "roleName": "instance-blah",
                    "buckets": [
                        "testbucket"
                    ],
                    "type": "s3"
                }
            },
            "AWS::CloudFormation::Init": {
                "bootstrap": {
                    "files": {
                        "/etc/ec2_facts.yaml": {
                            "content": {
                                "Fn::Join": [
                                    "",
                                    [
                                        "ec2_stack: ",
                                        {
                                            "Ref": "AWS::StackId"
                                        },
                                        "\n",
                                        "ec2_region: ",
                                        {
                                            "Ref": "AWS::Region"
                                        },
                                        "\n",
                                        "ec2_resource: LCtest\n",
                                        "app: test\n",
                                        "stack: test\n",
                                        "stage: dev\n",
                                        "ansible_playbook: test.yml\n",
                                        "ec2_a: b\n",
                                        "ec2_c: ",
                                        {
                                            "Ref": "d"
                                        },
                                        "\n",
                                    ]
                                ]
                            },
                            "owner": "root",
                            "group": "root",
                            "mode": "000644"
                        },
                        "/etc/ansible/hosts": {
                            "content": "localhost\n",
                            "mode": "000644",
                            "owner": "root",
                            "group": "root"
                        }
                    },
                    "packages": {
                        "apt": {
                            "ansible": [],
                            "python-boto": []
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
                                           args['name'] + ".yml"
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
                                           args['name'] + ".yml"
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
                            "ignoreErrors": "true",
                            "command": "echo 1000"
                        }
                    }
                },
                "configSets": {
                    "startup": [
                        "bootstrap",
                        {
                            "ConfigSet": "ansible"
                        }
                    ],
                    "ansible": [
                        "ansibleLoad",
                        "ansiblePre",
                        "ansibleRun"
                    ]
                }
            }
        }

        data = AnsibleProvisioner().cfn_init(args)
        data = json.loads(json.dumps(data, cls=awsencode))
        assert_equals(data, ci_data)


    @mock.patch('time.time', _mock_time)
    def test_ci_contains_expected_data_custom_facts(self):
        args = {
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'stackname': 'test',
            'appname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
            'custom_facts': {
                'a': 'b',
                'c': 'd',
            }
        }

        ci_data = {
            "AWS::CloudFormation::Authentication": {
                "rolebased": {
                    "roleName": "instance-blah",
                    "buckets": [
                        "testbucket"
                    ],
                    "type": "s3"
                }
            },
            "AWS::CloudFormation::Init": {
                "bootstrap": {
                    "files": {
                        "/etc/ec2_facts.yaml": {
                            "content": {
                                "Fn::Join": [
                                    "",
                                    [
                                        "ec2_stack: ",
                                        {
                                            "Ref": "AWS::StackId"
                                        },
                                        "\n",
                                        "ec2_region: ",
                                        {
                                            "Ref": "AWS::Region"
                                        },
                                        "\n",
                                        "ec2_resource: LCtest\n",
                                        "app: test\n",
                                        "stack: test\n",
                                        "stage: dev\n",
                                        "ansible_playbook: test.yml\n",
                                        "ec2_a: b\n",
                                        "ec2_c: d\n",
                                    ]
                                ]
                            },
                            "owner": "root",
                            "group": "root",
                            "mode": "000644"
                        },
                        "/etc/ansible/hosts": {
                            "content": "localhost\n",
                            "mode": "000644",
                            "owner": "root",
                            "group": "root"
                        }
                    },
                    "packages": {
                        "apt": {
                            "ansible": [],
                            "python-boto": []
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
                                           args['name'] + ".yml"
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
                                           args['name'] + ".yml"
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
                            "ignoreErrors": "true",
                            "command": "echo 1000"
                        }
                    }
                },
                "configSets": {
                    "startup": [
                        "bootstrap",
                        {
                            "ConfigSet": "ansible"
                        }
                    ],
                    "ansible": [
                        "ansibleLoad",
                        "ansiblePre",
                        "ansibleRun"
                    ]
                }
            }
        }

        data = AnsibleProvisioner().cfn_init(args)
        data = json.loads(json.dumps(data, cls=awsencode))
        assert_equals(data, ci_data)

    @mock.patch('time.time', _mock_time)
    def test_ci_contains_expected_data_eip(self):
        args = {
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'stackname': 'test',
            'appname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
            'eip': ['eip-1234', 'eip-2345']
        }

        ci_data = {
            "AWS::CloudFormation::Authentication": {
                "rolebased": {
                    "roleName": "instance-blah",
                    "buckets": [
                        "testbucket"
                    ],
                    "type": "s3"
                }
            },
            "AWS::CloudFormation::Init": {
                "bootstrap": {
                    "files": {
                        "/etc/ec2_facts.yaml": {
                            "content": {
                                "Fn::Join": [
                                    "",
                                    [
                                        "ec2_stack: ",
                                        {
                                            "Ref": "AWS::StackId"
                                        },
                                        "\n",
                                        "ec2_region: ",
                                        {
                                            "Ref": "AWS::Region"
                                        },
                                        "\n",
                                        "ec2_resource: LCtest\n",
                                        "app: test\n",
                                        "stack: test\n",
                                        "stage: dev\n",
                                        "ansible_playbook: test.yml\n",
                                        "ec2_elastic_ips: ",
                                        {
                                            "Ref": "eip-1234"
                                        },
                                        ",",
                                        {
                                            "Ref": "eip-2345"
                                        },
                                        "\n",
                                    ]
                                ]
                            },
                            "owner": "root",
                            "group": "root",
                            "mode": "000644"
                        },
                        "/etc/ansible/hosts": {
                            "content": "localhost\n",
                            "mode": "000644",
                            "owner": "root",
                            "group": "root"
                        }
                    },
                    "packages": {
                        "apt": {
                            "ansible": [],
                            "python-boto": []
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
                                           args['name'] + ".yml"
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
                                           args['name'] + ".yml"
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
                            "ignoreErrors": "true",
                            "command": "echo 1000"
                        }
                    }
                },
                "configSets": {
                    "startup": [
                        "bootstrap",
                        {
                            "ConfigSet": "ansible"
                        }
                    ],
                    "ansible": [
                        "ansibleLoad",
                        "ansiblePre",
                        "ansibleRun"
                    ]
                }
            }
        }

        data = AnsibleProvisioner().cfn_init(args)
        data = json.loads(json.dumps(data, cls=awsencode))
        assert_equals(data, ci_data)

    @mock.patch('time.time', _mock_time)
    def test_ci_contains_expected_data(self):
        args = {
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'stackname': 'test',
            'appname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
        }

        ci_data = {
            "AWS::CloudFormation::Authentication": {
                "rolebased": {
                    "type": "s3",
                    "buckets": [
                        "testbucket"
                    ],
                    "roleName": "instance-blah"
                }
            },
            "AWS::CloudFormation::Init": {
                "bootstrap": {
                    "files": {
                        "/etc/ec2_facts.yaml": {
                            "content": {
                                "Fn::Join": [
                                    "",
                                    [
                                        "ec2_stack: ",
                                        {
                                            "Ref": "AWS::StackId"
                                        },
                                        "\n",
                                        "ec2_region: ",
                                        {
                                            "Ref": "AWS::Region"
                                        },
                                        "\n",
                                        "ec2_resource: LCtest\n",
                                        "app: test\n",
                                        "stack: test\n",
                                        "stage: dev\n",
                                        "ansible_playbook: test.yml\n",
                                    ]
                                ]
                            },
                            "owner": "root",
                            "group": "root",
                            "mode": "000644"
                        },
                        "/etc/ansible/hosts": {
                            "content": "localhost\n",
                            "mode": "000644",
                            "owner": "root",
                            "group": "root"
                        }
                    },
                    "packages": {
                        "apt": {
                            "ansible": [],
                            "python-boto": []
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
                                           args['name'] + ".yml"
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
                                           args['name'] + ".yml"
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
                            "ignoreErrors": "true",
                            "command": "echo 1000"
                        }
                    }
                },
                "configSets": {
                    "startup": [
                        "bootstrap",
                        {
                            "ConfigSet": "ansible"
                        }
                    ],
                    "ansible": [
                        "ansibleLoad",
                        "ansiblePre",
                        "ansibleRun"
                    ]
                }
            }
        }

        data = AnsibleProvisioner().cfn_init(args)
        data = json.loads(json.dumps(data, cls=awsencode))
        assert_equals(data, ci_data)

    def test_provisioner_policy_contains_expected_data(self):
        args = {
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'stackname': 'test',
            'appname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
        }
        base = "arn:aws:s3:::%s" % args['bucket']
        pp_data = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject"
                    ],
                    "Resource": [
                        "%s/dev/test.tar.gz" % base
                    ]
                }
            ]
        }
        data = AnsibleProvisioner().provisioner_policy(args)
        assert_equals(data, pp_data)

    def test_provisioner_policy_contains_expected_data_metrics(self):
        args = {
            'role': 'instance-blah',
            'name': 'test',
            'stackname': 'test',
            'appname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
            'metrics': 'true'
        }
        pp_data = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': ['cloudwatch:PutMetricData'],
                    'Effect': 'Allow',
                    'Resource': '*'
                }
            ]
        }
        data = AnsibleProvisioner().provisioner_policy(args)
        assert_equals(data, pp_data)

    def test_provisioner_policy_contains_expected_data_no_artifacts(self):
        args = {
            'role': 'instance-blah',
            'name': 'test',
            'stackname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
        }
        data = AnsibleProvisioner().provisioner_policy(args)
        assert_equals(data, None)

    def test_provisioner_policy_contains_expected_data_eip(self):
        pp_data = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Resource': '*',
                    'Action': [
                        'ec2:AssociateAddress',
                        'ec2:DescribeAddresses'
                    ],
                    'Effect': 'Allow'
                }
            ]
        }
        args = {
            'role': 'instance-blah',
            'name': 'test',
            'appname': 'test',
            'stackname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
            'eip': ['a', 'b'],
        }
        data = AnsibleProvisioner().provisioner_policy(args)
        assert_equals(data, pp_data)

    @mock.patch('time.time', _mock_time)
    def test_ci_contains_expected_data_playbook(self):
        args = {
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'stackname': 'test',
            'appname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
            'playbook': 'custom.yml'
        }

        ci_data = {
            "AWS::CloudFormation::Authentication": {
                "rolebased": {
                    "roleName": "instance-blah",
                    "buckets": [
                        "testbucket"
                    ],
                    "type": "s3"
                }
            },
            "AWS::CloudFormation::Init": {
                "bootstrap": {
                    "files": {
                        "/etc/ec2_facts.yaml": {
                            "content": {
                                "Fn::Join": [
                                    "",
                                    [
                                        "ec2_stack: ",
                                        {
                                            "Ref": "AWS::StackId"
                                        },
                                        "\n",
                                        "ec2_region: ",
                                        {
                                            "Ref": "AWS::Region"
                                        },
                                        "\n",
                                        "ec2_resource: LCtest\n",
                                        "app: test\n",
                                        "stack: test\n",
                                        "stage: dev\n",
                                        "ansible_playbook: custom.yml\n"
                                    ]
                                ]
                            },
                            "owner": "root",
                            "group": "root",
                            "mode": "000644"
                        },
                        "/etc/ansible/hosts": {
                            "content": "localhost\n",
                            "owner": "root",
                            "group": "root",
                            "mode": "000644"
                        }
                    },
                    "packages": {
                        "apt": {
                            "python-boto": [],
                            "ansible": []
                        }
                    }
                },
                "configSets": {
                    "ansible": [
                        "ansibleLoad",
                        "ansiblePre",
                        "ansibleRun"
                    ],
                    "startup": [
                        "bootstrap",
                        {
                            "ConfigSet": "ansible"
                        }
                    ]
                },
                "trigger": {
                    "commands": {
                        "01-echo": {
                            "ignoreErrors": "true",
                            "command": "echo 1000"
                        }
                    }
                },
                "ansibleRun": {
                    "commands": {
                        "01-run_ansible": {
                            "command": "ansible-playbook /var/tmp/ansible-run/custom.yml"
                        },
                        "02-clean_ansible": {
                            "command": "rm -rf /var/tmp/ansible-run"
                        }
                    }
                },
                "ansibleLoad": {
                    "sources": {
                        "/var/tmp/ansible-run": "https://testbucket.s3.amazonaws.com/dev/test.tar.gz"
                    }
                },
                "ansiblePre": {
                    "commands": {
                        "01-run_ansible": {
                            "ignoreErrors": "false",
                            "command": "ansible-playbook --syntax-check /var/tmp/ansible-run/custom.yml"
                        }
                    }
                }
            }
        }

        data = AnsibleProvisioner().cfn_init(args)
        data = json.loads(json.dumps(data, cls=awsencode))
        assert_equals(data, ci_data)

