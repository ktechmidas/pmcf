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

from pmcf.exceptions import ProvisionerException
from pmcf.outputs import C4AWSCFNOutput


def _mock_run(self, data, run, poll=False, action='create', upload=False):
    return True


class TestC4CFNOutput(object):

    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput.run', _mock_run)
    def test_run_no_environment_raises(self):
        md = {
            'name': 'test',
            'owner': 'nobody',
            'version': '1.2',
        }
        cfno = C4AWSCFNOutput()
        assert_raises(ProvisionerException, cfno.run, {}, md)

    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput.run', _mock_run)
    def test_run_no_name_raises(self):
        md = {
            'owner': 'nobody',
            'environment': 'dev',
            'version': '1.2',
        }
        cfno = C4AWSCFNOutput()
        assert_raises(ProvisionerException, cfno.run, {}, md)

    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput.run', _mock_run)
    def test_run_no_owner_raises(self):
        md = {
            'name': 'test',
            'environment': 'dev',
            'version': '1.2',
        }
        cfno = C4AWSCFNOutput()
        assert_raises(ProvisionerException, cfno.run, {}, md)

    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput.run', _mock_run)
    def test_run_no_version_raises(self):
        md = {
            'name': 'test',
            'owner': 'nobody',
            'environment': 'dev',
        }
        cfno = C4AWSCFNOutput()
        assert_raises(ProvisionerException, cfno.run, {}, md)

    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput.run', _mock_run)
    def test_dev_run_succeeds(self):
        cfno = C4AWSCFNOutput()
        metadata = {
            'name': 'test',
            'owner': 'nobody',
            'environment': 'dev',
            'version': '1.2',
        }
        assert_equals(cfno.run({}, metadata), True)

    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput.run', _mock_run)
    def test_prod_run_succeeds(self):
        cfno = C4AWSCFNOutput()
        metadata = {
            'name': 'test',
            'owner': 'nobody',
            'environment': 'prod',
            'version': '1.2',
        }
        assert_equals(cfno.run({}, metadata), True)
