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

import copy
import logging
import yaml

from pmcf.exceptions import ParserFailure
from pmcf.parsers.base_parser import BaseParser
from pmcf.utils import split_subnets

LOG = logging.getLogger(__name__)


class YamlParser(BaseParser):
    """
    YAML Parser class.

    This is the supported parser class, as it translates almost directly to
    the supported internal schema.
    """

    def _get_value_for_env(self, data, environment, field):
        """
        Searches a dictionary for data for the current environment, and
        returns either a match or the default

        :param data: Dictionary to search
        :type data: dict.
        :param environment: Name of the environment to look for
        :type data: str.
        :raises: :class:`pmcf.exceptions.ParserFailure`
        :returns: variable
        """

        # Don't deal with these
        if isinstance(data, int):
            return data
        if isinstance(data, str):
            return data
        if isinstance(data, list):
            return data

        if data.get(environment, None) is not None:
            return data[environment]
        if data.get('default', None) is not None:
            return data['default']
        raise ParserFailure("Can't find environment-specific data for %s" %
                            field)

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

        for field in ['vpcid', 'defaultsg', 'subnets', 'notify']:
            item = data['config'].get(field, None)
            if item:
                data['config'][field] = self._get_value_for_env(
                    item, args['environment'], field)
        self._stack['config'].update(data['config'])
        if data['config'].get('environments', None):
            self._stack['config'].pop('environments', None)
            if args['environment'] not in data['config']['environments']:
                if args['action'] != 'delete':
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

        for idx, net in enumerate(data['resources'].get('network', [])):
            zones = net['zones']
            netrange = net['netrange']
            netname = net['name']
            net['public'] = net.get('public', True)
            if not net.get('subnets', None):
                subnets = []
                numsubnets = len(zones)
                subcidrs = split_subnets(netrange, numsubnets)
                settings = []
                if net['public']:
                    for z in zones:
                        settings.append('public')
                else:
                    for z in zones:
                        settings.append('private')

                for n in range(0, numsubnets):
                    z = n % len(zones)
                    subnets.append({
                        'cidr': str(subcidrs[n]),
                        'name': "%s-%s-%s" % (netname, zones[z], settings[n]),
                        'public': settings[n] == 'public',
                        'zone': zones[z],
                    })

                data['resources']['network'][idx]['subnets'] = subnets

        for instance in data['resources'].get('instance', []):
            if instance.get('public', None) is None:
                instance['public'] = False

            if instance.get('dns'):
                if not instance['dns'].get('zone', '').endswith('.'):
                    raise ParserFailure("DNS zone must end with '.' on %s" %
                                        instance['name'])

            for field in ['size', 'count', 'min', 'max', 'image', 'sg',
                          'monitoring', 'block_device', 'healthcheck',
                          'subnets']:
                item = instance.get(field, None)
                if item:
                    instance[field] =\
                        self._get_value_for_env(item,
                                                args['environment'],
                                                field)
            item = instance.get('scaling_policy', None)
            if item:
                if instance.get('nat'):
                    raise ParserFailure("instances with ElasticIPs and ",
                                        "ScalingPolicies are not supported")

                instance['scaling_policy'] = self._get_value_for_env(
                    item,
                    args['environment'],
                    'scaling_policy')
                if instance['scaling_policy'] == []:
                    instance.pop('scaling_policy', None)

            if instance['provisioner'].get('args'):
                for field in ['bucket', 'metrics']:
                    item = instance['provisioner']['args'].get(field, None)
                    if item:
                        instance['provisioner']['args'][field] =\
                            self._get_value_for_env(item,
                                                    args['environment'],
                                                    field)

        for lb in data['resources'].get('load_balancer', []):
            for field in ['policy', 'subnets']:
                item = lb.get(field, None)
                if item:
                    lb[field] =\
                        self._get_value_for_env(item,
                                                args['environment'],
                                                field)

        for sg in data['resources'].get('secgroup', []):
            if not sg.get('vpcid', None) and data['config'].get('vpcid'):
                sg['vpcid'] = data['config']['vpcid']

            new_rules = []
            for rule in sg['rules']:
                for field in ['source_group', 'source_cidr']:
                    item = rule.get(field, None)
                    if item:
                        rule[field] =\
                            self._get_value_for_env(item,
                                                    args['environment'],
                                                    field)
                        if isinstance(rule[field], list):
                            saved_list = rule[field]
                            rule[field] = saved_list.pop()
                            for source in saved_list:
                                new_rule = copy.deepcopy(rule)
                                new_rule.update({field: source})
                                new_rules.append(new_rule)
            sg['rules'].extend(new_rules)

        dropped = []
        for idx, sg in enumerate(data['resources'].get('secgroup', [])):
            stages = sg.pop('stages', [])
            if stages:
                if args['environment'] not in stages:
                    LOG.debug('Found secgroup not present in %s: %s' % (
                        args['environment'],
                        sg['name']))
                    dropped.insert(0, idx)
        for drop in dropped:
            data['resources']['secgroup'].pop(drop)

        dropped = []
        for idx, instance in enumerate(data['resources'].get('instance', [])):
            stages = instance.pop('stages', [])
            if stages:
                if args['environment'] not in stages:
                    LOG.debug('Found instance not present in %s: %s' % (
                        args['environment'],
                        instance['name']))
                    dropped.insert(0, idx)
        for drop in dropped:
            data['resources']['instance'].pop(drop)

        self._stack['resources'].update(data['resources'])

        for lb in self._stack['resources']['load_balancer']:
            if data['config'].get('subnets'):
                lb['subnets'] = lb.get('subnets', data['config']['subnets'])
            lb['policy'] = lb.get('policy', [])
            for idx, policy in enumerate(lb['policy']):
                if policy['type'] == 'log_policy':
                    lb['policy'][idx]['policy']['s3prefix'] = "%s/%s" % (
                        args['environment'],
                        policy['policy']['s3prefix'],
                    )

        for instance in self._stack['resources']['instance']:
            if data['config'].get('subnets'):
                instance['subnets'] = instance.get(
                    'subnets',
                    data['config']['subnets'])
                if not data['config'].get('vpcid'):
                    raise ParserFailure("subnets without vpcid is invalid")

            if self._stack['config'].get('notify', None):
                instance['notify'] = instance.get(
                    'notify',
                    self._stack['config']['notify'])

            if not instance.get('provisioner', None):
                if self._stack['config'].get('provisioner', '') ==\
                        'PuppetProvisioner':
                    bucket = self._stack['config'].get(
                        'bucket',
                        self._stack['config']['audit_output'])
                    instance['provisioner'] = {
                        'provider': 'PuppetProvisioner',
                        'args': {
                            'bucket': bucket,
                            'infrastructure': "%s.tar.gz" % instance['name'],
                        }
                    }

            if instance['provisioner'].get('args', {}).get('custom_profile'):
                instance['provisioner']['args']['custom_profile'] =\
                    self._get_value_for_env(
                        instance['provisioner']['args']['custom_profile'],
                        args['environment'],
                        'custom_profile')

            if instance.get('sg', []) == []:
                sgs = self._stack['resources']['secgroup']
                found = instance['name'] in [x['name'] for x in sgs]
                if not found:
                    self._stack['resources']['secgroup'].insert(0, {
                        'name': instance['name'],
                        'rules': []
                    })
                    if data['config'].get('vpcid'):
                        self._stack['resources']['secgroup'][0]['vpcid'] =\
                            data['config']['vpcid']
                    instance['sg'] = instance.get('sg', [])
                    instance['sg'].append(instance['name'])
            if not self._stack['config'].get('nodefaultsg'):
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
