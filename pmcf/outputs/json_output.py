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

from troposphere import Base64, GetAZs, Join, Ref, Template

from pmcf.outputs.base_output import BaseOutput
from pmcf.resources.aws import *

import logging

LOG = logging.getLogger(__name__)


class JSONOutput(BaseOutput):

    def add_resources(self, provisioner, resources, config):
        LOG.info('Start building template')
        data = Template()
        tags = []
        for tagkey in ['name', 'stage', 'version']:
            tags.append(ec2.Tag(
                key=tagkey.title(),
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
                AvailabilityZones=GetAZs(''),
                HealthCheck=elasticloadbalancing.HealthCheck(
                    'test',
                    HealthyThreshold=3,
                    Interval=5,
                    Target=lb_hc_tgt,
                    Timeout=2,
                    UnhealthyThreshold=3
                ),
                Listeners=listeners
            )
            LOG.debug('Adding lb: %s' % lbs[name].JSONrepr())
            data.add_resource(lbs[name])

        cfg = {'foo': 'bar'}

        sgs = {}
        for sg in resources['secgroup']:
            rules = []
            name = 'sg%s' % sg['name']
            for idx, rule in enumerate(sg['rules']):
                if rule.get('source_group'):
                    rules.append(ec2.SecurityGroupRule(
                        FromPort=rule['from_port'],
                        ToPort=rule['to_port'],
                        IpProtocol=rule['protocol'],
                        SourceSecurityGroupName=rule['source_group'],
                    ))
                else:
                    rules.append(ec2.SecurityGroupRule(
                        FromPort=rule['from_port'],
                        ToPort=rule['to_port'],
                        IpProtocol=rule['protocol'],
                        CidrIp=rule['source_cidr'],
                    ))
            sgs[name] = ec2.SecurityGroup(
                name,
                GroupDescription='security group for %s' % sg['name'],
                SecurityGroupIngress=rules,
                Tags=tags,
            )
            LOG.debug('Adding sg: %s' % sgs[name].JSONrepr())
            data.add_resource(sgs[name])

        for inst in resources['instance']:
            inst_sgs = [Ref(sgs['sg%s' % inst['name']])]
            try:
                inst['sg'].index('default')
                inst_sgs.append('default')
            except ValueError:
                pass
            ud = provisioner.userdata(cfg)
            lc = autoscaling.LaunchConfiguration(
                'LC%s' % inst['name'],
                ImageId=inst['image'],
                InstanceType=inst['type'],
                KeyName=inst['sshKey'],
                InstanceMonitoring=inst['monitoring'],
                SecurityGroups=inst_sgs,
                UserData=Base64(Join(ud, ''))
            )
            LOG.debug('Adding lc: %s' % lc.JSONrepr())
            data.add_resource(lc)
            asgtags = []
            for tagkey in ['name', 'stage', 'version']:
                asgtags.append(autoscaling.Tag(
                    key=tagkey.title(),
                    value=config[tagkey],
                    propogate=True,
                ))
            asg = autoscaling.AutoScalingGroup(
                'ASG%s' % inst['name'],
                AvailabilityZones=GetAZs(''),
                DesiredCapacity=inst['count'],
                LaunchConfigurationName=Ref(lc),
                LoadBalancerNames=[Ref(lbs['ELB%s' % inst['name']])],
                MaxSize=inst['count'],
                MinSize=inst['count'],
                Tags=asgtags
            )
            LOG.debug('Adding asg: %s' % asg.JSONrepr())
            data.add_resource(asg)

        LOG.info('Finished building template')
        indent = None
        if LOG.isEnabledFor(logging.DEBUG):
            indent = 4
        return data.to_json(indent=indent)

    def run(self, data):
        LOG.info('Start running data')
        print data
        LOG.info('Finished running data')


__all__ = [
    JSONOutput,
]
