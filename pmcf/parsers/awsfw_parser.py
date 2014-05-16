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

import urllib
import netaddr
import xmltodict
from xml.parsers.expat import ExpatError

from pmcf import exceptions
from pmcf.parsers import BaseParser


class AWSFWParser(BaseParser):

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
            raise exceptions.ParserFailure('Unable to parse healthcheck '
                                           'property')
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
                        raise exceptions.ParserFailure('an HTTPS listener '
                                                       'needs an sslCert')
                    else:
                        lstnr['sslCert'] = urllib.unquote(listener['sslCert'])
                lb['listener'].append(lstnr)
            if elb.get('elb-logging'):
                log_policy = {
                    'emit_interval': elbs[idx]['elb-logging']['emitinterval'],
                    's3bucket': elbs[idx]['elb-logging']['s3bucket'],
                    's3prefix': elbs[idx]['elb-logging']['prefix'],
                    'enabled': True,
                }
            if lb.get('healthcheck', None) is None:
                raise exceptions.ParserFailure('a loadbalancer needs '
                                               'a healthCheck parameter')

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
            fwrules.append(r)
        self._stack['resources']['secgroup'].append({
            'name': inst_name,
            'rules': fwrules
        })

    def build_instances(self, farmname, instances):
        for idx, instance in enumerate(instances):
            inst = {}
            inst['name'] = farmname + '-' + instance['tier']
            inst['image'] = instance['amiId']
            inst['type'] = instance['size']
            inst['count'] = instance['count']
            inst['sg'] = []
            if instance.get('role') and instance.get('app'):
                inst['provisioner'] = {
                    'type': 'awsfw_standalone',
                    'args': {
                        'apps': self._listify(instance['app']),
                        'roles': self._listify(instance['role'])
                    }
                }
            else:
                inst['provisioner'] = {
                    'type': instance['provisioner']['type'],
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

            self._stack['resources']['instance'].append(inst)

    def build_ds(self, ds):

        name_parts = ds['farmName'].split('-')
        self._stack['config'] = {
            'name': name_parts[0],
            'stage': name_parts[1],
            'strategy': 'BLUEGREEN',
            'version': name_parts[2],
        }
        if ds.get('farmOwner'):
            self._stack['config']['owner'] = ds['farmOwner']

        if ds.get('ELB'):
            self.build_lbs(ds['farmName'], self._listify(ds['ELB']))
        if ds.get('instances'):
            self.build_instances(ds['farmName'],
                                 self._listify(ds['instances']))
        if len(self._stack['resources']['instance']) == 0:
            raise exceptions.ParserFailure('Bad stack: no instances')

        for instance in self._stack['resources']['instance']:
            if ds.get('key'):
                instance['sshKey'] = ds['key']
            if ds.get('cloudwatch'):
                instance['monitoring'] = ds['cloudwatch']
            if ds.get('appBucket'):
                instance['provisioner']['args']['appBucket'] = ds['appBucket']
            if ds.get('roleBucket'):
                instance['provisioner']['args']['roleBucket'] = ds['appBucket']
            # The XML declaration <noDefaultSG/> becomes:
            # { 'noDefaultSG': None } so a normal
            # if ds.get('noDefaultSG') returns 'None' which evaluates to false
            if ds.get('noDefaultSG', 'nothere') == 'nothere':
                instance['sg'].append('default')

    def parse(self, config):
        try:
            data = xmltodict.parse(config)
        except ExpatError, e:
            raise exceptions.ParserFailure(e.message)

        self.build_ds(data['c4farm'])
        return self._stack


__all__ = [
    AWSFWParser
]
