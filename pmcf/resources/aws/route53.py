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

from pmcf.utils import error, init_error


class AliasTarget(route53.AliasTarget):
    pass


class RecordSetType(route53.RecordSetType):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
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
    def __init__(self, title=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
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
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def validate(self):
        super(self.__class__, self).validate()
        if len(set(['HostedZoneId', 'HostedZoneName']).intersection(
                set(self.properties.keys()))) != 1:
            error(self, 'Must set one of HostedZoneId or HostedZoneName')

        return True
