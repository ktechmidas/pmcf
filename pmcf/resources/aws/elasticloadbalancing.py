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
..  module:: pmcf.resources.aws.elasticloadbalancing
    :platform: Unix
    :synopsis: wrapper classes for troposphere ec2 classes

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

from troposphere import elasticloadbalancing as elb

from pmcf.utils import do_init, do_json, error

# pylint: disable=super-init-not-called


class AccessLoggingPolicy(elb.AccessLoggingPolicy):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, **kwargs):
        do_init(self, title, prop=True, **kwargs)

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

        if self.properties['Enabled'] is False:
            return True

        if len(set(self.properties.keys()).intersection(
               set(['EmitInterval', 'S3BucketName']))) != 2:
            error(self, 'Must specify EmitInterval and S3BucketName')

        if self.properties['EmitInterval'] not in [5, 60]:
            error(self, 'EmitInterval must be either 5 or 60')

        return True


class AppCookieStickinessPolicy(elb.AppCookieStickinessPolicy):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, **kwargs):
        do_init(self, title, prop=True, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class HealthCheck(elb.HealthCheck):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, **kwargs):
        do_init(self, title, prop=True, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class LBCookieStickinessPolicy(elb.LBCookieStickinessPolicy):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, **kwargs):
        do_init(self, title, prop=True, **kwargs)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()

        if 'PolicyName' not in self.properties.keys():
            error(self, 'Need unique PolicyName')


class Listener(elb.Listener):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, **kwargs):
        do_init(self, title, prop=True, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class Policy(elb.Policy):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, **kwargs):
        do_init(self, title, prop=True, **kwargs)

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
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, **kwargs):
        do_init(self, title, prop=True, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class LoadBalancer(elb.LoadBalancer):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

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
               set(['AvailabilityZones', 'Subnets']))) > 1:
            error(self, 'Can not specify both Subnets and AvailabilityZones')


__all__ = [
    'AccessLoggingPolicy',
    'AppCookieStickinessPolicy',
    'ConnectionDrainingPolicy',
    'HealthCheck',
    'LBCookieStickinessPolicy',
    'Listener',
    'LoadBalancer',
    'Policy',
]
