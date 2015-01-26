# Copyright (c) 2015 Piksel
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
from pmcf.resources.aws import cloudwatch

from tests.unit.resources import TestResource


class TestCloudWatchResource(TestResource):

    def test_metric_dimension_valid(self):
        data = {
            'Name': 'test',
            'Value': 'test'
        }
        md = cloudwatch.MetricDimension(
            Name='test',
            Value='test',
        )
        assert_equals(md.JSONrepr(), data)

    def test_metric_dimension_invalid_no_name(self):
        md = cloudwatch.MetricDimension(
            Value='test',
        )
        assert_raises(PropertyException, md.JSONrepr)

    def test_metric_dimension_invalid_extra_param(self):
        data = {
            'Name': 'test',
            'Value': 'test',
            'Foo': 'test',
        }
        assert_raises(PropertyException, cloudwatch.MetricDimension, **data)

    def test_alarm_valid(self):
        data = {
            'Properties': {
                'ActionsEnabled': 'true',
                'AlarmActions': ['arn:foo'],
                'ComparisonOperator': 'GreaterThanThreshold',
                'Dimensions': [{'Name': 'test', 'Value': 'test'}],
                'EvaluationPeriods': 5,
                'MetricName': 'ChunterRate',
                'Namespace': 'AWS/EC2',
                'Period': 60,
                'Statistic': 'Average',
                'Threshold': 100,
                'Unit': 'Count'
            },
            'Type': 'AWS::CloudWatch::Alarm'
        }

        a = cloudwatch.Alarm(
            "test",
            ActionsEnabled=True,
            AlarmActions=['arn:foo'],
            ComparisonOperator='GreaterThanThreshold',
            Namespace="AWS/EC2",
            MetricName="ChunterRate",
            Dimensions=[
                cloudwatch.MetricDimension(
                    Name="test",
                    Value="test",
                )
            ],
            EvaluationPeriods=5,
            Period=60,
            Statistic="Average",
            Threshold=100,
            Unit="Count"
        )
        assert_equals(self._data_for_resource(a), data)

    def test_alarm_valid_invalid_no_comp_op(self):
        a = cloudwatch.Alarm(
            "test",
            ActionsEnabled=True,
            AlarmActions=['arn:foo'],
            Namespace="AWS/EC2",
            MetricName="ChunterRate",
            Dimensions=[
                cloudwatch.MetricDimension(
                    Name="test",
                    Value="test",
                )
            ],
            EvaluationPeriods=5,
            Period=60,
            Statistic="Average",
            Threshold=100,
            Unit="Count"
        )
        assert_raises(PropertyException, self._data_for_resource, a)

    def test_alarm_valid_invalid_no_comp_op2(self):
        data = {
            'ActionsEnabled': 'true',
            'AlarmActions': 'arn:foo',
            'ComparisonOperator': 'GreaterThanThreshold',
            'Dimensions': [
                cloudwatch.MetricDimension(
                    Name="test",
                    Value="test",
                )
            ],
            'EvaluationPeriods': 5,
            'MetricName': 'ChunterRate',
            'Namespace': 'AWS/EC2',
            'Period': 60,
            'Statistic': 'Average',
            'Threshold': 100,
            'Unit': 'Count'
        }

        assert_raises(PropertyException, cloudwatch.Alarm, "test", **data)
