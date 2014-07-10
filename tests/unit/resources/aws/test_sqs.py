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
from pmcf.resources.aws import sqs

from tests.unit.resources import TestResource


class TestSQSResource(TestResource):
    def test_redrive_policy_valid(self):
        data = {
            'deadLetterTargetArn': 'test',
            'maxReceiveCount': 5
        }
        rp = sqs.RedrivePolicy(
            'test',
            deadLetterTargetArn='test',
            maxReceiveCount=5
        )
        assert_equals(self._data_for_resource(rp), data)

    def test_queue_valid(self):
        data = {
            'Properties': {
                'DelaySeconds': 5,
                'MaximumMessageSize': 128,
                'MessageRetentionPeriod': 60,
                'QueueName': 'test',
                'ReceiveMessageWaitTimeSeconds': 30,
                'RedrivePolicy': {
                    'deadLetterTargetArn': 'test',
                    'maxReceiveCount': 5
                },
                'VisibilityTimeout': 30,
            },
            'Type': 'AWS::SQS::Queue'
        }
        q = sqs.Queue(
            'test',
            DelaySeconds=5,
            MaximumMessageSize=128,
            MessageRetentionPeriod=60,
            QueueName='test',
            ReceiveMessageWaitTimeSeconds=30,
            RedrivePolicy=sqs.RedrivePolicy(
                'test',
                deadLetterTargetArn='test',
                maxReceiveCount=5
            ),
            VisibilityTimeout=30
        )
        assert_equals(self._data_for_resource(q), data)

    def test_queue_policy_valid(self):
        data = {
            'Properties': {
                'PolicyDocument': {},
                'Queues': ['test']
            },
            'Type': 'AWS::SQS::QueuePolicy'
        }
        qp = sqs.QueuePolicy(
            'test',
            PolicyDocument={},
            Queues=['test']
        )
        assert_equals(self._data_for_resource(qp), data)

    def test_queue_policy_invalid_no_queues(self):
        qp = sqs.QueuePolicy(
            'test',
            PolicyDocument={},
        )
        assert_raises(PropertyException, qp.JSONrepr)

    def test_redrive_policy_bad_name(self):
        assert_raises(PropertyException, sqs.RedrivePolicy, 'bad-name')

    def test_queue_bad_name(self):
        assert_raises(PropertyException, sqs.Queue, 'bad-name')

    def test_queue_policy_bad_name(self):
        assert_raises(PropertyException, sqs.QueuePolicy, 'bad-name')
