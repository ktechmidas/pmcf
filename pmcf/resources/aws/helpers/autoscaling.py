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

from troposphere import AWSObject
from troposphere.validators import integer


class ScheduledAction(AWSObject):
    type = "AWS::AutoScaling::ScheduledAction"

    props = {
        'AutoScalingGroupName': (basestring, True),
        'DesiredCapacity': (integer, False),
        'EndTime': (basestring, False),
        'MaxSize': (integer, False),
        'MinSize': (integer, False),
        'Recurrence': (basestring, True),
        'StartTime': (basestring, False),
    }

__all__ = [
    ScheduledAction,
]
