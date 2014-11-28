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

# This is the model layer, with a light validation layer over what troposphere
# provides

from troposphere import ec2
from pmcf.resources.aws.helpers import ec2 as rec2

from pmcf.utils import error, init_error


class Tag(ec2.Tag):
    pass


class CustomerGateway(ec2.CustomerGateway):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class DHCPOptions(ec2.DHCPOptions):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def validate(self):
        super(self.__class__, self).validate()

        if len(set(self.propnames).intersection(self.properties.keys())) > 0:
            return True
        error(self, 'Need at least one property')


class EIP(ec2.EIP):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)


class EIPAssociation(ec2.EIPAssociation):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def validate(self):
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
    def __init__(self, title=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def validate(self):
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
    def __init__(self, title=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()

        if len(set(self.properties.keys()).intersection(
                set(['Ebs', 'VirtualName']))) != 1:
            error(self, 'One of Ebs or VirtualName required')

        return True


class MountPoint(ec2.MountPoint):
    def __init__(self, title=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class PrivateIpAddressSpecification(ec2.PrivateIpAddressSpecification):
    def __init__(self, title=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class NetworkInterfaceProperty(ec2.NetworkInterfaceProperty):
    def __init__(self, title=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()

        if len(set(self.properties.keys()).intersection(
                set(['NetworkInterfaceId', 'SubnetId']))) != 1:
            error(self, 'One of NetworkInterfaceId or SubnetId required')

        return True


class Instance(ec2.Instance):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()

        if self.properties.get('NetworkInterfaces'):
            if self.properties.get('SecurityGroupIds'):
                error(self, 'Can not specify both NetworkInterfaces and '
                            'SecurityGroupIds')
            if self.properties.get('SubnetId'):
                error(self, 'Can not specify both NetworkInterfaces and '
                            'SubnetId')

        it = self.properties.get('Tenancy')
        if it:
            if it not in ['default', 'dedicated']:
                error(self, 'Tenancy must be one of "default", "dedicated"')


class InternetGateway(ec2.InternetGateway):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)


class NetworkAcl(ec2.NetworkAcl):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class ICMP(ec2.ICMP):
    def __init__(self, title=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def validate(self):
        super(self.__class__, self).validate()

        if len(set(self.properties.keys()).intersection(
                set(['Code', 'Type']))) != 2:
            error(self, 'Code and Type are required')

        return True


class PortRange(ec2.PortRange):
    def __init__(self, title=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def validate(self):
        super(self.__class__, self).validate()

        if len(set(self.properties.keys()).intersection(
                set(['From', 'To']))) != 2:
            error(self, 'From and To are required')

        return True


class NetworkAclEntry(ec2.NetworkAclEntry):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()

        if self.properties['Protocol'] == 1:
            if not self.properties.get('Icmp'):
                error(self, 'Icmp must be specified when protocol is 1')
        elif self.properties['Protocol'] in [6, 17]:  # TCP, UDP
            if not self.properties.get('PortRange'):
                error(self, 'PortRange must be specified when protocol '
                            'protocol is 6 or 17')


class NetworkInterface(ec2.NetworkInterface):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class NetworkInterfaceAttachment(ec2.NetworkInterfaceAttachment):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class Route(rec2.Route):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()
        if len(set(self.properties.keys()).intersection(
                set(['GatewayId', 'InstanceId',
                     'NetworkInterfaceId', 'VpcPeeringConnectionId']))) != 1:
            error(self, 'One of GatewayId, InstanceId, or NetworkInterfaceId '
                        'are required')

        return True


class RouteTable(ec2.RouteTable):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class SecurityGroupEgress(ec2.SecurityGroupEgress):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()

        if len(set(self.properties.keys()).intersection(
                set(['CidrIp', 'DestinationSecurityGroupId']))) != 1:
            error(self, 'CidrIp or DestinationSecurityGroupId are required')

        return True


class SecurityGroupIngress(ec2.SecurityGroupIngress):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
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
    def __init__(self, title=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
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
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class Subnet(ec2.Subnet):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class SubnetNetworkAclAssociation(ec2.SubnetNetworkAclAssociation):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class SubnetRouteTableAssociation(ec2.SubnetRouteTableAssociation):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class Volume(ec2.Volume):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
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
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class VPC(ec2.VPC):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()

        if self.properties.get('EnableDnsHostnames'):
            if not self.properties.get('EnableDnsSupport'):
                error(self, 'EnableDnsSupport must be true if '
                            'EnableDnsHostnames is true')

        it = self.properties.get('InstanceTenancy')
        if it:
            if it not in ['default', 'dedicated']:
                error(self, 'InstanceTenancy must be one of "default", '
                            '"dedicated"')


class VPCDHCPOptionsAssociation(ec2.VPCDHCPOptionsAssociation):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class VPCGatewayAttachment(ec2.VPCGatewayAttachment):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()

        if len(set(self.properties.keys()).intersection(
                set(['InternetGatewayId', 'VpnGatewayId']))) != 1:
            error(self, 'InternetGatewayId or VpnGatewayId are required')


class VPCPeeringConnection(rec2.VPCPeeringConnection):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class VPNConnection(ec2.VPNConnection):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class VPNConnectionRoute(ec2.VPNConnectionRoute):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)


class VPNGateway(ec2.VPNGateway):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()
        if self.properties.get('Type') != 'ipsec.1':
            error(self, 'Type must be ipsec.1')


class VPNGatewayRoutePropagation(rec2.VPNGatewayRoutePropagation):
    def __init__(self, title, template=None, **kwargs):
        try:
            super(self.__class__, self).__init__(title, template, **kwargs)
        except ValueError, e:
            init_error(e.message, self.__class__.__name__, title)

    def JSONrepr(self):
        try:
            return super(self.__class__, self).JSONrepr()
        except ValueError, e:
            error(self, e.message)

    def validate(self):
        super(self.__class__, self).validate()
        if not self.properties.get('RouteTableIds'):
            error(self, 'Resource RouteTableIds required')


__all__ = [
    BlockDeviceMapping,
    CustomerGateway,
    DHCPOptions,
    EBSBlockDevice,
    EIP,
    EIPAssociation,
    ICMP,
    Instance,
    InternetGateway,
    MountPoint,
    NetworkAcl,
    NetworkAclEntry,
    NetworkInterface,
    NetworkInterfaceAttachment,
    NetworkInterfaceProperty,
    PortRange,
    PrivateIpAddressSpecification,
    Route,
    RouteTable,
    SecurityGroup,
    SecurityGroupEgress,
    SecurityGroupIngress,
    SecurityGroupRule,
    Subnet,
    SubnetNetworkAclAssociation,
    SubnetRouteTableAssociation,
    Tag,
    Volume,
    VolumeAttachment,
    VPC,
    VPCDHCPOptionsAssociation,
    VPCGatewayAttachment,
    VPCPeeringConnection,
    VPNConnection,
    VPNConnectionRoute,
    VPNGateway,
    VPNGatewayRoutePropagation,
]
