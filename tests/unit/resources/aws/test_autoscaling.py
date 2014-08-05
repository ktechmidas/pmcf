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


class TestASGResource(TestResource):

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

    def test_autoscaling_group_invalid_no_lc(self):
        a = asg.AutoScalingGroup(
            "test",
            AvailabilityZones=['a', 'b', 'c'],
            Cooldown=30,
            DesiredCapacity=1,
            HealthCheckGracePeriod=5,
            HealthCheckType='EC2',
            MaxSize=2,
            MinSize=1
        )
        assert_raises(PropertyException, a.JSONrepr)

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

    def test_autoscaling_group_invalid_bad_update_policy(self):
        a = asg.AutoScalingGroup(
            "test",
            AvailabilityZones=['a', 'b', 'c'],
            Cooldown=30,
            DesiredCapacity=1,
            HealthCheckGracePeriod=5,
            HealthCheckType='BadPanda',
            LaunchConfigurationName='MyLC',
            UpdatePolicy=asg.UpdatePolicy(
                'AutoScalingRollingUpdate',
                MaxBatchSize='2',
                MinInstancesInService='3',
                PauseTime='PT5M'
            ),
            MaxSize=2,
            MinSize=1
        )
        assert_raises(PropertyException, a.JSONrepr)

    def test_autoscaling_group_invalid_bad_termination_policy(self):
        a = asg.AutoScalingGroup(
            "test",
            AvailabilityZones=['a', 'b', 'c'],
            Cooldown=30,
            DesiredCapacity=1,
            HealthCheckGracePeriod=5,
            HealthCheckType='ELB',
            LaunchConfigurationName='MyLC',
            TerminationPolicies=['Never'],
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

    def test_metric_collection_invalid_no_granularity(self):
        mc = asg.MetricsCollection(
            "test"
        )
        assert_raises(PropertyException, mc.JSONrepr)

    def test_metric_collection_invalid_bad_metric(self):
        mc = asg.MetricsCollection(
            "test",
            Granularity='1m',
            Metrics=['NotAMetric']
        )
        assert_raises(PropertyException, mc.JSONrepr)

    def test_metric_collection_valid(self):
        data = {
            'Granularity': '1m',
            'Metrics': ['GroupMinSize', 'GroupMaxSize']
        }
        mc = asg.MetricsCollection(
            "test",
            Granularity='1m',
            Metrics=['GroupMinSize', 'GroupMaxSize']
        )
        assert_equals(self._data_for_resource(mc), data)

    def test_launchconfiguration_invalid_no_imageid(self):
        lc = asg.LaunchConfiguration(
            'test',
            AssociatePublicIpAddress=False,
            InstanceMonitoring=False,
            InstanceType='m1.large',
            KeyName='bootstrap',
            SecurityGroups=['default'],
        )
        assert_raises(PropertyException, lc.JSONrepr)

    def test_launchconfiguration_invalid_no_instancetype(self):
        lc = asg.LaunchConfiguration(
            'test',
            AssociatePublicIpAddress=False,
            ImageId='testami-123',
            InstanceMonitoring=False,
            KeyName='bootstrap',
            SecurityGroups=['default'],
        )
        assert_raises(PropertyException, lc.JSONrepr)

    def test_launchconfiguration_valid(self):
        data = {
            'Properties': {
                'AssociatePublicIpAddress': 'false',
                'ImageId': 'testami-123',
                'InstanceMonitoring': 'false',
                'InstanceType': 'm1.large',
                'KeyName': 'bootstrap',
                'SecurityGroups': ['default'],
            },
            'Type': 'AWS::AutoScaling::LaunchConfiguration'
        }
        lc = asg.LaunchConfiguration(
            'test',
            AssociatePublicIpAddress=False,
            ImageId='testami-123',
            InstanceMonitoring=False,
            InstanceType='m1.large',
            KeyName='bootstrap',
            SecurityGroups=['default'],
        )
        assert_equals(self._data_for_resource(lc), data)

    def test_scaling_policy_invalid_no_group_name(self):
        sp = asg.ScalingPolicy(
            'test',
            AdjustmentType='ChangeInCapacity',
            Cooldown=5,
            ScalingAdjustment='1'
        )
        assert_raises(PropertyException, sp.JSONrepr)

    def test_scaling_policy_invalid_no_scaling_adjustment(self):
        sp = asg.ScalingPolicy(
            'test',
            AdjustmentType='ChangeInCapacity',
            AutoScalingGroupName='testasg-123',
            Cooldown=5,
        )
        assert_raises(PropertyException, sp.JSONrepr)

    def test_scaling_policy_invalid_no_adjustment_type(self):
        sp = asg.ScalingPolicy(
            'test',
            AutoScalingGroupName='testasg-123',
            Cooldown=5,
            ScalingAdjustment='1'
        )
        assert_raises(PropertyException, sp.JSONrepr)

    def test_scaling_policy_invalid_bad_adjustment_type(self):
        sp = asg.ScalingPolicy(
            'test',
            AdjustmentType='DoSomethingRandom',
            AutoScalingGroupName='testasg-123',
            Cooldown=5,
            ScalingAdjustment='1'
        )
        assert_raises(PropertyException, sp.JSONrepr)

    def test_scaling_policy_valid(self):
        data = {
            'Properties': {
                'AdjustmentType': 'ChangeInCapacity',
                'AutoScalingGroupName': 'testasg-123',
                'Cooldown': 5,
                'ScalingAdjustment': '1'
            },
            'Type': 'AWS::AutoScaling::ScalingPolicy'
        }
        sp = asg.ScalingPolicy(
            'test',
            AdjustmentType='ChangeInCapacity',
            AutoScalingGroupName='testasg-123',
            Cooldown=5,
            ScalingAdjustment='1'
        )
        assert_equals(self._data_for_resource(sp), data)

    def test_scheduled_action_invalid_no_group_name(self):
        sa = asg.ScheduledAction(
            'test',
            DesiredCapacity=9,
            StartTime='2014-06-01T00:00:00Z',
            EndTime='2014-12-01T00:00:00Z',
            Recurrence='0 10 * * *'
        )
        assert_raises(PropertyException, sa.JSONrepr)

    def test_scheduled_action_invalid_no_start_time(self):
        sa = asg.ScheduledAction(
            'test',
            AutoScalingGroupName='testasg-123',
            DesiredCapacity=9,
            EndTime='2014-12-01T00:00:00Z',
            Recurrence='0 10 * * *'
        )
        assert_raises(PropertyException, sa.JSONrepr)

    def test_scheduled_action_invalid_no_end_time(self):
        sa = asg.ScheduledAction(
            'test',
            AutoScalingGroupName='testasg-123',
            DesiredCapacity=9,
            StartTime='2014-06-01T00:00:00Z',
            Recurrence='0 10 * * *'
        )
        assert_raises(PropertyException, sa.JSONrepr)

    def test_scheduled_action_invalid_no_recurrence(self):
        sa = asg.ScheduledAction(
            'test',
            AutoScalingGroupName='testasg-123',
            DesiredCapacity=9,
            StartTime='2014-06-01T00:00:00Z',
            EndTime='2014-12-01T00:00:00Z',
        )
        assert_raises(PropertyException, sa.JSONrepr)

    def test_scheduled_action_invalid_bad_date(self):
        sa = asg.ScheduledAction(
            'test',
            AutoScalingGroupName='testasg-123',
            DesiredCapacity=9,
            StartTime='2014-06-01T00:00:00Z',
            EndTime='2014-12-01T25:00:00Z',
            Recurrence='0 10 * * *'
        )
        assert_raises(PropertyException, sa.JSONrepr)

    def test_scheduled_action_invalid_bad_cron(self):
        sa = asg.ScheduledAction(
            'test',
            AutoScalingGroupName='testasg-123',
            DesiredCapacity=9,
            StartTime='2014-06-01T00:00:00Z',
            EndTime='2014-12-01T00:00:00Z',
            Recurrence='0 10 45 * *'
        )
        assert_raises(PropertyException, sa.JSONrepr)

    def test_scheduled_action_valid(self):
        data = {
            'Properties': {
                'AutoScalingGroupName': 'testasg-123',
                'Recurrence': '0 10 * * *',
                'StartTime': '2014-06-01T00:00:00Z',
                'EndTime': '2014-12-01T00:00:00Z',
                'DesiredCapacity': 9
            },
            'Type': 'AWS::AutoScaling::ScheduledAction'
        }
        sa = asg.ScheduledAction(
            'test',
            AutoScalingGroupName='testasg-123',
            DesiredCapacity=9,
            StartTime='2014-06-01T00:00:00Z',
            EndTime='2014-12-01T00:00:00Z',
            Recurrence='0 10 * * *'
        )
        assert_equals(self._data_for_resource(sa), data)

    def test_trigger_invalid_no_group_name(self):
        t = asg.Trigger(
            "test",
            MetricName="CPUUtilization",
            Namespace="AWS/EC2",
            Statistic="Average",
            Period="300",
            UpperBreachScaleIncrement="1",
            LowerBreachScaleIncrement="-1",
            BreachDuration="600",
            UpperThreshold="90",
            LowerThreshold="75",
            Dimensions=[
                {"Name": "AutoScalingGroupName",
                 "Value": "testasg-123"}
            ]
        )
        assert_raises(PropertyException, t.JSONrepr)

    def test_trigger_invalid_no_breach_duration(self):
        t = asg.Trigger(
            "test",
            MetricName="CPUUtilization",
            Namespace="AWS/EC2",
            Statistic="Average",
            Period="300",
            UpperBreachScaleIncrement="1",
            LowerBreachScaleIncrement="-1",
            AutoScalingGroupName="testasg-123",
            UpperThreshold="90",
            LowerThreshold="75",
            Dimensions=[
                {"Name": "AutoScalingGroupName",
                 "Value": "testasg-123"}
            ]
        )
        assert_raises(PropertyException, t.JSONrepr)

    def test_trigger_invalid_no_dimensions(self):
        t = asg.Trigger(
            "test",
            MetricName="CPUUtilization",
            Namespace="AWS/EC2",
            Statistic="Average",
            Period="300",
            UpperBreachScaleIncrement="1",
            LowerBreachScaleIncrement="-1",
            AutoScalingGroupName="testasg-123",
            BreachDuration="600",
            UpperThreshold="90",
            LowerThreshold="75",
        )
        assert_raises(PropertyException, t.JSONrepr)

    def test_trigger_invalid_no_lower_threshold(self):
        t = asg.Trigger(
            "test",
            MetricName="CPUUtilization",
            Namespace="AWS/EC2",
            Statistic="Average",
            Period="300",
            UpperBreachScaleIncrement="1",
            LowerBreachScaleIncrement="-1",
            AutoScalingGroupName="testasg-123",
            BreachDuration="600",
            UpperThreshold="90",
            Dimensions=[
                {"Name": "AutoScalingGroupName",
                 "Value": "testasg-123"}
            ]
        )
        assert_raises(PropertyException, t.JSONrepr)

    def test_trigger_invalid_no_upper_threshold(self):
        t = asg.Trigger(
            "test",
            MetricName="CPUUtilization",
            Namespace="AWS/EC2",
            Statistic="Average",
            Period="300",
            UpperBreachScaleIncrement="1",
            LowerBreachScaleIncrement="-1",
            AutoScalingGroupName="testasg-123",
            BreachDuration="600",
            LowerThreshold="75",
            Dimensions=[
                {"Name": "AutoScalingGroupName",
                 "Value": "testasg-123"}
            ]
        )
        assert_raises(PropertyException, t.JSONrepr)

    def test_trigger_invalid_no_metric_name(self):
        t = asg.Trigger(
            "test",
            Namespace="AWS/EC2",
            Statistic="Average",
            Period="300",
            UpperBreachScaleIncrement="1",
            LowerBreachScaleIncrement="-1",
            AutoScalingGroupName="testasg-123",
            BreachDuration="600",
            UpperThreshold="90",
            LowerThreshold="75",
            Dimensions=[
                {"Name": "AutoScalingGroupName",
                 "Value": "testasg-123"}
            ]
        )
        assert_raises(PropertyException, t.JSONrepr)

    def test_trigger_invalid_no_namespace(self):
        t = asg.Trigger(
            "test",
            MetricName="CPUUtilization",
            Statistic="Average",
            Period="300",
            UpperBreachScaleIncrement="1",
            LowerBreachScaleIncrement="-1",
            AutoScalingGroupName="testasg-123",
            BreachDuration="600",
            UpperThreshold="90",
            LowerThreshold="75",
            Dimensions=[
                {"Name": "AutoScalingGroupName",
                 "Value": "testasg-123"}
            ]
        )
        assert_raises(PropertyException, t.JSONrepr)

    def test_trigger_invalid_no_period(self):
        t = asg.Trigger(
            "test",
            MetricName="CPUUtilization",
            Namespace="AWS/EC2",
            Statistic="Average",
            UpperBreachScaleIncrement="1",
            LowerBreachScaleIncrement="-1",
            AutoScalingGroupName="testasg-123",
            BreachDuration="600",
            UpperThreshold="90",
            LowerThreshold="75",
            Dimensions=[
                {"Name": "AutoScalingGroupName",
                 "Value": "testasg-123"}
            ]
        )
        assert_raises(PropertyException, t.JSONrepr)

    def test_trigger_invalid_no_statistic(self):
        t = asg.Trigger(
            "test",
            MetricName="CPUUtilization",
            Namespace="AWS/EC2",
            Period="300",
            UpperBreachScaleIncrement="1",
            LowerBreachScaleIncrement="-1",
            AutoScalingGroupName="testasg-123",
            BreachDuration="600",
            UpperThreshold="90",
            LowerThreshold="75",
            Dimensions=[
                {"Name": "AutoScalingGroupName",
                 "Value": "testasg-123"}
            ]
        )
        assert_raises(PropertyException, t.JSONrepr)

    def test_trigger_valid(self):
        data = {
            "Properties": {
                "MetricName": "CPUUtilization",
                "Namespace": "AWS/EC2",
                "Statistic": "Average",
                "Period": "300",
                "UpperBreachScaleIncrement": "1",
                "LowerBreachScaleIncrement": "-1",
                "AutoScalingGroupName": "testasg-123",
                "BreachDuration": "600",
                "UpperThreshold": "90",
                "LowerThreshold": "75",
                "Dimensions": [{
                    "Name": "AutoScalingGroupName",
                    "Value": "testasg-123"
                }]
            },
            "Type": "AWS::AutoScaling::Trigger",
        }
        t = asg.Trigger(
            "test",
            MetricName="CPUUtilization",
            Namespace="AWS/EC2",
            Statistic="Average",
            Period="300",
            UpperBreachScaleIncrement="1",
            LowerBreachScaleIncrement="-1",
            AutoScalingGroupName="testasg-123",
            BreachDuration="600",
            UpperThreshold="90",
            LowerThreshold="75",
            Dimensions=[
                {"Name": "AutoScalingGroupName",
                 "Value": "testasg-123"}
            ]
        )
        assert_equals(self._data_for_resource(t), data)

    def test_ebs_block_device_invalid_no_snapshot_or_size(self):
        ebsbd = asg.EBSBlockDevice(
            "test",
            DependsOn='mumble'
        )
        assert_raises(PropertyException, ebsbd.JSONrepr)

    def test_ebs_block_device_invalid_snapshot_and_size(self):
        ebsbd = asg.EBSBlockDevice(
            "test",
            SnapshotId="testsn-123",
            VolumeSize=50
        )
        assert_raises(PropertyException, ebsbd.JSONrepr)

    def test_ebs_block_device_valid_snapshot(self):
        data = {
            "SnapshotId": "testsn-123"
        }
        ebsbd = asg.EBSBlockDevice(
            "test",
            SnapshotId="testsn-123"
        )
        assert_equals(self._data_for_resource(ebsbd), data)

    def test_ebs_block_device_valid_size(self):
        data = {
            "VolumeSize": 50,
        }
        ebsbd = asg.EBSBlockDevice(
            "test",
            VolumeSize=50
        )
        assert_equals(self._data_for_resource(ebsbd), data)

    def test_block_device_mapping_invalid_no_device_name(self):
        bdm = asg.BlockDeviceMapping(
            "test",
            VirtualName="ephemeral0"
        )
        assert_raises(PropertyException, bdm.JSONrepr)

    def test_block_device_mapping_invalid_both_ebs_and_virtual_name(self):
        bdm = asg.BlockDeviceMapping(
            "test",
            DeviceName="/dev/sdb",
            VirtualName="ephemeral0",
            Ebs=asg.EBSBlockDevice(
                "test",
                VolumeSize=50
            )
        )
        assert_raises(PropertyException, bdm.JSONrepr)

    def test_block_device_mapping_invalid_no_ebs_or_virtual_name(self):
        bdm = asg.BlockDeviceMapping(
            "test",
            DeviceName="/dev/sdb",
        )
        assert_raises(PropertyException, bdm.JSONrepr)

    def test_block_device_mapping_valid_virtual_name(self):
        data = {
            "DeviceName": "/dev/sdb",
            "VirtualName": "ephemeral0"
        }
        bdm = asg.BlockDeviceMapping(
            "test",
            DeviceName="/dev/sdb",
            VirtualName="ephemeral0"
        )
        assert_equals(self._data_for_resource(bdm), data)

    def test_block_device_mapping_valid_ebs(self):
        data = {
            "DeviceName": "/dev/sdb",
            "Ebs": {"VolumeSize": 50}
        }
        bdm = asg.BlockDeviceMapping(
            "test",
            DeviceName="/dev/sdb",
            Ebs=asg.EBSBlockDevice(
                "test",
                VolumeSize=50
            )
        )
        assert_equals(self._data_for_resource(bdm), data)

    def test_notification_configuration_invalid_args(self):
        assert_raises(
            PropertyException,
            asg.NotificationConfiguration,
            'bad-name')

    def test_update_policy_invalid_name(self):
        assert_raises(PropertyException, asg.UpdatePolicy, 'bad-name')

    def test_metrics_collection_invalid_name(self):
        assert_raises(PropertyException, asg.MetricsCollection, 'bad-name')

    def test_auto_scaling_group_invalid_name(self):
        assert_raises(PropertyException, asg.AutoScalingGroup, 'bad-name')

    def test_launch_configuration_invalid_name(self):
        assert_raises(PropertyException, asg.LaunchConfiguration, 'bad-name')

    def test_scaling_policy_invalid_name(self):
        assert_raises(PropertyException, asg.ScalingPolicy, 'bad-name')

    def test_scheduled_action_invalid_name(self):
        assert_raises(PropertyException, asg.ScheduledAction, 'bad-name')

    def test_trigger_invalid_name(self):
        assert_raises(PropertyException, asg.Trigger, 'bad-name')

    def test_ebs_block_device_invalid_name(self):
        assert_raises(PropertyException, asg.EBSBlockDevice, 'bad-name')

    def test_block_device_mapping_invalid_name(self):
        assert_raises(PropertyException, asg.BlockDeviceMapping, 'bad-name')
