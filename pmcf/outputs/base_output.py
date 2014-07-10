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
    :synopsis: module containing abstract base class for output

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import abc
import datetime
import logging

LOG = logging.getLogger(__name__)


class BaseOutput(object):
    """
    Abstract base class for output classes.

    The PMCF Output classes are responsible for converting the internal data
    structure into a format suitable for use with public and private clouds.
    The format is then either printed to stdout or used as part of an API
    call to the cloud provider.

    Only provides an interface, and can not be used directly
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        """
        Constructor method.  Just records start time
        """

        self.start_time = datetime.datetime.utcnow()

    @abc.abstractmethod
    def add_resources(self, resources, config):
        """
        Converts internal data structure into format suitable for interface
        with public and private cloud providers

        :param resources: Internal data structure of resources
        :type resources: dict.
        :param config: Config key/value pairs
        :type config: dict.
        :raises: :class:`NotImplementedError`
        """

        raise NotImplementedError

    @abc.abstractmethod
    def run(self, data, metadata={}, poll=False,
            action='create', upload=False):
        """
        Interfaces with public and private cloud providers

        :param data: Stack definition
        :type data: str.
        :param metadata: Additional information for stack launch (tags, etc).
        :type metadata: dict.
        :param poll: Whether to poll until completion
        :type poll: boolean.
        :param action: Action to take on the stack
        :type action: str.
        :param upload: Whether to upload stack definition to s3 before launch
        :type upload: bool.
        :raises: :class:`NotImplementedError`
        """

        raise NotImplementedError

    @abc.abstractmethod
    def do_audit(self, data, metadata={}):
        """
        Records audit logs for current transaction

        :param data: Stack definition
        :type data: str.
        :param metadata: Additional information for stack launch (tags, etc).
        :type metadata: dict.
        :raises: :class:`NotImplementedError`
        """

        raise NotImplementedError


__all__ = [
    BaseOutput,
]
