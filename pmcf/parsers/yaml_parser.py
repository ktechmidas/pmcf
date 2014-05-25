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

import logging
import yaml

from pmcf.exceptions import ParserFailure
from pmcf.parsers.base_parser import BaseParser

LOG = logging.getLogger(__name__)


class YamlParser(BaseParser):
    def parse(self, config, args={}):

        LOG.info('Start parsing config')
        try:
            data = yaml.load(config)
        except Exception, e:
            raise ParserFailure(e)

        try:
            self._stack['config'] = {
                'name': data['config']['name'],
                'stage': args['stage']
            }
        except KeyError, e:
            raise ParserFailure(e)

        if args.get('accesskey') and args.get('secretkey'):
            self._stack['config']['access'] = args['accesskey']
            self._stack['config']['secret'] = args['secretkey']
        if args.get('instance_accesskey') and args.get('instance_secretkey'):
            self._stack['config']['instance_access'] =\
                args['instance_accesskey']
            self._stack['config']['instance_secret'] =\
                args['instance_secretkey']
        self._stack['resources'] = data['resources']

        self.validate()
        LOG.debug('stack: %s' % self._stack)
        LOG.info('Finished parsing config')
        return self._stack


__all__ = [
    YamlParser,
]
