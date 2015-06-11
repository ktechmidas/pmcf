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
..  module:: pmcf.resources.aws.route53
    :platform: Unix
    :synopsis: Piksel Managed Cloud Framework

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

from troposphere import route53

from pmcf.utils import do_init, do_json, error

# pylint: disable=super-init-not-called


class AliasTarget(route53.AliasTarget):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    pass


class RecordSetType(route53.RecordSetType):
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
        rr_props = ['TTL', 'SetIdentifier']
        if self.properties.get('AliasTarget'):
            if self.properties.get('ResourceRecords'):
                error(self, "Can't set both ResourceRecords and AliasTarget")

        for prop in rr_props:
            if self.properties.get(prop):
                if not self.properties.get('ResourceRecords'):
                    error(self, "Must set ResourceRecords with %s" % prop)

        if self.properties.get('ResourceRecords'):
            found = False
            for prop in rr_props:
                if self.properties.get(prop):
                    found = True
                    break
            if not found:
                error(
                    self,
                    "Must set TTL or SetIdentifier with ResourceRecords"
                )

        return True


class RecordSet(route53.RecordSet):
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
        rr_props = ['TTL', 'SetIdentifier']
        if self.properties.get('AliasTarget'):
            if self.properties.get('ResourceRecords'):
                error(self, "Can't set both ResourceRecords and AliasTarget")

        for prop in rr_props:
            if self.properties.get(prop):
                if not self.properties.get('ResourceRecords'):
                    error(self, "Must set ResourceRecords with %s" % prop)

        if self.properties.get('ResourceRecords'):
            found = False
            for prop in rr_props:
                if self.properties.get(prop):
                    found = True
                    break
            if not found:
                error(
                    self,
                    "Must set TTL or SetIdentifier with ResourceRecords"
                )

        return True


class RecordSetGroup(route53.RecordSetGroup):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()
        if len(set(['HostedZoneId', 'HostedZoneName']).intersection(
                set(self.properties.keys()))) != 1:
            error(self, 'Must set one of HostedZoneId or HostedZoneName')

        return True

__all__ = [
    'AliasTarget',
    'RecordSet',
    'RecordSetGroup',
    'RecordSetType',
]
