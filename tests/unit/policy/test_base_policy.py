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

from nose.tools import assert_equals, assert_raises

from pmcf.exceptions import PolicyException
from pmcf.policy import BasePolicy


class TestBasePolicy(object):

    def test_policy_file_load(self):
        policy = BasePolicy()
        assert_equals(policy.json_policy, {})

    def test_return_on_no_policy(self):
        policy = BasePolicy()
        assert_equals(True, policy.validate_resource('wombat', {}))

    def test_instance_policy_violation(self):
        data = {
            "count": "6",
            "monitoring": "false",
            "name": "ais-stage-v2p54-02-app",
            "provisioner": {
                "args": {
                    "roleBucket": "aws-c4-003358414754",
                    "appBucket": "aws-c4-003358414754",
                    "apps": [
                        "ais-jetty/v2.54-02",
                        "ais-nginx/v1.23",
                        "c4-devaccess"
                    ],
                    "roles": [
                        "jetty",
                        "nginx-latest/v1.5",
                        "nagiosclient/v1.5",
                        "snmpd/v1.2",
                        "cloudwatch-monitoring/v1"
                    ]
                },
                "name": "awsfw_standalone"
            },
            "sg": [
                "ais-stage-v2p54-02-app"
            ],
            "image": "ami-e97f849e",
            "type": "m2.xlarge",
            "sshKey": "ioko-pml"
        }

        policy = BasePolicy(json_file='etc/policy-instance.json')
        assert_raises(PolicyException,
                      policy.validate_resource, 'instance', data)

    def test_instance_load_default(self):
        data = {
            "count": "6",
            "monitoring": "false",
            "name": "ais-stage-v2p54-02-app",
            "provisioner": {
                "args": {
                    "roleBucket": "aws-c4-003358414754",
                    "appBucket": "aws-c4-003358414754",
                    "apps": [
                        "ais-jetty/v2.54-02",
                        "ais-nginx/v1.23",
                        "c4-devaccess"
                    ],
                    "roles": [
                        "jetty",
                        "nginx-latest/v1.5",
                        "nagiosclient/v1.5",
                        "snmpd/v1.2",
                        "cloudwatch-monitoring/v1"
                    ]
                },
                "name": "awsfw_standalone"
            },
            "sg": [
                "ais-stage-v2p54-02-app"
            ],
            "sshKey": "ioko-pml"
        }

        policy = BasePolicy(json_file='etc/policy-instance.json')
        policy.validate_resource('instance', data)
        assert_equals(data['type'], 'm1.medium')
