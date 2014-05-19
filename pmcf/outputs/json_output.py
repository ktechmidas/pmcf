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

        sgs = {}
        for sg in resources['secgroup']:
            name = 'sg%s' % sg['name']
            sgs[name] = ec2.SecurityGroup(
                name,
                GroupDescription='security group for %s' % sg['name'],
                Tags=tags,
            )
            data.add_resource(sgs[name])

            rules = []
            for idx, rule in enumerate(sg['rules']):
                rule_name = 'sg%s%02d' % (sg['name'], idx)
                if rule.get('source_group'):
                    data.add_resource(ec2.SecurityGroupIngress(
                        rule_name,
                        FromPort=rule['from_port'],
                        ToPort=rule['to_port'],
                        IpProtocol=rule['protocol'],
                        SourceSecurityGroupName=rule['source_group'],
                        GroupName=Ref(name)
                    ))
                else:
                    data.add_resource(ec2.SecurityGroupIngress(
                        rule_name,
                        FromPort=rule['from_port'],
                        ToPort=rule['to_port'],
                        IpProtocol=rule['protocol'],
                        CidrIp=rule['source_cidr'],
                        GroupName=Ref(name)
                    ))

        for inst in resources['instance']:
            inst_sgs = [Ref(sgs['sg%s' % inst['name']])]
            try:
                inst['sg'].index('default')
                inst_sgs.append('default')
            except ValueError:
                pass
            lc = autoscaling.LaunchConfiguration(
                'LC%s' % inst['name'],
                IamInstanceProfile='awsfw-provisioner',
                ImageId=inst['image'],
                InstanceType=inst['type'],
                KeyName=inst['sshKey'],
                InstanceMonitoring=inst['monitoring'],
                SecurityGroups=Ref(sgs['sg%s' % inst['name']]),
                UserData=provisioner.userdata(config)
            )
            data.add_resource(lc)
            data.add_resource(autoscaling.AutoScalingGroup(
                'ASG%s' % inst['name'],
                AvailabilityZones=[1, 2, 3],
                DesiredCapacity=inst['count'],
                LaunchConfigurationName=Ref(lc),
                LoadBalancerNames=Ref(lbs['ELB%s' % inst['name']]),
                MaxSize=inst['count'],
                MinSize=inst['count'],
                Tags=tags
            ))

        return data.to_json()

    def run(self, data):
        print data


__all__ = [
    JSONOutput,
]
