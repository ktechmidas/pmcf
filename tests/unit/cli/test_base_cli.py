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
import sys

from pmcf.cli.cli import main
from pmcf.exceptions import PropertyException


def _mock_get_config(self):
    return {
        'parser': 'AWSFWParser',
        'policy': 'JSONPolicy',
        'policyfile': 'blah.json',
        'provisioner': 'AWSFWProvisioner',
        'output': 'JSONOutput',
    }


def _mock_cli_init(self, options):
    pass


def _mock_run_succeeds(self):
    return False


def _mock_run_fails(self):
    raise PropertyException('test')


class TestBaseCLI(object):
    @mock.patch('pmcf.config.config.PMCFConfig.get_config', _mock_get_config)
    @mock.patch('pmcf.cli.cmd.PMCFCLI.__init__', _mock_cli_init)
    @mock.patch('pmcf.cli.cmd.PMCFCLI.run', _mock_run_succeeds)
    def test_main_succeeds(self):
        old_argv = sys.argv
        sys.argv = ['test.py', '-c', 'tests/data/etc/pmcf.conf',
                    '-P', 'tests/data/etc/policy.json',
                    '-p', 'c4', '-a', 'create',
                    'tests/data/awsfw/ais-stage-farm.xml']
        assert_equals(False, main())
        sys.argv = old_argv

    @mock.patch('pmcf.config.config.PMCFConfig.get_config', _mock_get_config)
    @mock.patch('pmcf.cli.cmd.PMCFCLI.__init__', _mock_cli_init)
    @mock.patch('pmcf.cli.cmd.PMCFCLI.run', _mock_run_succeeds)
    def test_verbose_main_succeeds(self):
        old_argv = sys.argv
        sys.argv = ['test.py', '-c', 'tests/data/etc/pmcf.conf',
                    '-P', 'tests/data/etc/policy.json',
                    '-p', 'c4', '-a', 'create', '-v',
                    'tests/data/awsfw/ais-stage-farm.xml']
        assert_equals(False, main())
        sys.argv = old_argv

    @mock.patch('pmcf.config.config.PMCFConfig.get_config', _mock_get_config)
    @mock.patch('pmcf.cli.cmd.PMCFCLI.__init__', _mock_cli_init)
    @mock.patch('pmcf.cli.cmd.PMCFCLI.run', _mock_run_succeeds)
    def test_debug_main_succeeds(self):
        old_argv = sys.argv
        sys.argv = ['test.py', '-c', 'tests/data/etc/pmcf.conf',
                    '-P', 'tests/data/etc/policy.json',
                    '-p', 'c4', '-a', 'create', '-d',
                    'tests/data/awsfw/ais-stage-farm.xml']
        assert_equals(False, main())
        sys.argv = old_argv

    @mock.patch('pmcf.config.config.PMCFConfig.get_config', _mock_get_config)
    @mock.patch('pmcf.cli.cmd.PMCFCLI.__init__', _mock_cli_init)
    @mock.patch('pmcf.cli.cmd.PMCFCLI.run', _mock_run_succeeds)
    def test_quiet_main_succeeds(self):
        old_argv = sys.argv
        sys.argv = ['test.py', '-c', 'tests/data/etc/pmcf.conf',
                    '-P', 'tests/data/etc/policy.json',
                    '-p', 'c4', '-a', 'create', '-q',
                    'tests/data/awsfw/ais-stage-farm.xml']
        assert_equals(False, main())
        sys.argv = old_argv

    @mock.patch('pmcf.config.config.PMCFConfig.get_config', _mock_get_config)
    @mock.patch('pmcf.cli.cmd.PMCFCLI.__init__', _mock_cli_init)
    @mock.patch('pmcf.cli.cmd.PMCFCLI.run', _mock_run_fails)
    def test_fail_of_main_fails(self):
        old_argv = sys.argv
        sys.argv = ['test.py', '-c', 'tests/data/etc/pmcf.conf',
                    '-P', 'tests/data/etc/policy.json',
                    '-p', 'c4', '-a', 'create',
                    'tests/data/awsfw/ais-stage-farm.xml']
        assert_equals(True, main())
        sys.argv = old_argv
