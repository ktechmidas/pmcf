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

from troposphere import autoscaling as asg

from pmcf.utils import error

EC2_INSTANCE_LAUNCH = "autoscaling:EC2_INSTANCE_LAUNCH"
EC2_INSTANCE_LAUNCH_ERROR = "autoscaling:EC2_INSTANCE_LAUNCH_ERROR"
EC2_INSTANCE_TERMINATE = "autoscaling:EC2_INSTANCE_TERMINATE"
EC2_INSTANCE_TERMINATE_ERROR = "autoscaling:EC2_INSTANCE_TERMINATE_ERROR"
TEST_NOTIFICATION = "autoscaling:TEST_NOTIFICATION"


class Tag(asg.Tag):
    pass


class NotificationConfiguration(asg.NotificationConfiguration):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class AutoScalingGroup(asg.AutoScalingGroup):
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


class ScheduledAction(asg.ScheduledAction):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class Trigger(asg.Trigger):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class EBSBlockDevice(asg.EBSBlockDevice):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class BlockDeviceMapping(asg.BlockDeviceMapping):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


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
