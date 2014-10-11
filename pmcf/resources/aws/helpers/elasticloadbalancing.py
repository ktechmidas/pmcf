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
from troposphere.validators import boolean
from troposphere.elasticloadbalancing import \
    (ConnectionDrainingPolicy, HealthCheck)


class AccessLoggingPolicy(AWSProperty):
    props = {
        'Enabled': (boolean, True),
        'EmitInterval': (int, False),
        'S3BucketName': (basestring, False),
        'S3BucketPrefix': (basestring, False),
    }


class LoadBalancer(AWSObject):
    type = "AWS::ElasticLoadBalancing::LoadBalancer"

    props = {
        'AccessLoggingPolicy': (AccessLoggingPolicy, False),
        'AppCookieStickinessPolicy': (list, False),
        'AvailabilityZones': (list, False),
        'ConnectionDrainingPolicy': (ConnectionDrainingPolicy, False),
        'CrossZone': (boolean, False),
        'HealthCheck': (HealthCheck, False),
        'Instances': (list, False),
        'LBCookieStickinessPolicy': (list, False),
        'LoadBalancerName': (basestring, False),
        'Listeners': (list, True),
        'Policies': (list, False),
        'Scheme': (basestring, False),
        'SecurityGroups': (list, False),
        'Subnets': (list, False),
        'Tags': (list, False),
    }


__all__ = [
    AccessLoggingPolicy,
    LoadBalancer,
]
