# Copyright (c) 2015 Piksel
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

from troposphere import elasticache as ec

from pmcf.utils import error, init_error


class CacheCluster(ec.CacheCluster):
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


class ParameterGroup(ec.ParameterGroup):
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


class SecurityGroup(ec.SecurityGroup):
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


class SecurityGroupIngress(ec.SecurityGroupIngress):
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


class SubnetGroup(ec.SubnetGroup):
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


__all__ = [
    CacheCluster,
    ParameterGroup,
    SecurityGroup,
    SecurityGroupIngress,
    SubnetGroup,
]
