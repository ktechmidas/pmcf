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
    :synopsis: module containing JSON output class

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import json
import logging
import re
from signal import signal, SIGPIPE, SIG_DFL
from troposphere import Base64, GetAtt, GetAZs, Output, Ref, Template

from pmcf.outputs.base_output import BaseOutput
from pmcf.resources.aws import autoscaling, ec2, iam, elasticloadbalancing
from pmcf.resources.aws import elasticache
from pmcf.resources.aws import cloudformation as cfn
from pmcf.resources.aws import cloudwatch, kinesis, route53, sqs
from pmcf.utils import import_from_string

LOG = logging.getLogger(__name__)


class JSONOutput(BaseOutput):
    """
    Cloudformation JSON output class.

    This class creates JSON output suitable for use with the AWS
    cloudformation API, but does not itself make use of the API.
    """

    def _add_caches(self, data, caches, config, sgs):
        """
        Iterates and creates AWS Elasticache

        :param data: Template object
        :type data: :class:`troposphere.Template`
        :param caches: list of cache definitions
        :type caches: list.
        :param config: Config key/value pairs
        :type config: dict.
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        """

        if len(caches) > 0:
            data.add_resource(elasticache.SubnetGroup(
                "CacheSubnetGroup%s" % config['name'],
                Description="Subnet Group for %s" % config['name'],
                SubnetIds=config['subnets']
            ))

        for cache in caches:
            cache_data = {
                "CacheNodeType": cache['size'],
                "ClusterName": "%s%s" % (
                    cache['name'],
                    config['environment']),
                "CacheSubnetGroupName":
                    Ref("CacheSubnetGroup%s" % config['name']),
                "Engine": cache['type'],
                "NumCacheNodes": cache['count'],
            }
            cache_sgs = []
            for secg in cache['sg']:
                if sgs.get(secg):
                    cache_sgs.append(Ref(sgs[secg]))
                else:
                    cache_sgs.append(secg)
            cache_data['VpcSecurityGroupIds'] = cache_sgs

            if cache['params'].get('params', {}) != {}:
                data.add_resource(elasticache.ParameterGroup(
                    "CacheParams%s" % cache['name'],
                    Description='Cache ParameterGroup for %s' % cache['name'],
                    Properties=cache['params']['params'],
                    CacheParameterGroupFamily=cache['params']['name'],
                ))
                cache_data['CacheParameterGroupName'] =\
                    Ref("CacheParams%s" % cache['name'])
            else:
                cache_data['CacheParameterGroupName'] =\
                    cache['params']['name']

            data.add_resource(elasticache.CacheCluster(
                "Cache%s" % cache['name'],
                **cache_data
            ))

    def _add_streams(self, data, streams, config):
        """
        Iterates and creates AWS SQS queues

        :param data: Template object
        :type data: :class:`troposphere.Template`
        :param queues: list of queue definitions
        :type queues: list.
        :param config: Config key/value pairs
        :type config: dict.
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        """

        for stream in streams:
            data.add_resource(kinesis.Stream(
                "Stream%s" % stream['name'],
                ShardCount=stream['shards'],
            ))

    def _add_queues(self, data, queues, config):
        """
        Iterates and creates AWS SQS queues

        :param data: Template object
        :type data: :class:`troposphere.Template`
        :param queues: list of queue definitions
        :type queues: list.
        :param config: Config key/value pairs
        :type config: dict.
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        """

        for queue in queues:
            data.add_resource(sqs.Queue(
                "SQS%s" % queue['name'],
                QueueName=queue['name'],
                MessageRetentionPeriod=queue.get('retention', 60),
            ))

    def _add_nets(self, data, nets, config):
        """
        Iterates and creates AWS VPC networks

        :param data: Template object
        :type data: :class:`troposphere.Template`
        :param nets: list of network definitions
        :type nets: list.
        :param config: Config key/value pairs
        :type config: dict.
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        """

        for net in nets:
            subnet_types = set()
            for idx, subnet in enumerate(net['subnets']):
                if subnet['public']:
                    subnet_types.add('public')
                else:
                    subnet_types.add('private')

            data.add_resource(ec2.VPC(
                "VPC%s" % net['name'],
                EnableDnsSupport=True,
                EnableDnsHostnames=True,
                CidrBlock=net['netrange'],
                Tags=[
                    {'Key': 'Name',
                     'Value': net['name']},
                ]))
            data.add_resource(ec2.RouteTable(
                "RT%s" % net['name'],
                VpcId=Ref("VPC%s" % net['name']),
                Tags=[
                    {'Key': 'Name',
                     'Value': net['name']},
                ]))
            if len(subnet_types) > 1:
                data.add_resource(ec2.RouteTable(
                    "RT%spublic" % net['name'],
                    VpcId=Ref("VPC%s" % net['name']),
                    Tags=[
                        {'Key': 'Name',
                         'Value': "%spublic" % net['name']},
                    ]))

            if net['public']:
                data.add_resource(ec2.InternetGateway(
                    "IG%s" % net['name'],
                    Tags=[
                        {'Key': 'Name',
                         'Value': net['name']},
                    ]))
                data.add_resource(ec2.VPCGatewayAttachment(
                    "VPCIG%s" % net['name'],
                    VpcId=Ref("VPC%s" % net['name']),
                    InternetGatewayId=Ref("IG%s" % net['name'])
                ))

                if len(subnet_types) > 1:
                    data.add_resource(ec2.Route(
                        "DefaultRoute%spublic" % net['name'],
                        DependsOn="VPCIG%s" % net['name'],
                        RouteTableId=Ref("RT%spublic" % net['name']),
                        DestinationCidrBlock="0.0.0.0/0",
                        GatewayId=Ref("IG%s" % net['name']),
                    ))

                else:
                    data.add_resource(ec2.Route(
                        "DefaultRoute%s" % net['name'],
                        DependsOn="VPCIG%s" % net['name'],
                        RouteTableId=Ref("RT%s" % net['name']),
                        DestinationCidrBlock="0.0.0.0/0",
                        GatewayId=Ref("IG%s" % net['name']),
                    ))

            if net.get('vpn', None):
                data.add_resource(ec2.VPNGateway(
                    "%sVPNGW" % (net['name']),
                    Type="ipsec.1",
                    Tags=[
                        {'Key': 'Name',
                         'Value': net['name']},
                    ]
                ))
                data.add_resource(ec2.VPCGatewayAttachment(
                    "VPCVPNGW%s" % net['name'],
                    VpcId=Ref("VPC%s" % net['name']),
                    VpnGatewayId=Ref("%sVPNGW" % net['name'])
                ))
                data.add_resource(ec2.VPNGatewayRoutePropagation(
                    "VGRP%s" % net['name'],
                    DependsOn="VPCVPNGW%s" % net['name'],
                    RouteTableIds=[Ref("RT%s" % net['name'])],
                    VpnGatewayId=Ref("%sVPNGW" % net['name'])
                ))
                if len(subnet_types) > 1:
                    data.add_resource(ec2.VPNGatewayRoutePropagation(
                        "VGRP%spublic" % net['name'],
                        DependsOn="VPCVPNGW%s" % net['name'],
                        RouteTableIds=[Ref("RT%spublic" % net['name'])],
                        VpnGatewayId=Ref("%sVPNGW" % net['name'])
                    ))

            for idx, vpn in enumerate(net.get('vpn', [])):
                data.add_resource(ec2.CustomerGateway(
                    "%sCG%s" % (net['name'], idx),
                    Type="ipsec.1",
                    BgpAsn=vpn['asn'],
                    IpAddress=vpn['ip'],
                    Tags=[
                        {'Key': 'Name',
                         'Value': net['name']},
                    ]
                ))
                data.add_resource(ec2.VPNConnection(
                    "%sVPNC%s" % (net['name'], idx),
                    DependsOn="VPCVPNGW%s" % net['name'],
                    Type='ipsec.1',
                    CustomerGatewayId=Ref("%sCG%s" % (net['name'], idx)),
                    VpnGatewayId=Ref("%sVPNGW" % net['name'])
                ))

            for route in net.get('routes', []):
                route_ref = {
                    'RouteTableId': Ref("RT%s" % net['name']),
                    'DestinationCidrBlock': route['cidr'],
                }
                if route['gateway'].startswith('='):
                    route_ref['VpcPeeringConnectionId'] = Ref(
                        "%s%sPeering" % (net['name'], route['gateway'][1:]))
                else:
                    route_ref['GatewayId'] = route['gateway']

                data.add_resource(ec2.Route(
                    "Route%s%s" % (
                        route['cidr'].replace('.', '').replace('/', ''),
                        net['name']),
                    **route_ref
                ))
                if len(subnet_types) > 1:
                    route_ref['RouteTableId'] = Ref("RT%spublic" % net['name'])
                    data.add_resource(ec2.Route(
                        "Route%s%spublic" % (
                            route['cidr'].replace('.', '').replace('/', ''),
                            net['name']),
                        **route_ref
                    ))

            for peer in net.get('peers', []):
                other_net = [n for n in nets
                             if n['name'] == peer['peerid'][1:]][0]
                other_subnet_types = set()
                for idx, subnet in enumerate(other_net['subnets']):
                    if bool(subnet['public']):
                        other_subnet_types.add('public')
                    else:
                        other_subnet_types.add('private')
                data.add_resource(ec2.VPCPeeringConnection(
                    "%s%sPeering" % (peer['peerid'][1:], net['name']),
                    VpcId=Ref("VPC%s" % net['name']),
                    PeerVpcId=Ref("VPC%s" % peer['peerid'][1:])
                ))
                data.add_resource(ec2.Route(
                    "Route%s%s" % (peer['peerid'][1:], net['name']),
                    RouteTableId=Ref("RT%s" % net['name']),
                    DestinationCidrBlock=other_net['netrange'],
                    VpcPeeringConnectionId=Ref(
                        "%s%sPeering" % (peer['peerid'][1:], net['name']))
                ))
                data.add_resource(ec2.Route(
                    "Route%s%s" % (net['name'], peer['peerid'][1:]),
                    RouteTableId=Ref("RT%s" % other_net['name']),
                    DestinationCidrBlock=net['netrange'],
                    VpcPeeringConnectionId=Ref(
                        "%s%sPeering" % (peer['peerid'][1:], net['name']))
                ))

                if len(other_subnet_types) > 1:
                    data.add_resource(ec2.Route(
                        "Route%s%spublic" % (peer['peerid'][1:], net['name']),
                        RouteTableId=Ref("RT%spublic" % other_net['name']),
                        DestinationCidrBlock=net['netrange'],
                        VpcPeeringConnectionId=Ref(
                            "%s%sPeering" % (peer['peerid'][1:], net['name']))
                    ))

            for idx, subnet in enumerate(net['subnets']):
                data.add_resource(ec2.Subnet(
                    "%sSubnet%s" % (net['name'], idx),
                    VpcId=Ref("VPC%s" % net['name']),
                    AvailabilityZone=subnet['zone'],
                    CidrBlock=subnet['cidr'],
                    Tags=[
                        {'Key': 'Name',
                         'Value': subnet['name']},
                        {'Key': 'Public',
                         'Value': subnet['public']},
                    ]))
                if len(subnet_types) > 1 and subnet['public']:
                    data.add_resource(ec2.SubnetRouteTableAssociation(
                        "%sSRTA%s" % (net['name'], idx),
                        SubnetId=Ref("%sSubnet%s" % (net['name'], idx)),
                        RouteTableId=Ref("RT%spublic" % net['name']),
                    ))
                else:
                    data.add_resource(ec2.SubnetRouteTableAssociation(
                        "%sSRTA%s" % (net['name'], idx),
                        SubnetId=Ref("%sSubnet%s" % (net['name'], idx)),
                        RouteTableId=Ref("RT%s" % net['name']),
                    ))

    def _add_secgroups(self, data, secgroups, config):
        """
        Iterates and creates AWS Security Groups

        :param data: Template object
        :type data: :class:`troposphere.Template`
        :param secgroups: list of security group definitions
        :type secgroups: list.
        :param config: Config key/value pairs
        :type config: dict.
        :returns: dict.
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        """

        sgs = {}
        for secg in secgroups:
            rules = []
            sgname = 'sg%s' % re.sub(r'\W+', '', secg['name'])
            name = secg['name']
            for idx, rule in enumerate(secg['rules']):
                if rule.get('port'):
                    rule['to_port'] = rule['from_port'] = rule['port']
                if rule.get('source_group'):
                    sg_rule_data = {}
                    if rule['source_group'].startswith('='):
                        if secg.get('vpcid', None):
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
                        if secg.get('vpcid', None):
                            sg_rule_data['SourceSecurityGroupId'] =\
                                rule['source_group']
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
            if secg.get('vpcid'):
                if secg['vpcid'].startswith('='):
                    sgargs['VpcId'] = Ref('VPC%s' % secg['vpcid'][1:])
                else:
                    sgargs['VpcId'] = secg['vpcid']
            sgs[name] = ec2.SecurityGroup(
                sgname,
                GroupDescription='security group for %s' % secg['name'],
                SecurityGroupIngress=rules,
                **sgargs
            )
            LOG.debug('Adding sg: %s', sgs[name].JSONrepr())
            data.add_resource(sgs[name])
        return sgs

    def _add_lbs(self, data, loadbalancers, config, sgs, instances):
        """
        Iterates and creates AWS ELBs

        :param data: Template object
        :type data: :class:`troposphere.Template`
        :param loadbalancers: list of load balancer definitions
        :type loadbalancers: list.
        :param config: Config key/value pairs
        :type config: dict.
        :param sgs: list of security group definitions
        :type sgs: list.
        :returns: dict.
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        """

        lbs = {}
        for ldb in loadbalancers:
            lb_hc_tgt = ldb['healthcheck']['protocol'] + ':' + \
                str(ldb['healthcheck']['port'])
            if ldb['healthcheck'].get('path'):
                lb_hc_tgt += ldb['healthcheck']['path']

            listeners = []
            for listener in ldb['listener']:
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

            name = "ELB%s" % re.sub(r'\W+', '', ldb['name'])
            lbtagname = '%s::%s' % (ldb['name'], config['environment'])

            ecdp = elasticloadbalancing.ConnectionDrainingPolicy(
                Enabled=True,
                Timeout=10,
            )
            elb = {
                'CrossZone': True,
                'HealthCheck': elasticloadbalancing.HealthCheck(
                    name,
                    HealthyThreshold=3,
                    Interval=5,
                    Target=lb_hc_tgt,
                    Timeout=2,
                    UnhealthyThreshold=3
                ),
                'Listeners': listeners,
                'ConnectionDrainingPolicy': ecdp,
                'Tags': [{'Key': 'Name', 'Value': lbtagname}],
            }
            for inst in instances:
                if name.lstrip('ELB') in inst.get('lb', []):
                    elb['Tags'].append({
                        'Key': 'App',
                        'Value': inst['name']})

            if ldb.get('sg'):
                elb['SecurityGroups'] = []
                for secg in ldb['sg']:
                    elb['SecurityGroups'].append(Ref(sgs[secg]))
            for policy in ldb['policy']:
                if policy['type'] == 'log_policy':
                    eap = elasticloadbalancing.AccessLoggingPolicy(
                        name,
                        EmitInterval=policy['policy']['emit_interval'],
                        Enabled=policy['policy']['enabled'],
                        S3BucketName=policy['policy']['s3bucket'],
                        S3BucketPrefix=policy['policy']['s3prefix']
                    )
                    elb['AccessLoggingPolicy'] = eap
            if ldb.get('subnets'):
                elb['Subnets'] = ldb['subnets']
                if ldb.get('internal', False):
                    elb['Scheme'] = 'internal'
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
            if ldb.get('dns', None):
                if ldb.get('internal', False) and ldb.get('subnets'):
                    alias_tgt = route53.AliasTarget(
                        GetAtt(name, "CanonicalHostedZoneNameID"),
                        GetAtt(name, "DNSName")
                    )
                else:
                    alias_tgt = route53.AliasTarget(
                        GetAtt(name, "CanonicalHostedZoneNameID"),
                        GetAtt(name, "CanonicalHostedZoneName")
                    )
                data.add_resource(route53.RecordSetType(
                    "DNS%s" % name,
                    AliasTarget=alias_tgt,
                    HostedZoneName="%s.%s" % (
                        config['environment'],
                        ldb['dns']
                    ),
                    Comment="ELB for %s in %s" % (
                        config['name'], config['environment']),
                    Name="%s.%s.%s" % (
                        ldb['name'],
                        config['environment'],
                        ldb['dns']
                    ),
                    Type="A"
                ))

            LOG.debug('Adding lb: %s', lbs[name].JSONrepr())
            data.add_resource(lbs[name])
        return lbs

    def _add_instances(self, data, instances, config, sgs, lbs):
        """
        Iterates and creates AWS ELBs

        :param data: Template object
        :type data: :class:`troposphere.Template`
        :param instances: list of instance definitions
        :type instances: list.
        :param config: Config key/value pairs
        :type config: dict.
        :param sgs: list of security group definitions
        :type sgs: list.
        :param lbs: list of load balancer definitions
        :type lbs: list.
        :returns: dict.
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        """

        for inst in instances:
            udata = None
            cfni = None
            args = inst['provisioner']['args']
            args.update({
                'environment': config['environment'],
                'name': inst['name'],
                'stackname': config['name'],
                'resource': "LC%s" % inst['name'],
            })
            args['appname'] = args.get('appname', config['name'])
            if config.get("version", None):
                args["version"] = config["version"]

            if inst.get('nat'):
                args['eip'] = []
                records = []
                for idx in range(0, inst['count']):
                    eip = ec2.EIP(
                        "EIP%s%s" % (inst['name'], idx),
                        Domain='vpc',
                    )
                    args['eip'].append(eip)
                    records.append(Ref(eip))
                    data.add_resource(eip)

                    data.add_resource(route53.RecordSetType(
                        "EIPDNS%s%02d" % (inst['name'], idx + 1),
                        HostedZoneName="%s.%s" % (
                            config['environment'],
                            inst['dnszone']
                        ),
                        Comment="EIP for %s in %s" % (
                            inst['name'], config['environment']),
                        Name="%s%02d.%s.%s" % (
                            inst['name'], idx + 1,
                            config['environment'],
                            inst['dnszone']
                        ),
                        Type="A",
                        TTL="300",
                        ResourceRecords=[Ref(eip)],
                    ))

                data.add_resource(route53.RecordSetType(
                    "EIPDNS%s" % inst['name'],
                    HostedZoneName="%s.%s" % (
                        config['environment'],
                        inst['dnszone']
                    ),
                    Comment="EIP for %s in %s" % (
                        inst['name'], config['environment']),
                    Name="%s.%s.%s" % (
                        inst['name'],
                        config['environment'],
                        inst['dnszone']
                    ),
                    Type="A",
                    TTL="300",
                    ResourceRecords=records,
                ))

            provider = inst['provisioner']['provider']
            provisioner = import_from_string('pmcf.provisioners',
                                             provider)()
            if provisioner.wants_wait():
                waithandle = cfn.WaitConditionHandle(
                    "Handle%s" % inst['name'],
                )
                args['WaitHandle'] = waithandle
                data.add_resource(waithandle)
                if inst['count'] > 0:
                    cnt = 1
                else:
                    cnt = 0
                data.add_resource(cfn.WaitCondition(
                    "Wait%s" % inst['name'],
                    DependsOn="ASG%s" % inst['name'],
                    Handle=Ref(waithandle),
                    Count=cnt,
                    Timeout=3600
                ))

            if provisioner.wants_profile():
                assume_policy_doc = {
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Principal": {
                            "Service": ["ec2.amazonaws.com"]
                        },
                        "Action": ["sts:AssumeRole"]
                    }]
                }

                iam_role = iam.Role(
                    "Role%s" % inst['name'],
                    AssumeRolePolicyDocument=assume_policy_doc,
                    Path='/%s/%s/' % (inst['name'], config['environment'])
                )
                data.add_resource(iam_role)
                args.update({'role': Ref(iam_role)})
                policy_doc = provisioner.provisioner_policy(args)
                if policy_doc:
                    data.add_resource(iam.PolicyType(
                        "Policy%s" % inst['name'],
                        PolicyName='iam-%s-%s' % (
                            inst['name'], config['environment']),
                        PolicyDocument=policy_doc,
                        Roles=[Ref(iam_role)]
                    ))

                iip = iam.InstanceProfile(
                    "Profile%s" % inst['name'],
                    Path="/%s/%s/" % (
                        inst['name'], config['environment']),
                    Roles=[Ref(iam_role)]
                )
                data.add_resource(iip)
                args.update({'profile': Ref(iip)})

            udata = provisioner.userdata(args)
            cfni = provisioner.cfn_init(args)

            lcargs = {
                'ImageId': inst['image'],
                'InstanceType': inst['size'],
                'KeyName': inst['sshKey'],
                'InstanceMonitoring': inst['monitoring'],
            }

            extra_disk_table = {
                "c1.medium": 1,
                "c1.xlarge": 4,
                "c3.large": 2,
                "c3.xlarge": 2,
                "c3.2xlarge": 2,
                "c3.4xlarge": 2,
                "c3.8xlarge": 2,
                "cc2.8xlarge": 4,
                "cg1.4xlarge": 2,
                "cr1.8xlarge": 2,
                "g2.2xlarge": 1,
                "hi1.4xlarge": 2,
                "hs1.8xlarge": 24,
                "i2.xlarge": 1,
                "i2.2xlarge": 2,
                "i2.4xlarge": 4,
                "i2.8xlarge": 8,
                "m1.small": 1,
                "m1.medium": 1,
                "m1.large": 2,
                "m1.xlarge": 4,
                "m2.xlarge": 1,
                "m2.2xlarge": 1,
                "m2.4xlarge": 2,
                "m3.medium": 1,
                "m3.large": 1,
                "m3.xlarge": 2,
                "m3.2xlarge": 2,
                "r3.large": 1,
                "r3.xlarge": 1,
                "r3.2xlarge": 1,
                "r3.4xlarge": 1,
                "r3.8xlarge": 2,
            }

            block_devs = []
            if inst['size'] in extra_disk_table.keys():
                for disk in range(extra_disk_table[inst['size']]):
                    # Magic Number - ASCII 'b' is 98
                    block_devs.append(autoscaling.BlockDeviceMapping(
                        VirtualName="ephemeral%d" % disk,
                        DeviceName="/dev/xvd%s" % chr(98 + disk)
                    ))

            for block_dev in inst.get('block_device', []):
                block_devs.append(autoscaling.BlockDeviceMapping(
                    DeviceName=block_dev['device'],
                    Ebs=autoscaling.EBSBlockDevice(
                        VolumeSize=block_dev['size'],
                        VolumeType=block_dev['type'],
                    )
                ))

            if block_devs:
                lcargs['BlockDeviceMappings'] = block_devs

            inst_sgs = []
            for secg in inst['sg']:
                if sgs.get(secg):
                    inst_sgs.append(Ref(sgs[secg]))
                else:
                    inst_sgs.append(secg)
            lcargs['SecurityGroups'] = inst_sgs
            if udata is not None:
                lcargs['UserData'] = Base64(udata)
            if cfni is not None:
                lcargs['Metadata'] = cfni

            if inst.get('public'):
                lcargs['AssociatePublicIpAddress'] = True

            if args.get('profile'):
                lcargs['IamInstanceProfile'] = args['profile']
            lcfg = autoscaling.LaunchConfiguration(
                'LC%s' % inst['name'],
                **lcargs
            )
            LOG.debug('Adding lc: %s', lcfg.JSONrepr())
            data.add_resource(lcfg)

            asgtags = [
                autoscaling.Tag(
                    key='Name',
                    value='%s::%s::%s' % (
                        config['name'],
                        inst['name'],
                        config['environment']
                    ),
                    propogate=True,
                ),
                autoscaling.Tag(
                    key='App',
                    value=inst['name'],
                    propogate=True,
                )
            ]
            custom_tags = inst['provisioner']['args'].get('custom_tags', {})
            for k, v in custom_tags.iteritems():
                asgtags.append(
                    autoscaling.Tag(
                        key=k,
                        value=v,
                        propogate=True,
                    )
                )
            if inst.get('dns'):
                dnstag = {
                    'r': inst['dns'].get('record', inst['name']),
                    'z': "%s.%s" % (
                        config['environment'],
                        inst['dns']['zone'],
                    ),
                    't': inst['dns']['type'],
                }
                asgtags.append(
                    autoscaling.Tag(
                        key='DNS',
                        value=json.dumps(dnstag, sort_keys=True),
                        propogate=True,
                    ))

            strategy = import_from_string(
                'pmcf.strategy',
                config.get('strategy', 'BlueGreen')
            )()

            inst['min'] = inst.get('min', inst['count'])
            inst['max'] = inst.get('max', inst['count'])
            asgargs = {
                'AvailabilityZones': inst.get('zones', GetAZs('')),
                'DesiredCapacity': inst['count'],
                'LaunchConfigurationName': Ref(lcfg),
                'MaxSize': inst['max'],
                'MinSize': inst['min'],
                'Tags': asgtags,
                'HealthCheckType': inst.get('healthcheck', 'EC2'),
                'HealthCheckGracePeriod': 600,
            }

            if strategy.termination_policy() != ['Default']:
                asgargs['TerminationPolicies'] = strategy.termination_policy()
            if config.get('vpcid') and inst.get('subnets'):
                asgargs['VPCZoneIdentifier'] = inst['subnets']
            if inst.get('lb'):
                asgargs['LoadBalancerNames'] = [
                    Ref(lbs["ELB" + x]) for x in inst['lb']
                ]
            if inst.get('depends'):
                asgargs['DependsOn'] = inst['depends']
            if inst.get('notify'):
                ncfg = autoscaling.NotificationConfiguration(
                    TopicARN=inst['notify'],
                    NotificationTypes=[
                        "autoscaling:EC2_INSTANCE_LAUNCH",
                        "autoscaling:EC2_INSTANCE_LAUNCH_ERROR",
                        "autoscaling:EC2_INSTANCE_TERMINATE",
                        "autoscaling:EC2_INSTANCE_TERMINATE_ERROR"
                    ]
                )
                asgargs['NotificationConfiguration'] = ncfg
            asg = autoscaling.AutoScalingGroup(
                'ASG%s' % inst['name'],
                **asgargs
            )
            LOG.debug('Adding asg: %s', asg.JSONrepr())
            data.add_resource(asg)

            if inst.get('timed_scaling_policy'):
                pol = inst['timed_scaling_policy']['up']
                scaleuppolargs = {
                    "AutoScalingGroupName": Ref("ASG%s" % inst['name']),
                    "Recurrence": pol['recurrence'],
                }
                if pol.get('count', None) is not None:
                    scaleuppolargs['DesiredCapacity'] = pol['count']

                if pol.get('min', None) is not None:
                    scaleuppolargs['MinSize'] = pol['min']

                if pol.get('max', None) is not None:
                    scaleuppolargs['MaxSize'] = pol['max']

                data.add_resource(autoscaling.ScheduledAction(
                    "ASGTimedScaleUp%s" % inst['name'],
                    **scaleuppolargs
                ))

                pol = inst['timed_scaling_policy'].get('down', None)
                if pol:
                    scaledownpolargs = {
                        "AutoScalingGroupName": Ref("ASG%s" % inst['name']),
                        "Recurrence": pol['recurrence']
                    }
                    if pol.get('count', None) is not None:
                        scaledownpolargs['DesiredCapacity'] = pol['count']

                    if pol.get('min', None) is not None:
                        scaledownpolargs['MinSize'] = pol['min']

                    if pol.get('max', None) is not None:
                        scaledownpolargs['MaxSize'] = pol['max']

                    data.add_resource(autoscaling.ScheduledAction(
                        "ASGTimedScaleDown%s" % inst['name'],
                        **scaledownpolargs
                    ))

            if inst.get('scaling_policy'):
                pol = inst['scaling_policy']
                scaleuppolargs = {
                    "AutoScalingGroupName": Ref("ASG%s" % inst['name']),
                    "Cooldown": pol['up'].get('wait', 300),
                }
                amount = pol['up']['change']
                if pol['up']['change'].find('%') != -1:
                    scaleuppolargs["AdjustmentType"] =\
                        "PercentChangeInCapacity"
                    amount = amount.replace('%', '')
                else:
                    scaleuppolargs["AdjustmentType"] = "ChangeInCapacity"
                scaleuppolargs["ScalingAdjustment"] = amount

                data.add_resource(autoscaling.ScalingPolicy(
                    "ASGScaleUp%s" % inst['name'],
                    **scaleuppolargs
                ))

                scaledownpolargs = {
                    "AutoScalingGroupName": Ref("ASG%s" % inst['name']),
                    "Cooldown": pol['up'].get('wait', 300),
                }
                amount = pol['down']['change']
                if pol['down']['change'].find('%') != -1:
                    scaledownpolargs["AdjustmentType"] =\
                        "PercentChangeInCapacity"
                    amount = amount.replace('%', '')
                else:
                    scaledownpolargs["AdjustmentType"] = "ChangeInCapacity"
                scaledownpolargs["ScalingAdjustment"] = amount

                data.add_resource(autoscaling.ScalingPolicy(
                    "ASGScaleDown%s" % inst['name'],
                    **scaledownpolargs
                ))

                def str_cond(cond):
                    """Helper method used locally"""
                    # expect '>= 40'
                    cond = cond.split()[0]
                    lookup = {
                        '>=': 'GreaterThanOrEqualToThreshold',
                        '>': 'GreaterThanThreshold',
                        '<': 'LessThanThreshold',
                        '<=': 'LessThanOrEqualToThreshold',
                    }
                    return lookup[cond]

                upalarmargs = {
                    "ActionsEnabled": True,
                    "AlarmActions": [Ref("ASGScaleUp%s" % inst['name'])],
                    "ComparisonOperator": str_cond(pol['up']['condition']),
                    "Namespace": ('/').join(pol['metric'].split('/')[:2]),
                    "MetricName": pol['metric'].split('/')[2],
                    "Dimensions": [
                        cloudwatch.MetricDimension(
                            Name="AutoScalingGroupName",
                            Value=Ref("ASG%s" % inst['name']),
                        )
                    ],
                    "EvaluationPeriods": pol.get('wait', 5),
                    "Statistic": pol['up']['stat'],
                    "Threshold": pol['up']['condition'].split()[1],
                    "Unit": pol['unit'],
                }
                if inst['monitoring']:
                    upalarmargs['Period'] = 60
                else:
                    upalarmargs['Period'] = 300

                data.add_resource(cloudwatch.Alarm(
                    "CloudwatchUp%s" % inst['name'],
                    **upalarmargs
                ))

                downalarmargs = {
                    "ActionsEnabled": True,
                    "OKActions": [Ref("ASGScaleDown%s" % inst['name'])],
                    "ComparisonOperator": str_cond(pol['down']['condition']),
                    "Namespace": ('/').join(pol['metric'].split('/')[:2]),
                    "MetricName": pol['metric'].split('/')[2],
                    "Dimensions": [
                        cloudwatch.MetricDimension(
                            Name="AutoScalingGroupName",
                            Value=Ref("ASG%s" % inst['name']),
                        )
                    ],
                    "EvaluationPeriods": pol.get('wait', 5),
                    "Statistic": pol['down']['stat'],
                    "Threshold": pol['down']['condition'].split()[1],
                    "Unit": pol['unit'],
                }
                if inst['monitoring']:
                    downalarmargs['Period'] = 60
                else:
                    downalarmargs['Period'] = 300

                data.add_resource(cloudwatch.Alarm(
                    "CloudwatchDown%s" % inst['name'],
                    **downalarmargs
                ))

    def add_resources(self, resources, config):
        """
        Creates JSON-formatted string representation of stack resourcs
        suitable for use with AWS Cloudformation

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

        self._add_streams(data, resources.get('stream', []), config)
        self._add_queues(data, resources.get('queue', []), config)
        self._add_nets(data, resources.get('network', []), config)
        sgs = self._add_secgroups(data, resources['secgroup'], config)
        self._add_caches(data, resources.get('cache', []), config, sgs)
        lbs = self._add_lbs(data,
                            resources['load_balancer'],
                            config,
                            sgs,
                            resources['instance'])
        self._add_instances(data,
                            resources['instance'],
                            config,
                            sgs,
                            lbs)

        LOG.info('Finished building template')
        return data.to_json(indent=None)

    def run(self, data, metadata=None, poll=False,
            action='create', upload=False):
        """
        Pretty-prints stack definition as json-formatted string

        :param data: Stack definition
        :type data: str.
        :param metadata: Additional information for stack launch (tags, etc).
        :type metadata: dict.
        :param poll: Whether to poll until completion
        :type poll: boolean.
        :param action: Action to take on the stack
        :type action: str.
        :param upload: Whether to upload stack definition to s3 before launch
        :type upload: bool.
        :returns: boolean
        """

        LOG.info('Start running data')
        metadata = metadata or {}
        indent = None
        if LOG.isEnabledFor(logging.DEBUG):
            indent = 4
        signal(SIGPIPE, SIG_DFL)
        print json.dumps(json.loads(data), indent=indent, sort_keys=True)

        LOG.info('Finished running data')
        self.do_audit(data, metadata)
        return True

    def do_audit(self, data, metadata=None):
        """
        Records audit logs for current transaction

        :param data: Stack definition
        :type data: str.
        :param metadata: Additional information for stack launch (tags, etc).
        :type metadata: dict.
        """

        pass


__all__ = [
    'JSONOutput',
]
