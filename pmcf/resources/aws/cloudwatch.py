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

from troposphere import cloudwatch

from pmcf.utils import error


class MetricDimension(cloudwatch.MetricDimension):
    def __init__(self, title=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, **kwargs)
        except (AttributeError, ValueError), e:
            error(self, e.message)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class Alarm(cloudwatch.Alarm):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except (TypeError, ValueError), e:
            error(self, e.message)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


__all__ = [
    MetricDimension,
    Alarm,
]