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
..  module:: pmcf.resources.aws.cloudformation
    :platform: Unix
    :synopsis: wrapper classes for troposphere cloudformation classes

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

from troposphere import cloudformation as cfn

from pmcf.resources.aws.helpers import cloudformation as cf
from pmcf.utils import do_init, do_json

# pylint: disable=super-init-not-called


class Stack(cf.Stack):
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


class WaitCondition(cfn.WaitCondition):
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


class WaitConditionHandle(cfn.WaitConditionHandle):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)


__all__ = [
    'Stack',
    'WaitCondition',
    'WaitConditionHandle',
]
