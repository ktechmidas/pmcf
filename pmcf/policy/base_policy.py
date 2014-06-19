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
..  module:: pmcf.policy.base_policy
    :platform: Unix
    :synopsis: module containing abstract base class for policy classes

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import abc
import logging

LOG = logging.getLogger(__name__)


class BasePolicy(object):
    """
    Abstract base class for policy classes.

    The PMCF Policy classes are responsible for constraining the available
    resource options and for setting resource defaults.

    Only provides an interface, and can not be used directly
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def validate_resource(self, resource_type, resource_data):
        """
        Validates resource against local policy.

        :param resource_type: Type of resource to validate
        :type resource_type: str.
        :param resource_data: Resource to validate
        :type resource_data: dict.
        :raises: :class:`NotImplementedError`
        :returns: dict
        """

        raise NotImplementedError


__all__ = [
    BasePolicy,
]
