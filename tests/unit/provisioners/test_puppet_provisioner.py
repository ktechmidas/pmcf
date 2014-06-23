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
            'WaitHandle': 'blah',
            'infrastructure': 'foo.zip',
            'application': 'bar.zip',
        }
        uri = "https://s3.amazonaws.com/cloudformation-examples/"
        script = {
            'Fn::Join': [
                '',
                [
                    '#!/bin/bash\n',
                    'error_exit() {\n',
                    '   cfn-signal -e 1 -r "$1" \'',
                    {'Ref': 'blah'},
                    "'\n",
                    '   exit 1\n',
                    '}\n\n',
                    'err=""\n',
                    'apt-get -y install python-setuptools\n',
                    'easy_install ' + uri,
                    'aws-cfn-bootstrap-latest.tar.gz\n',
                    'cfn-init --region ',
                    {'Ref': 'AWS::Region'},
                    ' -c startup -s ',
                    {'Ref': 'AWS::StackId'},
                    ' -r LCtest',
                    ' || error_exit "Failed to run cfn-init"\n',
                    '\nret=0\n',
                    'for i in `seq 1 5`; do\n',
                    '   puppet apply --modulepath /var/tmp/puppet/modules ',
                    '/var/tmp/puppet/manifests/site.pp\n',
                    '   ret=$?\n',
                    '   test $ret != 0 || break\n',
                    'done\n\n',
                    'if test $ret != 0; then\n',
                    '   err="Failed to run puppet"\n',
                    'fi\n',
                    '\n/srv/apps/bin/deploy deploy test bar.zip\n',
                    'ret=$(($ret|$?))\n',
                    'err="$err Failed to install application"\n',
                    '\nif test "$ret" != 0; then\n',
                    '   sleep 3600\n',
                    '   error_exit "$err"\n',
                    'else\n',
                    "   cfn-signal -e $ret -r Success '",
                    {'Ref': 'blah'},
                    "'\n",
                    'fi\n',
                    'rm -rf /var/tmp/puppet\n'
                ]
            ]
        }
        data = PuppetProvisioner().userdata(args)
        data = json.loads(json.dumps(data, cls=awsencode))
        assert_equals(data, script)

    def test_ci_contains_expected_data(self):
        args = {
            'infrastructure': 'zip.tgz',
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'environment': 'dev',
        }

        ci_data = {
            "AWS::CloudFormation::Init": {
                "bootstrap": {
                    "packages": {
                        "apt": {
                            "puppet": [],
                            "python-boto": [],
                        }
                    }
                },
                "configSets": {
                    "startup": ["bootstrap", "infra"],
                },
                "infra": {
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
                }
            },
            "AWS::CloudFormation::Authentication": {
                "rolebased": {
                    "type": "s3",
                    "buckets": [args['bucket']],
                    "roleName": args['role'],
                }
            }
        }

        data = PuppetProvisioner().cfn_init(args)
        assert_equals(data, ci_data)
