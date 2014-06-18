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
..  module:: pmcf.parsers.yaml_parser
    :platform: Unix
    :synopsis: module containing YAML parser class

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import logging
import os
import yaml

from pmcf.exceptions import ParserFailure
from pmcf.parsers.base_parser import BaseParser

LOG = logging.getLogger(__name__)


class YamlParser(BaseParser):
    """
    Baseline Parser class.

    This is the supported parser class, as it translates almost directly to
    the supported internal schema.
    """

    def parse(self, config, args={}):
        """
        Builds internal representation of data from the
        YAML representation

        :param config: String representation of config from file
        :type config: str.
        :param args: Configuration parameters
        :type args: dict.
        :raises: :class:`pmcf.exceptions.ParserFailure`
        :returns: dict
        """

        LOG.info('Start parsing config')
        try:
            data = yaml.load(config)
        except Exception, e:
            raise ParserFailure(e)

        try:
            self._stack['config'] = {
                'name': data['config']['name'],
                'environment': args['environment']
            }
        except KeyError, e:
            raise ParserFailure(e)

        self._stack['config'].update(data['config'])
        if data['config'].get('environments', None):
            self._stack['config'].pop('environments', None)
            if args['environment'] not in data['config']['environments']:
                raise ParserFailure('environment %s not in %s' %
                                    (args['environment'],
                                     data['config']['environments']))

        if args.get('accesskey') and args.get('secretkey'):
            self._stack['config']['access'] = args['accesskey']
            self._stack['config']['secret'] = args['secretkey']
        if args.get('instance_accesskey') and args.get('instance_secretkey'):
            self._stack['config']['instance_access'] =\
                args['instance_accesskey']
            self._stack['config']['instance_secret'] =\
                args['instance_secretkey']
        self._stack['resources'].update(data['resources'])

        for lb in self._stack['resources']['load_balancer']:
            lb['policy'] = lb.get('policy', [])
            if lb.get('internal', False):
                if data['config'].get('subnets'):
                    lb['subnets'] = data['config']['subnets']
        for instance in self._stack['resources']['instance']:
            if not instance.get('provisioner', None):
                if self._stack['config'].get('provisioner', '') ==\
                        'PuppetProvisioner':
                    bucket = self._stack['config'].get(
                        'bucket',
                        self._stack['config']['audit_output'])
                    instance['provisioner'] = {
                        'provider': 'PuppetProvisioner',
                        'args': {
                            'name': instance['name'],
                            'bucket': bucket,
                            'infrastructure': "%s.tar.gz" % instance['name'],
                            'profile': os.path.basename(instance.get(
                                'profile',
                                self._stack['config']['profile']))
                        }
                    }
            found = False
            for sg in self._stack['resources']['secgroup']:
                if sg['name'] == instance['name']:
                    found = True
                    break
            if not found:
                self._stack['resources']['secgroup'].insert(0, {
                    'name': instance['name'],
                    'rules': []
                })
                instance['sg'] = instance.get('sg', [])
                instance['sg'].append(instance['name'])
            if not self._stack['config'].get('nodefaultsg'):
                instance['sg'] = instance.get('sg', [])
                if data['config'].get('vpcid') and \
                        data['config'].get('defaultsg'):
                    instance['sg'].append(data['config']['defaultsg'])
                else:
                    instance['sg'].append('default')

        LOG.debug('stack: %s' % self._stack)
        LOG.info('Finished parsing config')
        return self._stack


__all__ = [
    YamlParser,
]
