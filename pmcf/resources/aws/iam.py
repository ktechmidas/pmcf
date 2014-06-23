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
..  module:: pmcf.resources.aws.iam
    :platform: Unix
    :synopsis: Piksel Managed Cloud Framework

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

from troposphere import iam

from pmcf.utils import error


class AccessKey(iam.AccessKey):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()
        if self.properties.get('Status'):
            if self.properties['Status'] not in ["Active", "Inactive"]:
                error(self, 'Status %s not valid' % self.properties['Status'])

        return True


class Group(iam.Group):
    def validate(self):
        super(self.__class__, self).validate()
        if self.properties.get('Path'):
            if self.properties['Path'][0] != '/' and\
                    self.properties['Path'][-1] != '/':
                error(self, "Path must begin and end with `/`")


class InstanceProfile(iam.InstanceProfile):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()
        if self.properties.get('Path'):
            if self.properties['Path'][0] != '/' and\
                    self.properties['Path'][-1] != '/':
                error(self, "Path must begin and end with `/`")


class LoginProfile(iam.LoginProfile):
    def validate(self):
        super(self.__class__, self).validate()
        if self.properties.get('Path'):
            if self.properties['Path'][0] != '/' and\
                    self.properties['Path'][-1] != '/':
                error(self, "Path must begin and end with `/`")


class Policy(iam.Policy):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class PolicyType(iam.PolicyType):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()
        if self.properties.get('Path'):
            if self.properties['Path'][0] != '/' and\
                    self.properties['Path'][-1] != '/':
                error(self, "Path must begin and end with `/`")


class Role(iam.Role):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()
        if self.properties.get('Path'):
            if self.properties['Path'][0] != '/' and\
                    self.properties['Path'][-1] != '/':
                error(self, "Path must begin and end with `/`")


class User(iam.User):
    def validate(self):
        super(self.__class__, self).validate()
        if self.properties.get('Path'):
            if self.properties['Path'][0] != '/' and\
                    self.properties['Path'][-1] != '/':
                error(self, "Path must begin and end with `/`")


class UserToGroupAddition(iam.UserToGroupAddition):
    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


__all__ = [
    AccessKey,
    Group,
    InstanceProfile,
    LoginProfile,
    Policy,
    PolicyType,
    Role,
    User,
    UserToGroupAddition,
]
