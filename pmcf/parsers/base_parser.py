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

import abc
import logging
import jsonschema
import yaml

from pmcf.exceptions import ParserFailure
from pmcf.schema.base import schema as base_schema
from pmcf.schema.instance import schema as instance_schema

LOG = logging.getLogger(__name__)


class BaseParser(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._stack = {
            'resources': {
                'instance': [],
                'secgroup': [],
                'load_balancer': [],
                'db': [],
                'cdn': [],
            },
            'config': {}
        }

    @abc.abstractmethod
    def parse(self, config, args={}):
        raise NotImplementedError

    def parse_file(self, fname, args={}):
        try:
            with open(fname) as fd:
                self.parse(fd.read(), args)
        except IOError, e:
            raise ParserFailure(str(e))

    def validate(self):
        LOG.info('Start validation of stack')
        if len(self._stack['resources']['instance']) == 0:
            raise ParserFailure('Bad stack: no instances')

        try:
            jsonschema.validate(self._stack, yaml.load(base_schema))
            for instance in self._stack['resources']['instance']:
                jsonschema.validate(instance, yaml.load(instance_schema))
        except jsonschema.exceptions.ValidationError, e:
            raise ParserFailure(str(e))
        LOG.info('Finished validation of stack')


__all__ = [
    BaseParser,
]
