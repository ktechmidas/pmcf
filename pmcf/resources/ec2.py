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
        if len(set(self.propnames).intersection(self.properties.keys())) > 0:
            return True
        raise ValueError('Need at least one property')


class EIP(ec2.EIP):
    pass


class EIPAssociation(ec2.EIPAssociation):
    def validate(self):
        net_props = ['InstanceId', 'PrivateIpAddress']
        nic_rsrc = []
        for prop in ['AllocationId', 'EIP']:
            if self.properties.get(prop):
                nic_rsrc.append(prop)
        if len(nic_rsrc) != 1:
            raise ValueError("Need to specify an EIP")

        if self.properties.get('AllocationId'):
            net_props.append('NetworkInterfaceId')

        if len(set(self.properties.keys()).intersection(set(net_props))) != 1:
            raise ValueError('Need to specify associated resource')

        return True


class EBSBlockDevice(ec2.EBSBlockDevice):
    def validate(self):
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
        if len(set(self.properties.keys()).intersection(
                set(['Ebs', 'VirtualName']))) != 1:
            raise ValueError('One of Ebs or VirtualName required')

        return True


class MountPoint(ec2.MountPoint):
    pass


class PrivateIpAddressSpecification(ec2.PrivateIpAddressSpecification):
    pass


class NetworkInterfaceProperty(ec2.NetworkInterfaceProperty):
    pass


class Instance(ec2.Instance):
    pass


class InternetGateway(ec2.InternetGateway):
    pass


class NetworkAcl(ec2.NetworkAcl):
    pass


class ICMP(ec2.ICMP):
    pass


class PortRange(ec2.PortRange):
    pass


class NetworkAclEntry(ec2.NetworkAclEntry):
    pass


class NetworkInterface(ec2.NetworkInterface):
    pass


class NetworkInterfaceAttachment(ec2.NetworkInterfaceAttachment):
    pass


class Route(ec2.Route):
    pass


class RouteTable(ec2.RouteTable):
    pass


class SecurityGroupEgress(ec2.SecurityGroupEgress):
    pass


class SecurityGroupIngress(ec2.SecurityGroupIngress):
    pass


class SecurityGroupRule(ec2.SecurityGroupRule):
    pass


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
