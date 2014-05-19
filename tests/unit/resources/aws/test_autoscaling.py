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
from pmcf.resources.aws import autoscaling as asg

from tests.unit.resources import TestResource


class TestEc2Resource(TestResource):

    def test_tag_valid(self):
        data = {'Key': 'foo', 'Value': 'bar', 'PropagateAtLaunch': False}
        tag = asg.Tag(
            key='foo',
            value='bar',
            propogate=False,
        )
        assert_equals(tag.JSONrepr(), data)

    def test_notification_configuration_invalid_no_topic(self):
        nc = asg.NotificationConfiguration(
            "test",
            NotificationTypes=[asg.TEST_NOTIFICATION]
        )
        assert_raises(PropertyException, nc.JSONrepr)

    def test_notification_configuration_invalid_no_types(self):
        nc = asg.NotificationConfiguration(
            "test",
            TopicARN='testme-123'
        )
        assert_raises(PropertyException, nc.JSONrepr)

    def test_notification_configuration_valid(self):
        data = {
            'NotificationTypes': [
                'autoscaling:TEST_NOTIFICATION'
            ],
            'TopicARN': 'testme-123'
        }
        nc = asg.NotificationConfiguration(
            "test",
            TopicARN='testme-123',
            NotificationTypes=[asg.TEST_NOTIFICATION]
        )
        assert_equals(self._data_for_resource(nc), data)

    def test_autoscaling_group_invalid_no_sizes(self):
        a = asg.AutoScalingGroup(
            "test",
            AvailabilityZones=['a', 'b', 'c'],
            Cooldown=30,
            HealthCheckGracePeriod=5,
            HealthCheckType='EC2',
            LaunchConfigurationName='MyLC',
        )
        assert_raises(PropertyException, a.JSONrepr)

    def test_autoscaling_group_invalid_no_az(self):
        a = asg.AutoScalingGroup(
            "test",
            Cooldown=30,
            DesiredCapacity=1,
            HealthCheckGracePeriod=5,
            HealthCheckType='EC2',
            LaunchConfigurationName='MyLC',
            MaxSize=2,
            MinSize=1
        )
        assert_raises(PropertyException, a.JSONrepr)

    def test_autoscaling_group_invalid_bad_healthcheck_type(self):
        a = asg.AutoScalingGroup(
            "test",
            AvailabilityZones=['a', 'b', 'c'],
            Cooldown=30,
            DesiredCapacity=1,
            HealthCheckGracePeriod=5,
            HealthCheckType='BadPanda',
            LaunchConfigurationName='MyLC',
            MaxSize=2,
            MinSize=1
        )
        assert_raises(PropertyException, a.JSONrepr)

    def test_autoscaling_group_valid(self):
        data = {
            'Properties': {
                'AvailabilityZones': ['a', 'b', 'c'],
                'Cooldown': 30,
                'DesiredCapacity': 1,
                'HealthCheckGracePeriod': 5,
                'HealthCheckType': 'ELB',
                'LaunchConfigurationName': 'MyLC',
                'MaxSize': 2,
                'MinSize': 1
            },
            'Type': 'AWS::AutoScaling::AutoScalingGroup'
        }
        a = asg.AutoScalingGroup(
            "test",
            AvailabilityZones=['a', 'b', 'c'],
            Cooldown=30,
            DesiredCapacity=1,
            HealthCheckGracePeriod=5,
            HealthCheckType='ELB',
            LaunchConfigurationName='MyLC',
            MaxSize=2,
            MinSize=1
        )
        assert_equals(self._data_for_resource(a), data)
