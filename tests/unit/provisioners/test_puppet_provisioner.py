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
from nose.tools import assert_equals
from troposphere import awsencode

from pmcf.provisioners.puppet import PuppetProvisioner


class TestPuppetProvisioner(object):
    def test_userdata_contains_expected_data(self):
        args = {
            'name': 'test',
            'resource': 'LCtest',
            'WaitHandle': 'blah',
            'infrastructure': 'foo.zip',
        }
        uri = "https://s3.amazonaws.com/cloudformation-examples/"

        script = {
            "Fn::Join": [
                "",
                [
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
                    "err=\"\"\n",
                    "apt-get -y install python-setuptools\n",
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
                ]
            ]
        }
        data = PuppetProvisioner().userdata(args)
        data = json.loads(json.dumps(data, cls=awsencode))
        assert_equals(data, script)

    def test_ci_contains_expected_data(self):
        args = {
            'infrastructure': 'zip.tgz',
            'application': 'bar.zip',
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
        }

        ci_data = {
            "AWS::CloudFormation::Authentication": {
                "rolebased": {
                    "type": "s3",
                    "buckets": [args['bucket']],
                    "roleName": args['role'],
                }
            },
            "AWS::CloudFormation::Init": {
                "bootstrap": {
                    "packages": {
                        "apt": {
                            "python-boto": [],
                            "puppet": []
                        }
                    },
                    "files": {
                        "/etc/facter/facts.d/localfacts.yaml": {
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
                                        "stage: dev\n"
                                    ]
                                ]
                            },
                            "owner": "root",
                            "group": "root",
                            "mode": "000644"
                        }
                    },
                },
                "infraLoad": {
                    "sources": {
                        "/var/tmp/puppet":
                            "https://%s.%s/artifacts/%s/%s/%s/%s" % (
                                args['bucket'],
                                "s3.amazonaws.com",
                                "infrastructure",
                                "test",
                                "dev",
                                args['infrastructure'],
                            ),
                        "/etc/puppet":
                            "https://%s.%s/artifacts/%s/%s" % (
                                args['bucket'],
                                "s3.amazonaws.com",
                                "infrastructure",
                                'hiera.tar.gz',
                            ),
                    }
                },
                "infraPuppetRun": {
                    "commands": {
                        "01-run_puppet": {
                            "command": "puppet apply --modulepath "
                                       "/var/tmp/puppet/modules "
                                       "--logdest syslog " +
                                       "/var/tmp/puppet/manifests/site.pp",
                            "ignoreErrors": "true",
                        },
                    }
                },
                "infraPuppetFinal": {
                    "commands": {
                        "01-run_puppet": {
                            "command": "puppet apply --modulepath "
                                       "/var/tmp/puppet/modules "
                                       "--logdest syslog " +
                                       "--detailed-exitcodes " +
                                       "/var/tmp/puppet/manifests/site.pp",
                        },
                        "02-clean_puppet": {
                            "command": "rm -rf /var/tmp/puppet"
                        }
                    }
                },
                "deployRun": {
                    "commands": {
                        "01-run_deploy": {
                            "command": "/srv/apps/bin/deploy %s %s %s %s" % (
                                "deploy",
                                args['name'],
                                args['application'],
                                args['environment'],
                            )
                        }
                    }
                },
                "configSets": {
                    "app": [
                        "deployRun"
                    ],
                    "startup": [
                        "bootstrap",
                        {
                            "ConfigSet": "infra"
                        },
                        {
                            "ConfigSet": "app"
                        },
                        {
                            "ConfigSet": "puppetFinal"
                        }
                    ],
                    "puppetFinal": [
                        "infraPuppetFinal"
                    ],
                    "infraUpdate": [
                        "infraLoad",
                        "infraPuppetRun",
                        "infraPuppetFinal"
                    ],
                    "infra": [
                        "infraLoad",
                        "infraPuppetRun"
                    ]
                }
            }
        }

        data = PuppetProvisioner().cfn_init(args)
        data = json.loads(json.dumps(data, cls=awsencode))
        assert_equals(data, ci_data)

    def test_provisioner_policy_contains_expected_data(self):
        args = {
            'infrastructure': 'zip.tgz',
            'application': 'bar.zip',
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
        }
        base = "arn:aws:s3:::%s/artifacts" % args['bucket']
        pp_data = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject"
                    ],
                    "Resource": [
                        "%s/infrastructure/test/dev/zip.tgz" % base,
                        "%s/infrastructure/hiera.tar.gz" % base,
                        "%s/application/test/dev/bar.zip" % base
                    ]
                }
            ]
        }
        data = PuppetProvisioner().provisioner_policy(args)
        assert_equals(data, pp_data)

    def test_provisioner_policy_contains_expected_data_no_artifacts(self):
        args = {
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
        }
        data = PuppetProvisioner().provisioner_policy(args)
        assert_equals(data, None)
