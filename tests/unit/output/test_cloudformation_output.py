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

from boto.exception import BotoServerError
import mock
from nose.tools import assert_equals, assert_raises

from pmcf.exceptions import ProvisionerException
from pmcf.outputs import AWSCFNOutput


def _mock_search_regions(svc):
    class FakeRegion(object):
        def __init__(self):
            self.name = 'eu-west-1'
            self.endpoint = 'http://localhost/'
    return [FakeRegion()]


def _mock_create_stack(obj, name, data):
    pass


class TestAWSCFNParser(object):

    def test_run_no_region_raises(self):
        cfno = AWSCFNOutput()
        assert_raises(ProvisionerException, cfno.run, {}, {})

    def test_run_bad_region_raises(self):
        cfno = AWSCFNOutput()
        assert_raises(ProvisionerException, cfno.run, {}, {'region': 'nah'})

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('boto.cloudformation.CloudFormationConnection.create_stack',
                _mock_create_stack)
    def test_run_connects(self):
        # Really, I should be able to test I have a connection separately
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test'
        }
        assert_equals(cfno.run({}, metadata), True)
