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
..  module:: pmcf.outputs.base_output
    :platform: Unix
    :synopsis: module containing output classes for PMCF

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import abc
import logging

LOG = logging.getLogger(__name__)


class BaseOutput(object):
    """
    Abstract base class for output classes.

    Only provides an interface, and can not be used directly
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def add_resources(self, provisioner, resources, config):
        """
        Converts internal data structure into format suitable for interface
        with public and private cloud providers

        :param provisioner: Subclass of :class:`pmcf.provisioners.BaseProvisioner`
        :type configfile: object.
        :param resources: Internal data structure of resources
        :type resources: dict.
        :param config: Config key/value pairs
        :type config: dict.
        :raises: NotImplementedError
        """

        raise NotImplementedError

    @abc.abstractmethod
    def run(self, data, metadata={}):
        """
        Interfaces with public and private cloud providers

        :param data: Stack definition
        :type data: str.
        :param metadata: Additional information for stack launch (tags, etc).
        :type profile_name: dict.
        :raises: NotImplementedError
        """

        raise NotImplementedError


__all__ = [
    BaseOutput,
]
