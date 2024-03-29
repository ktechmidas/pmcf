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

import mock
from nose.tools import assert_equals, assert_raises

from pmcf.cli.cmd import PMCFCLI
from pmcf.exceptions import PropertyException


def _mock_add_resources(self, resource, config):
    return ()


def _mock_cli_init_no_options(self):
    pass


def _mock_cli_init_jsonfile_option(self, json_file):
    pass


def _mock_parse_file(self, fname, args):
    return {
        'resources': {
            'instance': [{}],
            'secgroup': [],
            'load_balancer': [],
            'db': [],
            'cdn': [],
        },
        'config': {
            'name': 'test',
            'owner': 'test',
            'environment': 'test',
            'version': 'test',
        }
    }


def _mock_validate(self):
    pass


def _mock_run_succeeds(self, data, metadata, poll, action):
    return True


def _mock_run_fails(self, data, metadata, poll, action):
    raise PropertyException('test')


class TestCliCmd(object):

    @mock.patch('pmcf.parsers.AWSFWParser.__init__',
                _mock_cli_init_no_options)
    @mock.patch('pmcf.policy.JSONPolicy.__init__',
                _mock_cli_init_jsonfile_option)
    @mock.patch('pmcf.provisioners.AWSFWProvisioner.__init__',
                _mock_cli_init_no_options)
    @mock.patch('pmcf.outputs.JSONOutput.__init__',
                _mock_cli_init_no_options)
    def test_valid_config_succeeds(self):
        options = {
            'parser': 'AWSFWParser',
            'policy': 'JSONPolicy',
            'policyfile': 'tests/data/etc/policy.json',
            'provisioner': 'AWSFWProvisioner',
            'output': 'JSONOutput',
        }
        cli = PMCFCLI(options)
        assert_equals(cli.args['policyfile'], 'tests/data/etc/policy.json')

    @mock.patch('pmcf.policy.JSONPolicy.__init__',
                _mock_cli_init_jsonfile_option)
    @mock.patch('pmcf.provisioners.AWSFWProvisioner.__init__',
                _mock_cli_init_no_options)
    @mock.patch('pmcf.outputs.JSONOutput.__init__',
                _mock_cli_init_no_options)
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

    @mock.patch('pmcf.parsers.awsfw_parser.AWSFWParser.__init__',
                _mock_cli_init_no_options)
    @mock.patch('pmcf.parsers.awsfw_parser.AWSFWParser.validate',
                _mock_validate)
    @mock.patch('pmcf.parsers.awsfw_parser.AWSFWParser.parse_file',
                _mock_parse_file)
    @mock.patch('pmcf.policy.JSONPolicy.__init__',
                _mock_cli_init_jsonfile_option)
    @mock.patch('pmcf.policy.JSONPolicy.validate_resource',
                _mock_parse_file)
    @mock.patch('pmcf.provisioners.AWSFWProvisioner.__init__',
                _mock_cli_init_no_options)
    @mock.patch('pmcf.outputs.JSONOutput.__init__',
                _mock_cli_init_no_options)
    @mock.patch('pmcf.outputs.JSONOutput.add_resources',
                _mock_add_resources)
    @mock.patch('pmcf.outputs.JSONOutput.run',
                _mock_run_succeeds)
    def test_valid_config_run_succeeds(self):
        options = {
            'parser': 'AWSFWParser',
            'policy': 'JSONPolicy',
            'policyfile': 'tests/data/etc/policy.json',
            'provisioner': 'AWSFWProvisioner',
            'output': 'JSONOutput',
            'verbose': False,
            'stackfile': 'tests/data/awsfw/ais-stage-farm.xml',
            'accesskey': '1234',
            'secretkey': '3456',
            'instance_accesskey': '1234',
            'instance_secretkey': '3456',
            'poll': False,
            'region': 'eu-west-1',
            'audit': 'NoopAudit',
            'audit_output': 'foobar',
            'action': 'create',
        }
        cli = PMCFCLI(options)
        assert_equals(False, cli.run())

    @mock.patch('pmcf.parsers.awsfw_parser.AWSFWParser.__init__',
                _mock_cli_init_no_options)
    @mock.patch('pmcf.parsers.awsfw_parser.AWSFWParser.parse_file',
                _mock_parse_file)
    @mock.patch('pmcf.parsers.awsfw_parser.AWSFWParser.validate',
                _mock_validate)
    @mock.patch('pmcf.policy.JSONPolicy.__init__',
                _mock_cli_init_jsonfile_option)
    @mock.patch('pmcf.policy.JSONPolicy.validate_resource',
                _mock_parse_file)
    @mock.patch('pmcf.provisioners.AWSFWProvisioner.__init__',
                _mock_cli_init_no_options)
    @mock.patch('pmcf.outputs.JSONOutput.__init__',
                _mock_cli_init_no_options)
    @mock.patch('pmcf.outputs.JSONOutput.add_resources',
                _mock_add_resources)
    @mock.patch('pmcf.outputs.JSONOutput.run',
                _mock_run_fails)
    def test_invalid_config_keyerror_run_fails(self):
        options = {
            'parser': 'AWSFWParser',
            'policy': 'JSONPolicy',
            'policyfile': 'tests/data/etc/policy-instance.json',
            'provisioner': 'AWSFWProvisioner',
            'output': 'JSONOutput',
            'verbose': False,
            'debug': True,
            'stackfile': 'tests/data/awsfw/ais-stage-farm.xml',
        }
        cli = PMCFCLI(options)
        assert_equals(True, cli.run())

    @mock.patch('pmcf.parsers.awsfw_parser.AWSFWParser.__init__',
                _mock_cli_init_no_options)
    @mock.patch('pmcf.parsers.awsfw_parser.AWSFWParser.parse_file',
                _mock_parse_file)
    @mock.patch('pmcf.parsers.awsfw_parser.AWSFWParser.validate',
                _mock_validate)
    @mock.patch('pmcf.policy.JSONPolicy.__init__',
                _mock_cli_init_jsonfile_option)
    @mock.patch('pmcf.policy.JSONPolicy.validate_resource',
                _mock_parse_file)
    @mock.patch('pmcf.provisioners.AWSFWProvisioner.__init__',
                _mock_cli_init_no_options)
    @mock.patch('pmcf.outputs.JSONOutput.__init__',
                _mock_cli_init_no_options)
    @mock.patch('pmcf.outputs.JSONOutput.add_resources',
                _mock_add_resources)
    @mock.patch('pmcf.outputs.JSONOutput.run',
                _mock_run_fails)
    def test_invalid_config_run_debug_fails(self):
        options = {
            'parser': 'AWSFWParser',
            'policy': 'JSONPolicy',
            'policyfile': 'tests/data/etc/policy-instance.json',
            'provisioner': 'AWSFWProvisioner',
            'output': 'JSONOutput',
            'verbose': False,
            'debug': True,
            'accesskey': 'XXXX',
            'secretkey': 'YYYY',
            'region': 'eu-west-1',
            'poll': False,
            'action': 'create',
            'stackfile': 'tests/data/awsfw/ais-stage-farm.xml',
        }
        cli = PMCFCLI(options)
        assert_equals(True, cli.run())

    @mock.patch('pmcf.parsers.awsfw_parser.AWSFWParser.__init__',
                _mock_cli_init_no_options)
    @mock.patch('pmcf.parsers.awsfw_parser.AWSFWParser.parse_file',
                _mock_parse_file)
    @mock.patch('pmcf.parsers.awsfw_parser.AWSFWParser.validate',
                _mock_validate)
    @mock.patch('pmcf.policy.JSONPolicy.__init__',
                _mock_cli_init_jsonfile_option)
    @mock.patch('pmcf.policy.JSONPolicy.validate_resource',
                _mock_parse_file)
    @mock.patch('pmcf.provisioners.AWSFWProvisioner.__init__',
                _mock_cli_init_no_options)
    @mock.patch('pmcf.outputs.JSONOutput.__init__',
                _mock_cli_init_no_options)
    @mock.patch('pmcf.outputs.JSONOutput.add_resources',
                _mock_add_resources)
    @mock.patch('pmcf.outputs.JSONOutput.run',
                _mock_run_fails)
    def test_invalid_config_run_fails(self):
        options = {
            'parser': 'AWSFWParser',
            'policy': 'JSONPolicy',
            'policyfile': 'tests/data/etc/policy-instance.json',
            'provisioner': 'AWSFWProvisioner',
            'output': 'JSONOutput',
            'verbose': False,
            'debug': False,
            'accesskey': 'XXXX',
            'secretkey': 'YYYY',
            'region': 'eu-west-1',
            'poll': False,
            'action': 'create',
            'stackfile': 'tests/data/awsfw/ais-stage-farm.xml',
        }
        cli = PMCFCLI(options)
        assert_equals(True, cli.run())
