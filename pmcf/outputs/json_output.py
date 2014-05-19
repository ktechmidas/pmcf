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

from troposphere import Ref, Template

from pmcf.outputs.base_output import BaseOutput
from pmcf.resources.aws import *

import logging

LOG = logging.getLogger(__name__)


class JSONOutput(BaseOutput):

    def add_resources(self, provisioner, resources, config):
        data = Template()
        tags = []
        for tagkey in ['name', 'stage', 'version']:
            tags.append(ec2.Tag(
                key=tagkey,
                value=config[tagkey]
            ))

        lbs = {}
        for lb in resources['load_balancer']:
            lb_hc_tgt = lb['healthcheck']['protocol'] + ':' + \
                lb['healthcheck']['port']
            if lb['healthcheck'].get('path'):
                lb_hc_tgt += lb['healthcheck']['path']

            listeners = []
            for listener in lb['listener']:
                listeners.append(elasticloadbalancing.Listener(
                    InstancePort=listener['instance_port'],
                    InstanceProtocol=listener['protocol'],
                    LoadBalancerPort=listener['lb_port'],
                    Protocol=listener['protocol']
                ))

            name = "ELB" + lb['name']
            lbs[name] = elasticloadbalancing.LoadBalancer(
                "ELB" + lb['name'],
                CrossZone=True,
                HealthCheck=elasticloadbalancing.HealthCheck(
                    'test',
                    HealthyThreshold=3,
                    Interval=5,
                    Target=lb_hc_tgt,
                    Timeout=5,
                    UnhealthyThreshold=3
                ),
                Listeners=listeners
            )
            data.add_resource(lbs[name])

        config = {'foo': 'bar'}
        for inst in resources['instance']:
            for c in range(1, int(inst['count'])):
                data.add_resource(ec2.Instance(
                    'test%02d' % c,
                    IamInstanceProfile='awsfw-provisioner',
                    ImageId=inst['image'],
                    InstanceType=inst['type'],
                    KeyName=inst['sshKey'],
                    Monitoring=inst['monitoring'],
                    SecurityGroups=inst['sg'],
                    Tags=tags,
                    UserData=provisioner.userdata(config)
                ))
        return data.to_json()

    def run(self, data):
        print data


__all__ = [
    JSONOutput,
]
