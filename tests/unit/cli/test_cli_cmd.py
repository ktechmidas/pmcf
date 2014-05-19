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

from pmcf.cli.cmd import PMCFCLI
from pmcf.exceptions import PropertyException


class TestCliCmd(object):

    def test_valid_config_succeeds(self):
        options = {
            'parser': 'AWSFWParser',
            'policy': 'JSONPolicy',
            'policyfile': 'tests/data/etc/policy.json',
            'provisioner': 'AWSFWProvisioner',
            'output': 'JSONOutput',
            'verbose': False
        }
        cli = PMCFCLI(options)
        assert_equals(cli.args['policyfile'], 'tests/data/etc/policy.json')

    def test_invalid_config_raises(self):
        options = {
            'parser': 'THISDOESNOTEXIST',
            'policy': 'JSONPolicy',
            'policyfile': 'tests/data/etc/policy.json',
            'provisioner': 'AWSFWProvisioner',
            'output': 'JSONOutput',
            'verbose': False
        }
        assert_raises(PropertyException, PMCFCLI, options)

    def test_valid_config_run_succeeds(self):
        options = {
            'parser': 'AWSFWParser',
            'policy': 'JSONPolicy',
            'policyfile': 'tests/data/etc/policy.json',
            'provisioner': 'AWSFWProvisioner',
            'output': 'JSONOutput',
            'verbose': False,
            'stackfile': 'tests/data/awsfw/ais-stage-farm.xml',
        }
        cli = PMCFCLI(options)
        assert_equals(False, cli.run())

    def test_invalid_config_run_fails(self):
        options = {
            'parser': 'AWSFWParser',
            'policy': 'JSONPolicy',
            'policyfile': 'tests/data/etc/policy-instance.json',
            'provisioner': 'AWSFWProvisioner',
            'output': 'JSONOutput',
            'verbose': False,
            'stackfile': 'tests/data/awsfw/ais-stage-farm.xml',
        }
        cli = PMCFCLI(options)
        assert_equals(True, cli.run())
