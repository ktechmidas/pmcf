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

from troposphere import AWSObject, AWSProperty
from troposphere.validators import positive_integer, integer
from troposphere.autoscaling import NotificationConfiguration


class MetricsCollection(AWSProperty):
    props = {
        'Granularity': (basestring, True),
        'Metrics': (list, False),
    }


class AutoScalingGroup(AWSObject):
    type = "AWS::AutoScaling::AutoScalingGroup"

    props = {
        'AvailabilityZones': (list, True),
        'Cooldown': (integer, False),
        'DesiredCapacity': (integer, False),
        'HealthCheckGracePeriod': (int, False),
        'HealthCheckType': (basestring, False),
        'InstanceId': (basestring, False),
        'LaunchConfigurationName': (basestring, False),
        'LoadBalancerNames': (list, False),
        'MetricsCollection': (list, False),
        'MaxSize': (positive_integer, True),
        'MinSize': (positive_integer, True),
        'NotificationConfiguration': (NotificationConfiguration, False),
        'Tags': (list, False),  # Although docs say these are required
        'VPCZoneIdentifier': (list, False),
    }

    def validate(self):
        if 'UpdatePolicy' in self.resource:
            update_policy = self.resource['UpdatePolicy']
            if int(update_policy.MinInstancesInService) >= int(self.MaxSize):
                raise ValueError(
                    "The UpdatePolicy attribute "
                    "MinInstancesInService must be less than the "
                    "autoscaling group's MaxSize")
        return True


__all__ = [
    AutoScalingGroup,
    MetricsCollection,
]
