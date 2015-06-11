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
..  module:: pmcf.resources.aws.ec2
    :platform: Unix
    :synopsis: wrapper classes for troposphere ec2 classes

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

from troposphere import ec2

from pmcf.utils import do_init, do_json, error

# pylint: disable=super-init-not-called


class Tag(ec2.Tag):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    pass


class CustomerGateway(ec2.CustomerGateway):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class DHCPOptions(ec2.DHCPOptions):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()

        if len(set(self.propnames).intersection(self.properties.keys())) > 0:
            return True
        error(self, 'Need at least one property')


class EIP(ec2.EIP):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)


class EIPAssociation(ec2.EIPAssociation):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()

        net_props = ['InstanceId', 'PrivateIpAddress']
        if len(set(self.properties.keys()).intersection(
                set(['AllocationId', 'EIP']))) != 1:
            error(self, 'Need to specify an EIP')

        if self.properties.get('AllocationId'):
            net_props.append('NetworkInterfaceId')

        if len(set(self.properties.keys()).intersection(set(net_props))) != 1:
            error(self, 'Need to specify associated resource')

        return True


class EBSBlockDevice(ec2.EBSBlockDevice):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, **kwargs):
        do_init(self, title, prop=True, **kwargs)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()

        if self.properties.get('VolumeType'):
            if self.properties['VolumeType'] == 'io1':
                iops = int(self.properties.get('Iops', 0))
                if iops < 100 or iops > 2000:
                    error(self, 'iops property not in range 100-2000')
            elif self.properties['VolumeType'] in ['standard', 'gp2']:
                if self.properties.get('Iops'):
                    error(self, 'iops property not allowed on volumes '
                                'of type standard or gp2')
            else:
                error(self, 'Unknown VolumeType')
        else:
            self.properties['VolumeType'] = 'gp2'

        return True


class BlockDeviceMapping(ec2.BlockDeviceMapping):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, **kwargs):
        do_init(self, title, prop=True, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()

        if len(set(self.properties.keys()).intersection(
                set(['Ebs', 'VirtualName']))) != 1:
            error(self, 'One of Ebs or VirtualName required')

        return True


class MountPoint(ec2.MountPoint):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, **kwargs):
        do_init(self, title, prop=True, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class PrivateIpAddressSpecification(ec2.PrivateIpAddressSpecification):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, **kwargs):
        do_init(self, title, prop=True, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class NetworkInterfaceProperty(ec2.NetworkInterfaceProperty):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, **kwargs):
        do_init(self, title, prop=True, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()

        if len(set(self.properties.keys()).intersection(
                set(['NetworkInterfaceId', 'SubnetId']))) != 1:
            error(self, 'One of NetworkInterfaceId or SubnetId required')

        return True


class Instance(ec2.Instance):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()

        if self.properties.get('NetworkInterfaces'):
            if self.properties.get('SecurityGroupIds'):
                error(self, 'Can not specify both NetworkInterfaces and '
                            'SecurityGroupIds')
            if self.properties.get('SubnetId'):
                error(self, 'Can not specify both NetworkInterfaces and '
                            'SubnetId')

        inst_ten = self.properties.get('Tenancy')
        if inst_ten:
            if inst_ten not in ['default', 'dedicated']:
                error(self, 'Tenancy must be one of "default", "dedicated"')


class InternetGateway(ec2.InternetGateway):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)


class NetworkAcl(ec2.NetworkAcl):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class ICMP(ec2.ICMP):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, **kwargs):
        do_init(self, title, prop=True, **kwargs)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()

        if len(set(self.properties.keys()).intersection(
                set(['Code', 'Type']))) != 2:
            error(self, 'Code and Type are required')

        return True


class PortRange(ec2.PortRange):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, **kwargs):
        do_init(self, title, prop=True, **kwargs)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()

        if len(set(self.properties.keys()).intersection(
                set(['From', 'To']))) != 2:
            error(self, 'From and To are required')

        return True


class NetworkAclEntry(ec2.NetworkAclEntry):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()

        if self.properties['Protocol'] == 1:
            if not self.properties.get('Icmp'):
                error(self, 'Icmp must be specified when protocol is 1')
        elif self.properties['Protocol'] in [6, 17]:  # TCP, UDP
            if not self.properties.get('PortRange'):
                error(self, 'PortRange must be specified when protocol '
                            'protocol is 6 or 17')


# pylint: disable=interface-not-implemented


class NetworkInterface(ec2.NetworkInterface):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


# pylint: enable=interface-not-implemented


class NetworkInterfaceAttachment(ec2.NetworkInterfaceAttachment):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class Route(ec2.Route):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()
        if len(set(self.properties.keys()).intersection(
                set(['GatewayId', 'InstanceId',
                     'NetworkInterfaceId', 'VpcPeeringConnectionId']))) != 1:
            error(self, 'One of GatewayId, InstanceId, or NetworkInterfaceId '
                        'are required')

        return True


class RouteTable(ec2.RouteTable):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class SecurityGroupEgress(ec2.SecurityGroupEgress):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()

        if len(set(self.properties.keys()).intersection(
                set(['CidrIp', 'DestinationSecurityGroupId']))) != 1:
            error(self, 'CidrIp or DestinationSecurityGroupId are required')

        return True


class SecurityGroupIngress(ec2.SecurityGroupIngress):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()

        if len(set(self.properties.keys()).intersection(
                set(['GroupName', 'GroupId']))) != 1:
            error(self, 'GroupName or GroupId are required')

        if self.properties.get('CidrIp'):
            if len(set(self.properties.keys()).intersection(
                set(['SourceSecurityGroupName', 'SourceSecurityGroupId',
                     'SourceSecurityGroupOwnerId']))) != 0:
                error(self, 'Cannot specify SourceSecurityGroup options '
                            'and CidrIp')

        elif len(set(self.properties.keys()).intersection(
                set(['SourceSecurityGroupName',
                     'SourceSecurityGroupId']))) != 1:
                error(self, 'Either SourceSecurityGroupName or '
                            'SourceSecurityGroupId is necessary when CidrIp '
                            'is unset')

        return True


class SecurityGroupRule(ec2.SecurityGroupRule):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title=None, **kwargs):
        do_init(self, title, prop=True, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()

        if self.properties.get('CidrIp'):
            if len(set(self.properties.keys()).intersection(
                set(['SourceSecurityGroupName', 'SourceSecurityGroupId',
                     'SourceSecurityGroupOwnerId']))) != 0:
                error(self, 'Cannot specify SourceSecurityGroup options '
                            'and CidrIp')

        elif len(set(self.properties.keys()).intersection(
                set(['SourceSecurityGroupName',
                     'SourceSecurityGroupId']))) != 1:
                error(self, 'Either SourceSecurityGroupName or '
                            'SourceSecurityGroupId is necessary when CidrIp '
                            'is unset')

        return True


class SecurityGroup(ec2.SecurityGroup):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class Subnet(ec2.Subnet):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class SubnetNetworkAclAssociation(ec2.SubnetNetworkAclAssociation):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class SubnetRouteTableAssociation(ec2.SubnetRouteTableAssociation):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class Volume(ec2.Volume):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()

        iops = int(self.properties.get('Iops', 0))
        size = self.properties.get('Size')

        if self.properties.get('VolumeType') == 'io1':
            if iops < 100 or iops > 4000:
                error(self, 'iops property not in range 100-4000')
        elif self.properties.get('VolumeType') == 'gp2':
            if self.properties.get('Iops'):
                error(self, 'iops property not allowed on volumes '
                            'of type gp2')
        else:
            self.properties['VolumeType'] = 'standard'
            if self.properties.get('Iops'):
                error(self, 'iops property not allowed on volumes '
                            'of type standard')
        if size:
            if self.properties.get('SnapshotId'):
                error(self, 'Cannot set Size and SnapshotId')
            if iops > 0:
                if iops > (int(size) * 10):
                    error(self, 'Size must be at least 10 times iops')

        return True


class VolumeAttachment(ec2.VolumeAttachment):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class VPC(ec2.VPC):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()

        if self.properties.get('EnableDnsHostnames'):
            if not self.properties.get('EnableDnsSupport'):
                error(self, 'EnableDnsSupport must be true if '
                            'EnableDnsHostnames is true')

        inst_ten = self.properties.get('InstanceTenancy')
        if inst_ten:
            if inst_ten not in ['default', 'dedicated']:
                error(self, 'InstanceTenancy must be one of "default", '
                            '"dedicated"')


class VPCDHCPOptionsAssociation(ec2.VPCDHCPOptionsAssociation):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class VPCGatewayAttachment(ec2.VPCGatewayAttachment):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()

        if len(set(self.properties.keys()).intersection(
                set(['InternetGatewayId', 'VpnGatewayId']))) != 1:
            error(self, 'InternetGatewayId or VpnGatewayId are required')


class VPCPeeringConnection(ec2.VPCPeeringConnection):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class VPNConnection(ec2.VPNConnection):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class VPNConnectionRoute(ec2.VPNConnectionRoute):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)


class VPNGateway(ec2.VPNGateway):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()
        if self.properties.get('Type') != 'ipsec.1':
            error(self, 'Type must be ipsec.1')


class VPNGatewayRoutePropagation(ec2.VPNGatewayRoutePropagation):
    """
    Subclass of troposphere class to provide wrappers for raising correct
    exception types and do other validation.
    """

    def __init__(self, title, template=None, **kwargs):
        do_init(self, title, template=template, **kwargs)

    def JSONrepr(self):
        """
        Return JSON representation of troposphere resource object
        """

        return do_json(self)

    def validate(self):
        """
        Validate properties of troposphere resource with additional checks
        """

        super(self.__class__, self).validate()
        if not self.properties.get('RouteTableIds'):
            error(self, 'Resource RouteTableIds required')


__all__ = [
    'BlockDeviceMapping',
    'CustomerGateway',
    'DHCPOptions',
    'EBSBlockDevice',
    'EIP',
    'EIPAssociation',
    'ICMP',
    'Instance',
    'InternetGateway',
    'MountPoint',
    'NetworkAcl',
    'NetworkAclEntry',
    'NetworkInterface',
    'NetworkInterfaceAttachment',
    'NetworkInterfaceProperty',
    'PortRange',
    'PrivateIpAddressSpecification',
    'Route',
    'RouteTable',
    'SecurityGroup',
    'SecurityGroupEgress',
    'SecurityGroupIngress',
    'SecurityGroupRule',
    'Subnet',
    'SubnetNetworkAclAssociation',
    'SubnetRouteTableAssociation',
    'Tag',
    'Volume',
    'VolumeAttachment',
    'VPC',
    'VPCDHCPOptionsAssociation',
    'VPCGatewayAttachment',
    'VPCPeeringConnection',
    'VPNConnection',
    'VPNConnectionRoute',
    'VPNGateway',
    'VPNGatewayRoutePropagation',
]
