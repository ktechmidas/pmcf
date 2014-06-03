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

import logging
from troposphere import Base64, GetAtt, GetAZs, Output, Ref, Template

from pmcf.exceptions import ProvisionerException
from pmcf.outputs.base_output import BaseOutput
from pmcf.resources.aws import autoscaling, ec2, elasticloadbalancing

LOG = logging.getLogger(__name__)


class JSONOutput(BaseOutput):

    def add_resources(self, provisioner, resources, config):
        LOG.info('Start building template')
        data = Template()
        desc = "%s %s stack" % (config['name'], config['stage'])
        data.add_description(desc)
        data.add_version()

        sgs = {}
        for sg in resources['secgroup']:
            rules = []
            sgname = 'sg%s' % sg['name']
            name = sg['name']
            for idx, rule in enumerate(sg['rules']):
                if rule.get('port'):
                    rule['to_port'] = rule['from_port'] = rule['port']
                if rule.get('source_group'):
                    sg_rule_data = {}
                    if rule['source_group'].startswith('='):
                        if config.get('vpcid', None):
                            sg_rule_data['SourceSecurityGroupId'] =\
                                Ref(sgs[rule['source_group'][1:]])
                        else:
                            sg_rule_data['SourceSecurityGroupName'] =\
                                Ref(sgs[rule['source_group'][1:]])
                    elif rule['source_group'].find('/') != -1:
                        (sg_owner, sg_group) = rule['source_group'].split('/')
                        sg_rule_data['SourceSecurityGroupName'] = sg_group
                        sg_rule_data['SourceSecurityGroupOwnerId'] = sg_owner
                    else:
                        sg_rule_data['SourceSecurityGroupName'] =\
                            rule['source_group']

                    rules.append(ec2.SecurityGroupRule(
                        FromPort=rule['from_port'],
                        ToPort=rule['to_port'],
                        IpProtocol=rule['protocol'],
                        **sg_rule_data
                    ))
                else:
                    rules.append(ec2.SecurityGroupRule(
                        FromPort=rule['from_port'],
                        ToPort=rule['to_port'],
                        IpProtocol=rule['protocol'],
                        CidrIp=rule['source_cidr'],
                    ))
            sgargs = {}
            if config.get('vpcid'):
                sgargs['VpcId'] = config['vpcid']
            sgs[name] = ec2.SecurityGroup(
                sgname,
                GroupDescription='security group for %s' % sg['name'],
                SecurityGroupIngress=rules,
                **sgargs
            )
            LOG.debug('Adding sg: %s' % sgs[name].JSONrepr())
            data.add_resource(sgs[name])

        lbs = {}
        for lb in resources['load_balancer']:
            lb_hc_tgt = lb['healthcheck']['protocol'] + ':' + \
                str(lb['healthcheck']['port'])
            if lb['healthcheck'].get('path'):
                lb_hc_tgt += lb['healthcheck']['path']

            listeners = []
            for listener in lb['listener']:
                kwargs = {
                    'InstancePort': listener['instance_port'],
                    'LoadBalancerPort': listener['lb_port'],
                    'Protocol': listener['protocol']
                }
                if listener.get('instance_protocol'):
                    kwargs['InstanceProtocol'] = listener['instance_protocol']
                if listener.get('sslCert'):
                    kwargs['SSLCertificateId'] = listener['sslCert']
                listeners.append(elasticloadbalancing.Listener(**kwargs))

            name = "ELB" + lb['name']
            elb = {
                'CrossZone': True,
                'AvailabilityZones': GetAZs(''),
                'HealthCheck': elasticloadbalancing.HealthCheck(
                    'test',
                    HealthyThreshold=3,
                    Interval=5,
                    Target=lb_hc_tgt,
                    Timeout=2,
                    UnhealthyThreshold=3
                ),
                'Listeners': listeners
            }
            if lb.get('sg'):
                elb['SecurityGroups'] = []
                for sg in lb['sg']:
                    elb['SecurityGroups'].append(Ref(sgs[sg]))
            for policy in lb['policy']:
                if policy['type'] == 'log_policy':
                    eap = elasticloadbalancing.AccessLoggingPolicy(
                        name,
                        EmitInterval=policy['policy']['emit_interval'],
                        Enabled=policy['policy']['enabled'],
                        S3BucketName=policy['policy']['s3bucket'],
                        S3BucketPrefix=policy['policy']['s3prefix'],
                    )
                    elb['AccessLoggingPolicy'] = eap
            lbs[name] = elasticloadbalancing.LoadBalancer(
                name,
                **elb
            )
            data.add_output(
                Output(
                    "%sDNS" % name,
                    Description="Public DNSName of the %s ELB" % name,
                    Value=GetAtt(lbs[name], "DNSName"),
                )
            )
            LOG.debug('Adding lb: %s' % lbs[name].JSONrepr())
            data.add_resource(lbs[name])

        for inst in resources['instance']:
            cfg = {}
            args = {}
            if inst.get('provisioner'):
                if inst['provisioner']['provider'] != provisioner.provides():
                    raise ProvisionerException('wrong provisoner for '
                                               'instance: %s' %
                                               inst['provisioner']['provider']
                                               )

                if inst['provisioner']['provider'] == 'awsfw_standalone':
                    args = inst['provisioner']['args']
                    cfg['platform_environment'] = config['stage']
                    cred_mapping = {
                        'instance_access': 'AWS_ACCESS_KEY_ID',
                        'instance_secret': 'AWS_SECRET_ACCESS_KEY',
                    }
                    for k, v in cred_mapping.iteritems():
                        if config.get(k, None):
                            cfg[v] = config[k]

            lcargs = {
                'ImageId': inst['image'],
                'InstanceType': inst['size'],
                'KeyName': inst['sshKey'],
                'InstanceMonitoring': inst['monitoring'],
            }
            inst_sgs = []
            for sg in inst['sg']:
                if sgs.get(sg):
                    inst_sgs.append(Ref(sgs[sg]))
                else:
                    inst_sgs.append(sg)
            lcargs['SecurityGroups'] = inst_sgs
            ud = provisioner.userdata(cfg, args)
            if ud is not None:
                lcargs['UserData'] = Base64(ud)

            if inst.get('profile', None):
                lcargs['IamInstanceProfile'] = inst['profile']
            lc = autoscaling.LaunchConfiguration(
                'LC%s' % inst['name'],
                **lcargs
            )
            LOG.debug('Adding lc: %s' % lc.JSONrepr())
            data.add_resource(lc)

            asgtags = [
                autoscaling.Tag(
                    key='Name',
                    value=config['name'] + '::' + inst['name'],
                    propogate=True,
                ),
                autoscaling.Tag(
                    key='App',
                    value=inst['name'],
                    propogate=True,
                )
            ]
            inst['min'] = inst.get('min', inst['count'])
            inst['max'] = inst.get('max', inst['count'])
            asgargs = {
                'AvailabilityZones': GetAZs(''),
                'DesiredCapacity': inst['count'],
                'LaunchConfigurationName': Ref(lc),
                'MaxSize': inst['min'],
                'MinSize': inst['max'],
                'Tags': asgtags
            }
            if inst.get('lb'):
                asgargs['LoadBalancerNames'] = [
                    Ref(lbs["ELB" + inst['lb']])
                ]
            asg = autoscaling.AutoScalingGroup(
                'ASG%s' % inst['name'],
                **asgargs
            )
            LOG.debug('Adding asg: %s' % asg.JSONrepr())
            data.add_resource(asg)

        LOG.info('Finished building template')
        indent = None
        if LOG.isEnabledFor(logging.DEBUG):
            indent = 4
        return data.to_json(indent=indent)

    def run(self, data, metadata={}):
        LOG.info('Start running data')
        print data
        LOG.info('Finished running data')
        return True


__all__ = [
    JSONOutput,
]
