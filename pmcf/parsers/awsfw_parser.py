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

from pmcf import exceptions
from pmcf.parsers import BaseParser
import xmltodict


class AWSFWParser(BaseParser):

    @staticmethod
    def _listify(data):
        if not isinstance(data, list):
            return [data]
        return data

    @staticmethod
    def _build_hc(hc_xml):
        (protocol, rest) = hc_xml.split(':')
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

    def build_ds(self, ds):
        elbs = self._listify(ds['ELB'])
        for idx, elb in enumerate(elbs):
            lb = {}
            lb['listener'] = []
            for listener in self._listify(elbs[idx]['listener']):
                hc = listener.get('healthCheck',
                                  listener['protocol'] + ':' +
                                  listener['port'])
                lb['listener'].append({
                    'protocol': listener['protocol'],
                    'lb_port': listener['port'],
                    'instance_port': listener['instancePort'],
                    'health_check': self._build_hc(hc),
                })
            self._resources['load_balancer'].append(lb)

        instances = self._listify(ds['instances'])
        for idx, instance in enumerate(instances):
            inst = {}
            inst['image'] = instance['amiId']
            inst['type'] = instance['size']
            inst['count'] = instance['count']
            if instance.get('role') and instance.get('app'):
                inst['provisioner'] = 'awsfw_standalone'
                inst['apps'] = self._listify(instance['app'])
                inst['roles'] = self._listify(instance['role'])

            self._resources['instance'].append(inst)

    def parse(self, config):
        data = xmltodict.parse(config)
        self.build_ds(data['c4farm'])
        print self._resources
        return self._resources


__all__ = [
    AWSFWParser
]
