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
..  module:: pmcf.resources.aws.rds
    :platform: Unix
    :synopsis: Piksel Managed Cloud Framework

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

from troposphere import rds

from pmcf.utils import do_init, do_json, error

# pylint: disable=super-init-not-called


class DBInstance(rds.DBInstance):
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
        if self.properties.get('Iops'):
            if (self.properties['Iops'] % 1000) != 0:
                error(self, "Iops must be a multiple of 1000")
            if (self.properties['Iops'] / 10) !=\
                    int(self.properties['AllocatedStorage']):
                error(self, "`AllocatedStorage' must be `Iops' / 10")

        if len(set(self.properties.keys()).intersection(
                set(['DBSecurityGroups', 'VPCSecurityGroups']))) == 2:
            error(self, "Cannot specify both `DBSecurityGroups' and "
                        "`VPCSecurityGroups'")

        if self.properties.get('MultiAZ'):
            if self.properties.get('AvailabilityZone'):
                error(self, "Can't specify both `AvailabilityZone' and "
                            "`MultiAZ'")


class DBParameterGroup(rds.DBParameterGroup):
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
        if not self.properties.get('Family'):
            error(self, "Must specify `Family'")


class DBSubnetGroup(rds.DBSubnetGroup):
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


class RDSSecurityGroup(rds.RDSSecurityGroup):
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
        if self.properties.get('CIDRIP'):
            if len(set(self.properties.keys()).intersection(
                set(['EC2SecurityGroupId', 'EC2SecurityGroupName',
                     'EC2SecurityGroupOwnerId']))) > 0:
                error(self, "CIDRIP is only valid on its own")
        else:
            if len(set(self.properties.keys()).intersection(
                    set(['EC2SecurityGroupId', 'EC2SecurityGroupName']))) != 1:
                    error(self, "Cannot use both `EC2SecurityGroupId' and "
                                "`EC2SecurityGroupName'")


class DBSecurityGroup(rds.DBSecurityGroup):
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


class DBSecurityGroupIngress(rds.DBSecurityGroupIngress):
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
        if self.properties.get('CIDRIP'):
            if len(set(self.properties.keys()).intersection(
                set(['EC2SecurityGroupId', 'EC2SecurityGroupName',
                     'EC2SecurityGroupOwnerId']))) > 0:
                error(self, "CIDRIP is only valid on its own")
        else:
            if len(set(self.properties.keys()).intersection(
                    set(['EC2SecurityGroupId', 'EC2SecurityGroupName']))) != 1:
                    error(self, "Cannot use both `EC2SecurityGroupId' and "
                                "`EC2SecurityGroupName'")


__all__ = [
    'DBInstance',
    'DBParameterGroup',
    'DBSecurityGroup',
    'DBSecurityGroupIngress',
    'DBSubnetGroup',
    'RDSSecurityGroup',
]
