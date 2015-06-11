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
    :synopsis: module containing AWSFW parser class

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

        But::

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
        hck = {
            'protocol': protocol.upper(),
            'port': int(port)
        }
        if path:
            hck['path'] = path
        LOG.debug('Found healthcheck: %s', hck)
        return hck

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
            ldb = {
                'listener': [],
                'policy': []
            }
            for listener in self._listify(elbs[idx]['listener']):
                hck = listener.get('healthCheck')
                if hck:
                    ldb['healthcheck'] = self._build_hc(hck)
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
                lstnr['instance_protocol'] = listener.get(
                    'instance_protocol',
                    listener['protocol'].upper()
                )
                if listener.get('instance_protocol'):
                    lstnr['instance_protocol'] = listener['instance_protocol']
                else:
                    if listener['protocol'].upper() in ['HTTP', 'HTTPS']:
                        lstnr['instance_protocol'] = 'HTTP'
                LOG.debug('Found listener: %s', lstnr)
                ldb['listener'].append(lstnr)
            if elb.get('elb-logging'):
                log_policy = {
                    'emit_interval': int(elb['elb-logging']['emitinterval']),
                    's3bucket': urllib.unquote(elb['elb-logging']['s3bucket']),
                    's3prefix': urllib.unquote(elb['elb-logging']['prefix']),
                    'enabled': True,
                }
                LOG.debug('Found log_policy: %s', log_policy)
                ldb['policy'].append({
                    'type': 'log_policy',
                    'policy': log_policy
                })

            LOG.debug('Found loadbalancer: %s', ldb)
            if elb.get('suffix'):
                ldb['name'] = elb['suffix']
            else:
                ldb['name'] = farmname.replace('-', '')
            self._stack['resources']['load_balancer'].append(ldb)
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
            rle = {
                'from_port': int(rule['port']),
                'to_port': int(rule['port']),
                'protocol': rule['protocol'],
            }
            try:
                netaddr.IPNetwork(rule['source'])
                rle['source_cidr'] = rule['source']
            except netaddr.AddrFormatError:
                rle['source_group'] = rule['source']
            LOG.debug('Found firewall rule: %s', rle)
            fwrules.append(rle)
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

        for instance in instances:
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
                        [self._stack['resources']['load_balancer'][0]['name']]
                elif len(self._stack['resources']['load_balancer']) > 1:
                    if instance['elb'] is not None:
                        inst['lb'] = [instance['elb']]
                    else:
                        raise ParserFailure('Bad stack: unclear loadbalancer '
                                            'to instance declaration')
                else:
                    raise ParserFailure('Bad stack: unclear loadbalancer '
                                        'to instance declaration')
            if instance.get('role') and instance.get('app'):
                inst['provisioner'] = {
                    'provider': 'AWSFWProvisioner',
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

            LOG.debug('Found instance: %s', inst)
            self._stack['resources']['instance'].append(inst)
        return self._stack['resources']['instance']

    def build_ds(self, dat, args=None):
        """
        Builds internal representation of data from the
        AWSFW native XML structure.

        :param dat: dictionary created by xmltodict from AWSFW XML
        :type dat: dict.
        :param args: Configuration parameters
        :type args: dict.
        :raises: :class:`pmcf.exceptions.ParserFailure`
        :returns: dict
        """

        args = args or {}
        name_parts = dat['farmName'].split('-')

        self._stack['config'] = {
            'name': name_parts[0],
            'environment': name_parts[1],
            'strategy': 'BlueGreen',
            'version': name_parts[2],
            'owner': dat.get('farmOwner', 'gis-channel4@piksel.com')
        }
        try:
            self._stack['config']['generation'] = name_parts[3]
        except IndexError:
            pass
        if args.get('accesskey') and args.get('secretkey'):
            self._stack['config']['access'] = args['accesskey']
            self._stack['config']['secret'] = args['secretkey']
        if args.get('instance_accesskey') and args.get('instance_secretkey'):
            self._stack['config']['instance_accesskey'] =\
                args['instance_accesskey']
            self._stack['config']['instance_secretkey'] =\
                args['instance_secretkey']

        if dat.get('ELB'):
            self.build_lbs(dat['farmName'], self._listify(dat['ELB']))
        if dat.get('instances'):
            self.build_instances(dat['farmName'],
                                 self._listify(dat['instances']))

        for inst in self._stack['resources']['instance']:
            inst['provisioner']['args']['platform_environment'] =\
                self._stack['config']['environment']
            if self._stack['config'].get('instance_accesskey'):
                inst['provisioner']['args']['AWS_ACCESS_KEY_ID'] =\
                    self._stack['config']['instance_accesskey']
            if self._stack['config'].get('instance_secretkey'):
                inst['provisioner']['args']['AWS_SECRET_ACCESS_KEY'] =\
                    self._stack['config']['instance_secretkey']
            if dat.get('key'):
                inst['sshKey'] = dat['key']
            if dat.get('cloudwatch'):
                inst['monitoring'] = self._str_to_bool(dat['cloudwatch'])
            if dat.get('appBucket'):
                inst['provisioner']['args']['appbucket'] = dat['appBucket']
            if dat.get('roleBucket'):
                inst['provisioner']['args']['rolebucket'] = dat['appBucket']
            # The XML declaration <noDefaultSG/> becomes:
            # { 'noDefaultSG': None } so a normal
            # if dat.get('noDefaultSG') returns 'None' which evaluates to false
            if dat.get('noDefaultSG', 'missing') == 'missing':
                inst['sg'].append('default')
        return self._stack

    def parse(self, config, args=None):
        """
        Builds internal representation of data from the
        AWSFW native XML structure.

        :param config: String representation of config from file
        :type config: str.
        :param args: Configuration parameters
        :type args: dict.
        :raises: :class:`pmcf.exceptions.ParserFailure`
        :returns: dict
        """

        LOG.info('Start parsing farm config')
        args = args or {}
        try:
            data = xmltodict.parse(config)
        except ExpatError, exc:
            raise ParserFailure(exc.message)

        self.build_ds(data['c4farm'], args)
        LOG.debug('stack: %s', self._stack)
        LOG.info('Finished parsing farm config')
        return self._stack


__all__ = [
    'AWSFWParser',
]
