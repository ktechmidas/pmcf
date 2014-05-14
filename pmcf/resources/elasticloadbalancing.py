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

# This is the model layer, with a light validation layer over what troposphere
# provides

from troposphere import elasticloadbalancing as elb

from pmcf.resources.helpers import elasticloadbalancing
from pmcf.utils import error


class AccessLoggingPolicy(elasticloadbalancing.AccessLoggingPolicy):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()

        if self.properties['Enabled'] == 'false':
            return True

        if len(set(self.properties.keys()).intersection(
               set(['EmitInterval', 'S3BucketName']))) != 2:
            error(self, 'Must specify EmitInterval and S3BucketName')

        if self.properties['EmitInterval'] not in [5, 60]:
            error(self, 'EmitInterval must be either 5 or 60')

        return True


class AppCookieStickinessPolicy(elb.AppCookieStickinessPolicy):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class HealthCheck(elb.HealthCheck):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class LBCookieStickinessPolicy(elb.LBCookieStickinessPolicy):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()

        if 'PolicyName' not in self.properties.keys():
            error(self, 'Need unique PolicyName')


class Listener(elb.Listener):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class Policy(elb.Policy):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()

        policy_types = [
            'AppCookieStickinessPolicyType',
            'BackendServerAuthenticationPolicyType',
            'LBCookieStickinessPolicyType',
            'ProxyProtocolPolicyType',
            'PublicKeyPolicyType',
            'SSLNegotiationPolicyType',
        ]

        if self.properties['PolicyType'] not in policy_types:
            error(self, 'PolicyType must be one of %s' % policy_types)


class ConnectionDrainingPolicy(elb.ConnectionDrainingPolicy):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class LoadBalancer(elasticloadbalancing.LoadBalancer):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()

        if len(set(self.properties.keys()).intersection(
               set(['AvailabilityZones', 'Subnets']))) > 1:
            error(self, 'Can not specify both Subnets and AvailabilityZones')


__all__ = [
    AccessLoggingPolicy,
    AppCookieStickinessPolicy,
    ConnectionDrainingPolicy,
    HealthCheck,
    LBCookieStickinessPolicy,
    Listener,
    LoadBalancer,
    Policy,
]
