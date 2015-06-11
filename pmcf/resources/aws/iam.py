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

from pmcf.utils import do_init, do_json, error

# pylint: disable=super-init-not-called


class AccessKey(iam.AccessKey):
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
        if self.properties.get('Status'):
            if self.properties['Status'] not in ["Active", "Inactive"]:
                error(self, 'Status %s not valid' % self.properties['Status'])

        return True


class Group(iam.Group):
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
        if self.properties.get('Path'):
            if not (self.properties['Path'].startswith('/') and
                    self.properties['Path'].endswith('/')):
                error(self, "Path must begin and end with `/`")


class InstanceProfile(iam.InstanceProfile):
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
        if self.properties.get('Path'):
            if not (self.properties['Path'].startswith('/') and
                    self.properties['Path'].endswith('/')):
                error(self, "Path must begin and end with `/`")


class LoginProfile(iam.LoginProfile):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    pass


class Policy(iam.Policy):
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


class PolicyType(iam.PolicyType):
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


class Role(iam.Role):
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
        if self.properties.get('Path'):
            if not (self.properties['Path'].startswith('/') and
                    self.properties['Path'].endswith('/')):
                error(self, "Path must begin and end with `/`")


class User(iam.User):
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
        if self.properties.get('Path'):
            if not (self.properties['Path'].startswith('/') and
                    self.properties['Path'].endswith('/')):
                error(self, "Path must begin and end with `/`")


class UserToGroupAddition(iam.UserToGroupAddition):
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


__all__ = [
    'AccessKey',
    'Group',
    'InstanceProfile',
    'LoginProfile',
    'Policy',
    'PolicyType',
    'Role',
    'User',
    'UserToGroupAddition',
]
