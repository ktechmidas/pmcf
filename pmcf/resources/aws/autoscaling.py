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

import time
from troposphere import autoscaling as asg
from troposphere import UpdatePolicy

from pmcf.resources.aws.helpers import autoscaling
from pmcf.utils import error

EC2_INSTANCE_LAUNCH = asg.EC2_INSTANCE_LAUNCH
EC2_INSTANCE_LAUNCH_ERROR = asg.EC2_INSTANCE_LAUNCH_ERROR
EC2_INSTANCE_TERMINATE = asg.EC2_INSTANCE_TERMINATE
EC2_INSTANCE_TERMINATE_ERROR = asg.EC2_INSTANCE_TERMINATE_ERROR
TEST_NOTIFICATION = asg.TEST_NOTIFICATION


class Tag(asg.Tag):
    pass


class UpdatePolicy(UpdatePolicy):
    pass


class NotificationConfiguration(asg.NotificationConfiguration):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class MetricsCollection(autoscaling.MetricsCollection):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()
        allowed_metrics = [
            'GroupMinSize',
            'GroupMaxSize',
            'GroupDesiredCapacity',
            'GroupInServiceInstances',
            'GroupPendingInstances',
            'GroupTerminatingInstances',
            'GroupTotalInstances',
        ]

        if self.properties.get('Metrics'):
            for metric in self.properties['Metrics']:
                if metric not in allowed_metrics:
                    error(self, 'Metric %s not known' % metric)

        return True


class AutoScalingGroup(autoscaling.AutoScalingGroup):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()
        if self.properties.get('HealthCheckType', None):
            if self.properties['HealthCheckType'] not in ['ELB', 'EC2']:
                error(self, "HealthCheckType must be one of `ELB' or `EC2'")

        if len(set(self.properties.keys()).intersection(
                set(['InstanceId', 'LaunchConfigurationName']))) != 1:
            error(self, "Need to specify one of `InstanceId', "
                        "`LaunchConfigurationName'")

        return True


class LaunchConfiguration(asg.LaunchConfiguration):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class ScalingPolicy(asg.ScalingPolicy):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()
        valid_adj_types = [
            'ChangeInCapacity',
            'ExactCapacity',
            'PercentChangeInCapacity',
        ]
        if self.properties['AdjustmentType'] not in valid_adj_types:
            error(self, 'AdjustmentType must be one of %s' %
                  ', '.join(valid_adj_types))


class ScheduledAction(asg.ScheduledAction):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()
        tm_fmt = "%Y-%m-%dT%H:%M:%SZ"
        cron_valid = [
            range(0, 8),
            range(1, 13),
            range(1, 32),
            range(0, 24),
            range(0, 60)
        ]
        recurrence = self.properties['Recurrence'].split()
        for idx, item in enumerate(recurrence):
            if item == '*':
                continue
            if int(item) not in cron_valid[idx]:
                error(self, "Invalid cron spec: %s not in range %d-%d or *" %
                      (item, cron_valid[idx][0], cron_valid[idx][-2]))

        for item in ['StartTime', 'EndTime']:
            try:
                struct_time = time.strptime(self.properties[item], tm_fmt)
            except ValueError:
                error(self, '%s invalid date, must match %s' % (item, tm_fmt))


class Trigger(asg.Trigger):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class EBSBlockDevice(asg.EBSBlockDevice):
    def validate(self):
        super(self.__class__, self).validate()
        if len(set(self.properties.keys()).intersection(
                set(['SnapshotId', 'VolumeSize']))) != 1:
            error(self, "Need to specify one of `SnapshotId', `VolumeSize'")


class BlockDeviceMapping(asg.BlockDeviceMapping):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()
        if len(set(self.properties.keys()).intersection(
                set(['Ebs', 'VirtualName']))) != 1:
            error(self, "Need to specify one of `Ebs', `VirtualName'")


__all__ = [
    EC2_INSTANCE_LAUNCH,
    EC2_INSTANCE_LAUNCH_ERROR,
    EC2_INSTANCE_TERMINATE,
    EC2_INSTANCE_TERMINATE_ERROR,
    TEST_NOTIFICATION,
    AutoScalingGroup,
    BlockDeviceMapping,
    EBSBlockDevice,
    LaunchConfiguration,
    NotificationConfiguration,
    ScalingPolicy,
    ScheduledAction,
    Tag,
    Trigger,
]
