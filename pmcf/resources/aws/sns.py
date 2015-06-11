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
..  module:: pmcf.resources.aws.sns
    :platform: Unix
    :synopsis: Piksel Managed Cloud Framework

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

from troposphere import sns

from pmcf.utils import do_init, do_json, error

# pylint: disable=super-init-not-called


class Subscription(sns.Subscription):
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

        valid_protos = ["https", "http", "email", "email-json", "sqs"]
        super(self.__class__, self).validate()
        if self.properties['Protocol'] not in valid_protos:
            error(self, 'Protocol %s not valid. Not in %s' % (
                self.properties['Protocol'],
                valid_protos
            ))

        return True


class TopicPolicy(sns.TopicPolicy):
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


class Topic(sns.Topic):
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
    'Subscription',
    'Topic',
    'TopicPolicy',
]
