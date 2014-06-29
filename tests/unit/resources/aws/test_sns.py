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

from pmcf.exceptions import PropertyException
from pmcf.resources.aws import sns

from tests.unit.resources import TestResource


class TestSNSResource(TestResource):

    def test_subscription_valid(self):
        data = {
            'Endpoint': 'test@test.com',
            'Protocol': 'email'
        }
        s = sns.Subscription(
            'test',
            Endpoint='test@test.com',
            Protocol='email'
        )
        assert_equals(self._data_for_resource(s), data)

    def test_subscription_invalid_no_endpoint(self):
        s = sns.Subscription(
            'test',
            Protocol='email'
        )
        assert_raises(PropertyException, s.JSONrepr)

    def test_subscription_invalid_no_protocol(self):
        s = sns.Subscription(
            'test',
            Endpoint='test@test.com',
        )
        assert_raises(PropertyException, s.JSONrepr)

    def test_subscription_invalid_bad_protocol(self):
        s = sns.Subscription(
            'test',
            Protocol='carrier-pigeon',
            Endpoint='test@test.com',
        )
        assert_raises(PropertyException, s.JSONrepr)

    def test_topic_policy_valid(self):
        data = {
            'Properties': {
                'PolicyDocument': {},
                'Topics': ['foo'],
            },
            'Type': 'AWS::SNS::TopicPolicy'
        }
        tp = sns.TopicPolicy(
            'test',
            PolicyDocument={},
            Topics=['foo']
        )
        assert_equals(self._data_for_resource(tp), data)

    def test_topic_policy_invalid_no_topics(self):
        tp = sns.TopicPolicy(
            'test',
            PolicyDocument={},
        )
        assert_raises(PropertyException, tp.JSONrepr)

    def test_topic_valid(self):
        data = {
            'Properties': {
                'DisplayName': 'test',
                'Subscription': [{
                    'Endpoint': 'test@test.com', 'Protocol': 'email'}],
                'TopicName': 'test',
            },
            'Type': 'AWS::SNS::Topic'
        }
        t = sns.Topic(
            'test',
            DisplayName='test',
            Subscription=[sns.Subscription(
                Endpoint='test@test.com',
                Protocol='email'
            )],
            TopicName='test'
        )
        assert_equals(self._data_for_resource(t), data)

    def test_topic_invalid_no_subscriptions(self):
        t = sns.Topic(
            'test',
            DisplayName='test',
            TopicName='test'
        )
        assert_raises(PropertyException, t.JSONrepr)
