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
..  module:: pmcf.parsers.awsfw_parser
    :platform: Unix
    :synopsis: module containing parsers for PMCF

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import logging
import netaddr
import urllib
import xmltodict
from xml.parsers.expat import ExpatError

from pmcf.exceptions import ParserFailure
from pmcf.parsers.base_parser import BaseParser

LOG = logging.getLogger(__name__)


class AWSFWParser(BaseParser):
    """
    AWSFW-specific parser class.

    Bespoke parser for legacy AWSFW XML format.
    """

    @staticmethod
    def _str_to_bool(string):
        """
        Turns a string 'true' into the python True, and anything else into
        False

        :param string: String to check
        :type string: str.
        :returns: boolean
        """

        if isinstance(string, str):
            return string.lower() == 'true'
        return False

    @staticmethod
    def _listify(data):
        """
        Turns anything except a list into a list.  If passed a list, will
        return it unchanged.  Anything else will be returned as a list with
        one element.

        This is necessary because because xmltodict does not produce
        consistent output.  Given::

        <foo>
          <bar>baz</bar>
          <bar>qux</bar>
        </foo>

        xmltodict will return a data structure of::

        {'foo': {'bar': ['baz, 'qux']}}

        But:

        <foo>
          <bar>baz</bar>
        </foo>

        xmltodict will return a data structure of::

        {'foo': {'bar': 'baz}}

        In order to consistently access subelements, it's safer to always
        transform them into a list.

        :param data: Datatype to check.
        :type data: object.
        :returns: list
        """

        if not isinstance(data, list):
            return [data]
        return data

    @staticmethod
    def _build_hc(hc_xml):
        """
        Builds internal representation of a loadbalancer healthcheck from the
        AWSFW native XML structure.

        :param hc_xml: Healthcheck structure from XML
        :type hc_xml: dict.
        :raises: :class:`pmcf.exceptions.ParserFailure`
        :returns: dict
        """

        try:
            (protocol, rest) = hc_xml.split(':')
        except ValueError:
            LOG.debug('Expected PROTO:port[/path]')
            raise ParserFailure('Unable to parse healthcheck property')
        if protocol.upper() in ['HTTP', 'HTTPS']:
            port = rest.split('/')[0]
            path = rest[len(port):]
        else:
            port = rest
            path = None
        hc = {
            'protocol': protocol.upper(),
            'port': int(port)
        }
        if path:
            hc['path'] = path
        LOG.debug('Found healthcheck: %s' % hc)
        return hc

    def build_lbs(self, farmname, elbs):
        """
        Builds internal representation of loadbalancers from the
        AWSFW native XML structure.

        :param farmname: Name of current farm
        :type farmname: string.
        :param elbs: list of ELBs to parse
        :type elbs: list.
        :raises: :class:`pmcf.exceptions.ParserFailure`
        :returns: list
        """

        for idx, elb in enumerate(elbs):
            lb = {
                'listener': [],
                'policy': []
            }
            for listener in self._listify(elbs[idx]['listener']):
                hc = listener.get('healthCheck')
                if hc:
                    lb['healthcheck'] = self._build_hc(hc)
                lstnr = {
                    'protocol': listener['protocol'],
                    'lb_port': int(listener['port']),
                    'instance_port': int(listener['instancePort']),
                }
                if listener['protocol'].upper() == 'HTTPS':
                    if not listener.get('sslCert'):
                        raise ParserFailure('an HTTPS listener needs an '
                                            'sslCert')
                    else:
                        lstnr['sslCert'] = urllib.unquote(listener['sslCert'])
                if listener.get('instance_protocol'):
                    lstnr['instance_protocol'] = listener['instance_protocol']
                else:
                    if listener['protocol'].upper() in ['HTTP', 'HTTPS']:
                        lstnr['instance_protocol'] = 'HTTP'
                LOG.debug('Found listener: %s' % lstnr)
                lb['listener'].append(lstnr)
            if elb.get('elb-logging'):
                log_policy = {
                    'emit_interval': int(elb['elb-logging']['emitinterval']),
                    's3bucket': urllib.unquote(elb['elb-logging']['s3bucket']),
                    's3prefix': urllib.unquote(elb['elb-logging']['prefix']),
                    'enabled': True,
                }
                LOG.debug('Found log_policy: %s' % log_policy)
                lb['policy'].append({
                    'type': 'log_policy',
                    'policy': log_policy
                })

            LOG.debug('Found loadbalancer: %s' % lb)
            if elb.get('suffix'):
                lb['name'] = elb['suffix']
            else:
                lb['name'] = farmname.replace('-', '')
            self._stack['resources']['load_balancer'].append(lb)
        return self._stack['resources']['load_balancer']

    def build_fw(self, inst_name, rules):
        """
        Builds internal representation of firewall rules from the
        AWSFW native XML structure.

        :param inst_name: Name of current instance
        :type inst_name: string.
        :param rules: list of rules to parse
        :type rules: list.
        :raises: :class:`pmcf.exceptions.ParserFailure`
        :returns: list
        """

        fwrules = []
        for rule in rules:
            r = {
                'from_port': int(rule['port']),
                'to_port': int(rule['port']),
                'protocol': rule['protocol'],
            }
            try:
                netaddr.IPNetwork(rule['source'])
                r['source_cidr'] = rule['source']
            except netaddr.AddrFormatError:
                r['source_group'] = rule['source']
            LOG.debug('Found firewall rule: %s' % r)
            fwrules.append(r)
        self._stack['resources']['secgroup'].append({
            'name': inst_name,
            'rules': fwrules
        })
        return self._stack['resources']['secgroup']

    def build_instances(self, farmname, instances):
        """
        Builds internal representation of instances from the
        AWSFW native XML structure.

        :param farmname: Name of current farm
        :type farmname: string.
        :param instance: list of instances to parse
        :type instances: list.
        :raises: :class:`pmcf.exceptions.ParserFailure`
        :returns: list
        """

        for idx, instance in enumerate(instances):
            inst = {}
            if instance.get('cname'):
                inst['name'] = instance['cname']
            else:
                inst['name'] = instance['tier']
            inst['image'] = instance['amiId']
            inst['size'] = instance['size']
            inst['count'] = int(instance['count'])
            inst['sg'] = []
            inst['block_device'] = []
            if instance.get('elb', 'missing') != 'missing':
                if len(self._stack['resources']['load_balancer']) == 1:
                    inst['lb'] =\
                        self._stack['resources']['load_balancer'][0]['name']
                elif len(self._stack['resources']['load_balancer']) > 1:
                    if instance['elb'] is not None:
                        inst['lb'] = instance['elb']
                    else:
                        raise ParserFailure('Bad stack: unclear loadbalancer '
                                            'to instance declaration')
                else:
                    raise ParserFailure('Bad stack: unclear loadbalancer '
                                        'to instance declaration')
            if instance.get('role') and instance.get('app'):
                inst['provisioner'] = {
                    'provider': 'awsfw_standalone',
                    'args': {
                        'apps': self._listify(instance['app']),
                        'roles': self._listify(instance['role'])
                    }
                }
            else:
                inst['provisioner'] = {
                    'provider': instance['provisioner']['provider'],
                    'args': {
                        'apps': self._listify(
                            instance['provisioner']['args']['app']),
                        'roles': self._listify(
                            instance['provisioner']['args']['role'])
                    }
                }
            if instance.get('firewall'):
                self.build_fw(inst['name'],
                              self._listify(instance['firewall']['rule']))
                inst['sg'].append(inst['name'])

            if instance.get('volume'):
                for vol in self._listify(instance['volume']):
                    data = {
                        'size': int(vol['volumeSize']),
                        'device': vol['volumeDevice']
                    }
                    inst['block_device'].append(data)

            LOG.debug('Found instance: %s' % inst)
            self._stack['resources']['instance'].append(inst)
        return self._stack['resources']['instance']

    def build_ds(self, ds, args={}):
        """
        Builds internal representation of data from the
        AWSFW native XML structure.

        :param ds: dictionary created by xmltodict from AWSFW XML
        :type farmname: dict.
        :param args: Configuration parameters
        :type instances: dict.
        :raises: :class:`pmcf.exceptions.ParserFailure`
        :returns: dict
        """

        name_parts = ds['farmName'].split('-')

        self._stack['config'] = {
            'name': name_parts[0],
            'stage': name_parts[1],
            'strategy': 'BLUEGREEN',
            'version': name_parts[2],
            'owner': ds.get('farmOwner', 'gis-channel4@piksel.com')
        }
        if args.get('accesskey') and args.get('secretkey'):
            self._stack['config']['access'] = args['accesskey']
            self._stack['config']['secret'] = args['secretkey']
        if args.get('instance_accesskey') and args.get('instance_secretkey'):
            self._stack['config']['instance_access'] =\
                args['instance_accesskey']
            self._stack['config']['instance_secret'] =\
                args['instance_secretkey']

        if ds.get('ELB'):
            self.build_lbs(ds['farmName'], self._listify(ds['ELB']))
        if ds.get('instances'):
            self.build_instances(ds['farmName'],
                                 self._listify(ds['instances']))

        for instance in self._stack['resources']['instance']:
            if ds.get('key'):
                instance['sshKey'] = ds['key']
            if ds.get('cloudwatch'):
                instance['monitoring'] = self._str_to_bool(ds['cloudwatch'])
            if ds.get('appBucket'):
                instance['provisioner']['args']['appBucket'] = ds['appBucket']
            if ds.get('roleBucket'):
                instance['provisioner']['args']['roleBucket'] = ds['appBucket']
            # The XML declaration <noDefaultSG/> becomes:
            # { 'noDefaultSG': None } so a normal
            # if ds.get('noDefaultSG') returns 'None' which evaluates to false
            if ds.get('noDefaultSG', 'missing') == 'missing':
                instance['sg'].append('default')
        return self._stack

    def parse(self, config, args={}):
        """
        Builds internal representation of data from the
        AWSFW native XML structure.

        :param config: String representation of config from file
        :type config: str.
        :param args: Configuration parameters
        :type instances: dict.
        :raises: :class:`pmcf.exceptions.ParserFailure`
        :returns: dict
        """

        LOG.info('Start parsing farm config')
        try:
            data = xmltodict.parse(config)
        except ExpatError, e:
            raise ParserFailure(e.message)

        self.build_ds(data['c4farm'], args)
        self.validate()
        LOG.debug('stack: %s' % self._stack)
        LOG.info('Finished parsing farm config')
        return self._stack


__all__ = [
    AWSFWParser,
]
