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
..  module:: pmcf.parsers.base_parser
    :platform: Unix
    :synopsis: module containing abstract base parser class

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import abc
import logging
import jsonschema
import yaml

from pmcf.exceptions import ParserFailure
from pmcf.schema.base import schema as base_schema

LOG = logging.getLogger(__name__)


class BaseParser(object):
    """
    Abstract base class for parser classes.

    Only provides an interface, and can not be used directly
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._stack = {
            'resources': {
                'instance': [],
                'secgroup': [],
                'load_balancer': [],
                'db': [],
                'cdn': [],
                'role': [],
            },
            'config': {}
        }

    @abc.abstractmethod
    def parse(self, config, args={}):
        """
        Method signature for parsing file contents into internal
        representation of data.

        :param config: String representation of config from file
        :type config: str.
        :param args: Configuration parameters
        :type args: dict.
        :raises: :class:`NotImplementedError`
        :returns: dict.
        """

        raise NotImplementedError

    def stack(self):
        """
        Accessor method for internal data storage.

        :returns: dict.
        """

        return self._stack

    def parse_file(self, fname, args={}):
        """
        Wrapper method for :py:meth:`parse` to pass in file contents

        :param fname: Filename
        :type fname: str.
        :param args: Configuration parameters
        :type args: dict.
        :raises: :class:`pmcf.exceptions.ParserFailure`
        :returns: dict.
        """

        try:
            with open(fname) as fd:
                return self.parse(fd.read(), args)
        except IOError, e:
            raise ParserFailure(str(e))

    def validate(self):
        """
        Validate resulting data structure against the internal
        :class:`pmcf.schema.base_schema.BaseSchema schema`

        :raises: :class:`pmcf.exceptions.ParserFailure`
        """
        LOG.info('Start validation of stack')
        try:
            jsonschema.validate(self._stack, yaml.load(base_schema))
        except jsonschema.exceptions.ValidationError, e:
            raise ParserFailure(str(e))
        LOG.info('Finished validation of stack')


__all__ = [
    BaseParser,
]
