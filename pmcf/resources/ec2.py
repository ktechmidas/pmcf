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


class Tag(ec2.Tag):
    pass


class CustomerGateway(ec2.CustomerGateway):
    pass


class DHCPOptions(ec2.DHCPOptions):
    def validate(self):
        super(self.__class__, self).validate()
        if len(set(self.propnames).intersection(self.properties.keys())) > 0:
            return True
        raise ValueError('Need at least one property')


class EIP(ec2.EIP):
    pass


class EIPAssociation(ec2.EIPAssociation):
    def validate(self):
        super(self.__class__, self).validate()
        net_props = ['InstanceId', 'PrivateIpAddress']
        if len(set(self.properties.keys()).intersection(
                set(['AllocationId', 'EIP']))) != 1:
            raise ValueError("Need to specify an EIP")

        if self.properties.get('AllocationId'):
            net_props.append('NetworkInterfaceId')

        if len(set(self.properties.keys()).intersection(set(net_props))) != 1:
            raise ValueError('Need to specify associated resource')

        return True


class EBSBlockDevice(ec2.EBSBlockDevice):
    def validate(self):
        super(self.__class__, self).validate()
        if self.properties.get('VolumeType') == 'io1':
            iops = int(self.properties.get('Iops', 0))
            if iops < 100 or iops > 2000:
                raise ValueError('iops property not in range 100-2000')
        else:
            self.properties['VolumeType'] = 'standard'
            if self.properties.get('Iops'):
                raise ValueError('iops property not allowed on volumes '
                                 'of type standard')

        return True


class BlockDeviceMapping(ec2.BlockDeviceMapping):
    def validate(self):
        super(self.__class__, self).validate()
        if len(set(self.properties.keys()).intersection(
                set(['Ebs', 'VirtualName']))) != 1:
            raise ValueError('One of Ebs or VirtualName required')

        return True


class MountPoint(ec2.MountPoint):
    pass


class PrivateIpAddressSpecification(ec2.PrivateIpAddressSpecification):
    pass


class NetworkInterfaceProperty(ec2.NetworkInterfaceProperty):
    def validate(self):
        super(self.__class__, self).validate()
        if len(set(self.properties.keys()).intersection(
                set(['NetworkInterfaceId', 'SubnetId']))) != 1:
            raise ValueError('One of NetworkInterfaceId or SubnetId required')

        return True


class Instance(ec2.Instance):
    pass


class InternetGateway(ec2.InternetGateway):
    pass


class NetworkAcl(ec2.NetworkAcl):
    pass


class ICMP(ec2.ICMP):
    def validate(self):
        super(self.__class__, self).validate()
        if len(set(self.properties.keys()).intersection(
                set(['Code', 'Type']))) != 2:
            raise ValueError('Code and Type are required')

        return True


class PortRange(ec2.PortRange):
    def validate(self):
        super(self.__class__, self).validate()
        if len(set(self.properties.keys()).intersection(
                set(['From', 'To']))) != 2:
            raise ValueError('From and To are required')

        return True


class NetworkAclEntry(ec2.NetworkAclEntry):
    def validate(self):
        super(self.__class__, self).validate()
        if self.properties['Protocol'] == 1:
            if not self.properties.get('Icmp'):
                raise ValueError('Icmp must be specified when protocol is 1')
        elif self.properties['Protocol'] in [6, 17]:  # TCP, UDP
            if not self.properties.get('PortRange'):
                raise ValueError('PortRange must be specified when protocol '
                                 'protocol is 6 or 17')


class NetworkInterface(ec2.NetworkInterface):
    pass


class NetworkInterfaceAttachment(ec2.NetworkInterfaceAttachment):
    pass


class Route(ec2.Route):
    def validate(self):
        super(self.__class__, self).validate()
        if len(set(self.properties.keys()).intersection(
                set(['GatewayId', 'InstanceId', 'NetworkInterfaceId']))) != 1:
            raise ValueError('One of GatewayId, InstanceId, or '
                             'NetworkInterfaceId are required')

        return True


class RouteTable(ec2.RouteTable):
    pass


class SecurityGroupEgress(ec2.SecurityGroupEgress):
    def validate(self):
        super(self.__class__, self).validate()
        if len(set(self.properties.keys()).intersection(
                set(['CidrIp', 'DestinationSecurityGroupId']))) != 1:
            raise ValueError('CidrIp or DestinationSecurityGroupId are '
                             'required')

        return True


class SecurityGroupIngress(ec2.SecurityGroupIngress):
    def validate(self):
        super(self.__class__, self).validate()
        if len(set(self.properties.keys()).intersection(
                set(['GroupName', 'GroupId']))) != 1:
            raise ValueError('GroupName or GroupId are required')

        if self.properties.get('CidrIp'):
            if len(set(self.properties.keys()).intersection(
                set(['SourceSecurityGroupName', 'SourceSecurityGroupId',
                     'SourceSecurityGroupOwnerId']))) != 0:
                raise ValueError('Cannot specify SourceSecurityGroup options '
                                 'and CidrIp')

        elif len(set(self.properties.keys()).intersection(
                set(['SourceSecurityGroupName',
                     'SourceSecurityGroupId']))) != 1:
                raise ValueError('Either SourceSecurityGroupName or '
                                 'SourceSecurityGroupId is necessary when '
                                 'CidrIp is unset')

        return True


class SecurityGroupRule(ec2.SecurityGroupRule):
    def validate(self):
        super(self.__class__, self).validate()
        if self.properties.get('CidrIp'):
            if len(set(self.properties.keys()).intersection(
                set(['SourceSecurityGroupName', 'SourceSecurityGroupId',
                     'SourceSecurityGroupOwnerId']))) != 0:
                raise ValueError('Cannot specify SourceSecurityGroup options '
                                 'and CidrIp')

        elif len(set(self.properties.keys()).intersection(
                set(['SourceSecurityGroupName',
                     'SourceSecurityGroupId']))) != 1:
                raise ValueError('Either SourceSecurityGroupName or '
                                 'SourceSecurityGroupId is necessary when '
                                 'CidrIp is unset')

        return True


class SecurityGroup(ec2.SecurityGroup):
    pass


class Subnet(ec2.Subnet):
    pass


class SubnetNetworkAclAssociation(ec2.SubnetNetworkAclAssociation):
    pass


class SubnetRouteTableAssociation(ec2.SubnetRouteTableAssociation):
    pass


class Volume(ec2.Volume):
    pass


class VolumeAttachment(ec2.VolumeAttachment):
    pass


class VPC(ec2.VPC):
    pass


class VPCDHCPOptionsAssociation(ec2.VPCDHCPOptionsAssociation):
    pass


class VPCGatewayAttachment(ec2.VPCGatewayAttachment):
    pass


class VPNConnection(ec2.VPNConnection):
    pass


class VPNConnectionRoute(ec2.VPNConnectionRoute):
    pass


class VPNGateway(ec2.VPNGateway):
    pass


class VPNGatewayRoutePropagation(ec2.VPNGatewayRoutePropagation):
    pass


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
    VPNConnection,
    VPNConnectionRoute,
    VPNGateway,
    VPNGatewayRoutePropagation
]
