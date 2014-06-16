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
from troposphere import Ref

from pmcf.exceptions import PropertyException
from pmcf.resources.aws import cloudformation as cfn

from tests.unit.resources import TestResource


class TestCFNResource(TestResource):

    def test_stack_valid(self):
        data = {
            'Properties': {
                'TemplateURL': 'http://example.com/foo.json',
                'TimeoutInMinutes': 3600
            },
            'Type': u'AWS::CloudFormation::Stack'
        }
        s = cfn.Stack(
            'test',
            TemplateURL='http://example.com/foo.json',
            TimeoutInMinutes=3600
        )
        assert_equals(self._data_for_resource(s), data)

    def test_stack_invalid_no_url(self):
        s = cfn.Stack(
            'test',
            TimeoutInMinutes=3600
        )
        assert_raises(PropertyException, s.JSONrepr)

    def test_wait_condition_valid(self):
        data = {
            'Properties': {
                'Count': 2,
                'Handle': {
                    'Ref': 'test'
                },
                'Timeout': 3600
            },
            'Type': u'AWS::CloudFormation::WaitCondition'
        }
        wc = cfn.WaitCondition(
            'test',
            Count=2,
            Handle=Ref('test'),
            Timeout=3600
        )
        assert_equals(self._data_for_resource(wc), data)

    def test_wait_condition_invalid_no_handle(self):
        wc = cfn.WaitCondition(
            'test',
            Count=2,
            Timeout=3600
        )
        assert_raises(PropertyException, wc.JSONrepr)

    def test_wait_condition_invalid_no_timeout(self):
        wc = cfn.WaitCondition(
            'test',
            Count=2,
            Handle=Ref('test'),
        )
        assert_raises(PropertyException, wc.JSONrepr)

    def test_wait_condition_handle_valid(self):
        data = {
            'Type': u'AWS::CloudFormation::WaitConditionHandle',
        }
        wch = cfn.WaitConditionHandle('test')
        assert_equals(self._data_for_resource(wch), data)
