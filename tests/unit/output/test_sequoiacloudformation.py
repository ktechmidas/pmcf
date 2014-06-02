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
from pmcf.outputs import SequoiaAWSCFNOutput


def _mock_run(self, data, run):
    return True


class TestSequoiaCFNOutput(object):

    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput.run', _mock_run)
    def test_run_no_stage_raises(self):
        md = {
            'name': 'test',
        }
        cfno = SequoiaAWSCFNOutput()
        assert_raises(ProvisionerException, cfno.run, {}, md)

    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput.run', _mock_run)
    def test_run_no_name_raises(self):
        md = {
            'stage': 'dev',
        }
        cfno = SequoiaAWSCFNOutput()
        assert_raises(ProvisionerException, cfno.run, {}, md)

    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput.run', _mock_run)
    def test_dev_run_succeeds(self):
        cfno = SequoiaAWSCFNOutput()
        metadata = {
            'name': 'test',
            'stage': 'dev',
        }
        assert_equals(cfno.run({}, metadata), True)

    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput.run', _mock_run)
    def test_prod_run_succeeds(self):
        cfno = SequoiaAWSCFNOutput()
        metadata = {
            'name': 'test',
            'stage': 'prod',
        }
        assert_equals(cfno.run({}, metadata), True)
