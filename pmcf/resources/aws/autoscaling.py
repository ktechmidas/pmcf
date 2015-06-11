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

"""
..  module:: pmcf.resources.aws.autoscaling
    :platform: Unix
    :synopsis: wrapper classes for troposphere autoscaling classes

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import time
from troposphere import autoscaling as asg
from troposphere import UpdatePolicy as udp
from pmcf.resources.aws.helpers import autoscaling

from pmcf.utils import do_init, do_json, error

EC2_INSTANCE_LAUNCH = asg.EC2_INSTANCE_LAUNCH
EC2_INSTANCE_LAUNCH_ERROR = asg.EC2_INSTANCE_LAUNCH_ERROR
EC2_INSTANCE_TERMINATE = asg.EC2_INSTANCE_TERMINATE
EC2_INSTANCE_TERMINATE_ERROR = asg.EC2_INSTANCE_TERMINATE_ERROR
TEST_NOTIFICATION = asg.TEST_NOTIFICATION

# pylint: disable=super-init-not-called


class Tag(asg.Tag):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    pass


class UpdatePolicy(udp):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, prop=True, **kwargs)


class NotificationConfiguration(asg.NotificationConfiguration):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, template=None, **kwargs):
        do_init(self, title, template=template, prop=True, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class MetricsCollection(asg.MetricsCollection):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, template=None, **kwargs):
        do_init(self, title, template=template, prop=True, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

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


class AutoScalingGroup(asg.AutoScalingGroup):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()
        if self.properties.get('HealthCheckType', None):
            if self.properties['HealthCheckType'] not in ['ELB', 'EC2']:
                error(self, "HealthCheckType must be one of `ELB' or `EC2'")

        valid_policies = set([
            'Default',
            'OldestInstance',
            'NewestInstance',
            'OldestLaunchConfiguration',
            'ClosestToNextInstanceHour',
        ])

        if self.properties.get('TerminationPolicies'):
            invalid_policies = set(self.properties['TerminationPolicies']) -\
                valid_policies
            if len(invalid_policies) > 0:
                raise ValueError(
                    "Invalid TerminationPolicy declaration: "
                    "%s not valid" % invalid_policies)

        return True


class LaunchConfiguration(asg.LaunchConfiguration):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class ScalingPolicy(asg.ScalingPolicy):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()
        valid_adj_types = [
            'ChangeInCapacity',
            'ExactCapacity',
            'PercentChangeInCapacity',
        ]
        if self.properties['AdjustmentType'] not in valid_adj_types:
            error(self, 'AdjustmentType must be one of %s' %
                  ', '.join(valid_adj_types))


class ScheduledAction(autoscaling.ScheduledAction):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()

        if len(set(self.properties.keys()).intersection(
                set(['DesiredCapacity', 'MinSize', 'MaxSize']))) == 0:
            error(self, "Need to specify one of `DesiredCapacity', `MinSize', "
                        "`MaxSize'")

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
            if self.properties.get(item):
                try:
                    time.strptime(self.properties[item], tm_fmt)
                except ValueError:
                    error(self, '%s invalid date, must match %s' %
                          (item, tm_fmt))


class Trigger(asg.Trigger):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class EBSBlockDevice(asg.EBSBlockDevice):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, template=None, **kwargs):
        do_init(self, title, template=template, prop=True, **kwargs)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()
        if len(set(self.properties.keys()).intersection(
                set(['SnapshotId', 'VolumeSize']))) != 1:
            error(self, "Need to specify one of `SnapshotId', `VolumeSize'")
        if 'VolumeType' in self.properties.keys():
            allowed_types = ['standard', 'io1', 'gp2']
            if self.properties['VolumeType'] not in allowed_types:
                error(self, "Bad VolumeType: `%s' - must be one of `%s'" % (
                    self.properties['VolumeType'],
                    ("', `").join(allowed_types)
                ))


class BlockDeviceMapping(asg.BlockDeviceMapping):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, template=None, **kwargs):
        do_init(self, title, template=template, prop=True, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()
        if len(set(self.properties.keys()).intersection(
                set(['Ebs', 'VirtualName']))) != 1:
            error(self, "Need to specify one of `Ebs', `VirtualName'")


__all__ = [
    'EC2_INSTANCE_LAUNCH',
    'EC2_INSTANCE_LAUNCH_ERROR',
    'EC2_INSTANCE_TERMINATE',
    'EC2_INSTANCE_TERMINATE_ERROR',
    'TEST_NOTIFICATION',
    'AutoScalingGroup',
    'BlockDeviceMapping',
    'EBSBlockDevice',
    'LaunchConfiguration',
    'NotificationConfiguration',
    'ScalingPolicy',
    'ScheduledAction',
    'Tag',
    'Trigger',
]
