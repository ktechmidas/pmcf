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

from troposphere import rds

from pmcf.utils import error, init_error


class DBInstance(rds.DBInstance):
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
        if not self.properties.get('Family'):
            error(self, "Must specify `Family'")


class DBSubnetGroup(rds.DBSubnetGroup):
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


class RDSSecurityGroup(rds.RDSSecurityGroup):
    def __init__(self, title=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def validate(self):
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


class DBSecurityGroupIngress(rds.DBSecurityGroupIngress):
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
    DBInstance,
    DBParameterGroup,
    DBSecurityGroup,
    DBSecurityGroupIngress,
    DBSubnetGroup,
    RDSSecurityGroup,
]
