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
import sys

from pmcf.cli.cli import main


class TestBaseCLI(object):
    def test_main_succeeds(self):
        old_argv = sys.argv
        sys.argv = ['test.py', '-c', 'tests/data/etc/pmcf.conf',
                    '-P', 'tests/data/etc/policy.json',
                    '-p', 'c4', '-C', 'NoopConfig',
                    '-r', 'NoopCLI', '-a', 'create',
                    'tests/data/awsfw/ais-stage-farm.xml']
        assert_equals(False, main())
        sys.argv = old_argv

    def test_main_fails_on_exception(self):
        old_argv = sys.argv
        sys.argv = ['test.py', '-c', 'tests/data/etc/pmcf.conf',
                    '-P', 'tests/data/etc/policy.json',
                    '-p', 'c4', '-C', 'NoopConfig',
                    '-r', 'FailCLI', '-a', 'create',
                    'tests/data/awsfw/ais-stage-farm.xml']
        assert_equals(True, main())
        sys.argv = old_argv
