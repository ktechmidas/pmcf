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

import datetime
import logging
import netaddr
import os
import urllib
import xmltodict
from xml.parsers.expat import ExpatError

from pmcf.exceptions import ParserFailure
from pmcf.parsers.base_parser import BaseParser


LOG = logging.getLogger(__name__)


class AWSFWParser(BaseParser):

    @staticmethod
    def _str_to_bool(string):
        return string.lower() == 'true'

    @staticmethod
    def _listify(data):
        if not isinstance(data, list):
            return [data]
        return data

    @staticmethod
    def _build_hc(hc_xml):
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
            'port': port
        }
        if path:
            hc['path'] = path
        LOG.debug('Found healthcheck: %s' % hc)
        return hc

    def build_lbs(self, farmname, elbs):
        for idx, elb in enumerate(elbs):
            lb = {}
            lb['listener'] = []
            for listener in self._listify(elbs[idx]['listener']):
                hc = listener.get('healthCheck')
                if hc:
                    lb['healthcheck'] = self._build_hc(hc)
                lstnr = {
                    'protocol': listener['protocol'],
                    'lb_port': listener['port'],
                    'instance_port': listener['instancePort'],
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
                    'emit_interval': elb['elb-logging']['emitinterval'],
                    's3bucket': urllib.unquote(elb['elb-logging']['s3bucket']),
                    's3prefix': urllib.unquote(elb['elb-logging']['prefix']),
                    'enabled': True,
                }
                LOG.debug('Found log_policy: %s' % log_policy)
                lb['logging'] = log_policy
            if lb.get('healthcheck', None) is None:
                raise ParserFailure('a loadbalancer needs a healthCheck '
                                    'parameter')

            LOG.debug('Found loadbalancer: %s' % lb)
            if elb.get('suffix'):
                lb['name'] = elb['suffix']
            else:
                lb['name'] = farmname.replace('-', '')
            self._stack['resources']['load_balancer'].append(lb)

    def build_fw(self, inst_name, rules):
        fwrules = []
        for rule in rules:
            r = {
                'from_port': rule['port'],
                'to_port': rule['port'],
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

    def build_instances(self, farmname, instances):
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
                        'size': vol['volumeSize'],
                        'device': vol['volumeDevice']
                    }
                    inst['block_device'].append(data)

            LOG.debug('Found instance: %s' % inst)
            self._stack['resources']['instance'].append(inst)

    def build_ds(self, ds, args={}):
        name_parts = ds['farmName'].split('-')

        self._stack['config'] = {
            'name': name_parts[0],
            'stage': name_parts[1],
            'strategy': 'BLUEGREEN',
            'version': name_parts[2],
        }
        review_date = (datetime.date.today() +
                       datetime.timedelta(6*365/12)).isoformat()
        self._stack['tags'] = {
            'Project': name_parts[0],
            'Environment': name_parts[1],
            'CodeVersion': name_parts[2],
            'Farm': ds['farmName'],
            'ReviewDate': review_date,
            'Owner': ds.get('farmOwner', 'gis-channel4@piksel.com')
        }
        if args.get('accesskey') and args.get('secretkey'):
            self._stack['config']['access'] = args['accesskey']
            self._stack['config']['secret'] = args['secretkey']
        if args.get('instance_accesskey') and args.get('instance_secretkey'):
            self._stack['config']['instance_access'] =\
                args['instance_accesskey']
            self._stack['config']['instance_secret'] =\
                args['instance_secretkey']
        if ds.get('farmOwner'):
            self._stack['config']['owner'] = ds['farmOwner']

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

    def parse(self, config, args={}):
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
