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
..  module:: pmcf.outputs.json_output
    :platform: Unix
    :synopsis: module containing JSON output class for PMCF

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import logging
from troposphere import Base64, GetAtt, GetAZs, Output, Ref, Template

from pmcf.outputs.base_output import BaseOutput
from pmcf.resources.aws import autoscaling, ec2, elasticloadbalancing
from pmcf.resources.aws import cloudformation as cfn
from pmcf.utils import import_from_string

LOG = logging.getLogger(__name__)


class JSONOutput(BaseOutput):

    def add_resources(self, resources, config):
        """
        Creates JSON-formatted string representation of stack resourcs

        :param resources: Internal data structure of resources
        :type resources: dict.
        :param config: Config key/value pairs
        :type config: dict.
        :returns: string
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        """

        LOG.info('Start building template')
        data = Template()
        desc = "%s %s stack" % (config['name'], config['environment'])
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
            if lb.get('internal', False) and lb.get('subnets'):
                elb['Scheme'] = 'internal'
                elb['Subnets'] = lb['subnets']
            else:
                elb['AvailabilityZones'] = GetAZs('')
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
            ud = None
            ci = None
            if inst.get('provisioner'):
                args = inst['provisioner']['args']
                provider = inst['provisioner']['provider']
                provisioner = import_from_string('pmcf.provisioners',
                                                 provider)()
                if inst['provisioner']['provider'] != 'AWSFWProvisioner':
                    waithandle = cfn.WaitConditionHandle(
                        "%sHandle" % inst['name'],
                    )
                    args['WaitHandle'] = waithandle
                    data.add_resource(waithandle)
                    data.add_resource(cfn.WaitCondition(
                        "%sWait" % inst['name'],
                        DependsOn="ASG%s" % inst['name'],
                        Handle=Ref(waithandle),
                        Count=inst['count'],
                        Timeout=3600
                    ))
                ud = provisioner.userdata(args)
                ci = provisioner.cfn_init(args)

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
            if ud is not None:
                lcargs['UserData'] = Base64(ud)
            if ci is not None:
                lcargs['Metadata'] = ci

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
        """
        Prints out stack definition as json-formatted string

        :param data: Stack definition
        :type data: str.
        :param metadata: Additional information for stack launch (tags, etc).
        :type metadata: dict.
        :returns: boolean
        """

        LOG.info('Start running data')
        print data
        LOG.info('Finished running data')
        self.do_audit(data, metadata)
        return True

    def do_audit(self, data, metadata={}):
        """
        Records audit logs for current transaction

        :param data: Stack definition
        :type data: str.
        :param metadata: Additional information for stack launch (tags, etc).
        :type metadata: dict.
        """

        pass


__all__ = [
    JSONOutput,
]
