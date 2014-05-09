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

import json
from nose.tools import assert_equals, assert_raises

from pmcf.resources import ec2
from pmcf.data.template import DataTemplate


class TestEc2Resource(object):

    def _data_for_resource(self, data):
        t = DataTemplate()
        t.add_resource(data)
        return json.loads(t.to_json())['Resources']['test']

    def test_tag(self):
        data = {'Key': 'foo', 'Value': 'bar'}
        tag = ec2.Tag(
            key='foo',
            value='bar'
        )
        assert_equals(tag.JSONrepr(), data)

    def test_customer_gateway_invalid(self):
        cust_gw = ec2.CustomerGateway('test')
        assert_raises(ValueError, cust_gw.JSONrepr)

    def test_customer_gateway_valid(self):
        data = {
            'Properties': {
                'BgpAsn': '65000',
                'IpAddress': '1.2.3.4',
                'Type': 'ipsec.1'
            },
            'Type': 'AWS::EC2::CustomerGateway'
        }

        cust_gw = ec2.CustomerGateway(
            "test",
            BgpAsn="65000",
            IpAddress="1.2.3.4",
            Type="ipsec.1",
        )
        assert_equals(self._data_for_resource(cust_gw), data)

    def test_dhcp_options_invalid(self):
        dhcp_opts = ec2.DHCPOptions("test")
        assert_raises(ValueError, dhcp_opts.JSONrepr)

    def test_dhcp_options_valid(self):
        data = {
            'Properties': {
                'DomainName': 'example.com'
            },
            'Type': 'AWS::EC2::DHCPOptions'
        }

        dhcp_opts = ec2.DHCPOptions(
            "test",
            DomainName="example.com"
        )
        assert_equals(self._data_for_resource(dhcp_opts), data)

    def test_eip(self):
        data = {
            'Properties': {
                'Domain': 'vpc'
            },
            'Type': 'AWS::EC2::EIP'
        }

        eip = ec2.EIP(
            "test",
            Domain="vpc",
        )
        assert_equals(self._data_for_resource(eip), data)

    def test_eip_association_invalid_no_device(self):
        eipa = ec2.EIPAssociation(
            "test",
            InstanceId="testme-234"
        )
        assert_raises(ValueError, eipa.JSONrepr)

    def test_eip_association_invalid_no_instance(self):
        eipa = ec2.EIPAssociation(
            "test",
            EIP="testme-123"
        )
        assert_raises(ValueError, eipa.JSONrepr)

    def test_eip_association_invalid_no_allocation_id(self):
        eipa = ec2.EIPAssociation(
            "test",
            EIP="testme-123",
            NetworkInterfaceId="test-345"
        )
        assert_raises(ValueError, eipa.JSONrepr)

    def test_eip_association_valid_allocation_id(self):
        data = {
            'Properties': {
                'AllocationId': 'testme-123',
                'NetworkInterfaceId': 'testme-234'
            },
            'Type': 'AWS::EC2::EIPAssociation'
        }

        eipa = ec2.EIPAssociation(
            "test",
            AllocationId="testme-123",
            NetworkInterfaceId="testme-234"
        )
        assert_equals(self._data_for_resource(eipa), data)

    def test_eip_association_valid_eip(self):
        data = {
            'Properties': {
                'EIP': 'testme-123',
                'InstanceId': 'testme-234'
            },
            'Type': 'AWS::EC2::EIPAssociation'
        }

        eipa = ec2.EIPAssociation(
            "test",
            EIP="testme-123",
            InstanceId="testme-234"
        )
        assert_equals(self._data_for_resource(eipa), data)

    def test_ebs_block_device_invalid_io1_no_iops(self):
        ebsbd = ec2.EBSBlockDevice(
            "test",
            VolumeType="io1"
        )
        assert_raises(ValueError, ebsbd.JSONrepr)

    def test_ebs_block_device_invalid_io1_invalid_iops(self):
        ebsbd = ec2.EBSBlockDevice(
            "test",
            VolumeType="io1",
            Iops=2100,
        )
        assert_raises(ValueError, ebsbd.JSONrepr)

    def test_ebs_block_device_invalid_standard_invalid_iops(self):
        ebsbd = ec2.EBSBlockDevice(
            "test",
            VolumeType="standard",
            Iops=200,
        )
        assert_raises(ValueError, ebsbd.JSONrepr)

    def test_ebs_block_device_valid_high_io(self):
        data = {'Iops': 1100, 'VolumeType': 'io1'}
        ebsbd = ec2.EBSBlockDevice(
            "test",
            VolumeType="io1",
            Iops=1100,
        )
        assert_equals(self._data_for_resource(ebsbd), data)

    def test_ebs_block_device_valid_standard(self):
        data = {'VolumeType': 'standard'}
        ebsbd = ec2.EBSBlockDevice(
            "test",
        )
        assert_equals(self._data_for_resource(ebsbd), data)

    def test_block_device_mapping_invalid_no_type(self):
        ebsbdm = ec2.BlockDeviceMapping(
            "test",
            DeviceName="/dev/sda",
        )
        assert_raises(ValueError, ebsbdm.JSONrepr)

    def test_block_device_mapping_invalid_conflicting_type(self):
        ebsbdm = ec2.BlockDeviceMapping(
            "test",
            Ebs=ec2.EBSBlockDevice("test", VolumeSize=50),
            VirtualName="ephemeral1"
        )
        assert_raises(ValueError, ebsbdm.JSONrepr)

    def test_block_device_mapping_invalid_no_devicename_ebs(self):
        ebsbdm = ec2.BlockDeviceMapping(
            "test",
            Ebs=ec2.EBSBlockDevice("test", VolumeSize=50),
        )
        assert_raises(ValueError, ebsbdm.JSONrepr)

    def test_block_device_mapping_invalid_no_devicename_ephemeral(self):
        ebsbdm = ec2.BlockDeviceMapping(
            "test",
            VirtualName="ephemeral1"
        )
        assert_raises(ValueError, ebsbdm.JSONrepr)

    def test_block_device_mapping_valid(self):
        data = {'DeviceName': '/dev/sda', 'VirtualName': 'ephemeral1'}
        ebsbdm = ec2.BlockDeviceMapping(
            "test",
            DeviceName="/dev/sda",
            VirtualName="ephemeral1"
        )
        assert_equals(self._data_for_resource(ebsbdm), data)

    def test_mount_point_invalid_no_volumeid(self):
        mp = ec2.MountPoint(
            Device="/dev/sda"
        )
        assert_raises(ValueError, mp.JSONrepr)

    def test_mount_point_invalid_no_deviceid(self):
        mp = ec2.MountPoint(
            VolumeId="1atestme",
        )
        assert_raises(ValueError, mp.JSONrepr)

    def test_mount_point_valid(self):
        data = {'Device': '/dev/sda', 'VolumeId': '1atestme'}
        mp = ec2.MountPoint(
            "test",
            VolumeId="1atestme",
            Device="/dev/sda"
        )
        assert_equals(self._data_for_resource(mp), data)

    def test_private_ipaddress_specification_invalid_no_ip(self):
        pips = ec2.PrivateIpAddressSpecification(
            "test",
            Primary=False,
        )
        assert_raises(ValueError, pips.JSONrepr)

    def test_private_ipaddress_specification_invalid_no_primary(self):
        pips = ec2.PrivateIpAddressSpecification(
            PrivateIpAddress='1.2.3.4',
        )
        assert_raises(ValueError, pips.JSONrepr)

    def test_private_ipaddress_specification_valid(self):
        data = {'Primary': 'true', 'PrivateIpAddress': '1.2.3.4'}
        pips = ec2.PrivateIpAddressSpecification(
            "test",
            PrivateIpAddress='1.2.3.4',
            Primary=True,
        )
        assert_equals(self._data_for_resource(pips), data)

    def test_network_interface_property_invalid_no_subnet_or_int(self):
        nip = ec2.NetworkInterfaceProperty(
            DeviceIndex='1',
        )
        assert_raises(ValueError, nip.JSONrepr)

    def test_network_interface_property_invalid_both_subnet_and_int(self):
        nip = ec2.NetworkInterfaceProperty(
            NetworkInterfaceId='testme-123',
            DeviceIndex='1',
            SubnetId='testme-456'
        )
        assert_raises(ValueError, nip.JSONrepr)

    def test_network_interface_property_valid(self):
        data = {
            'AssociatePublicIpAddress': 'true',
            'DeleteOnTermination': 'true',
            'Description': 'testme',
            'DeviceIndex': '1',
            'NetworkInterfaceId': 'testme-123'
        }
        nip = ec2.NetworkInterfaceProperty(
            "test",
            NetworkInterfaceId='testme-123',
            AssociatePublicIpAddress=True,
            DeviceIndex='1',
            DeleteOnTermination=True,
            Description='testme',
        )
        assert_equals(self._data_for_resource(nip), data)

#    def test_Instance_invalid(self):
#        pass
#
#    def test_Instance_valid(self):
#        pass
#
    def test_internet_gateway_invalid(self):
        # You can't screw this one up
        pass

    def test_internet_gateway_valid(self):
        data = {'Type': 'AWS::EC2::InternetGateway'}
        ig = ec2.InternetGateway(
            "test"
        )
        assert_equals(self._data_for_resource(ig), data)

    def test_network_acl_invalid_no_vpcid(self):
        na = ec2.NetworkAcl("test")
        assert_raises(ValueError, na.JSONrepr)

    def test_network_acl_valid(self):
        data = {
            'Type': 'AWS::EC2::NetworkAcl',
            'Properties': {
                'VpcId': 'testme-123'
            }
        }
        na = ec2.NetworkAcl(
            "test",
            VpcId='testme-123'
        )
        assert_equals(self._data_for_resource(na), data)

    def test_icmp_invalid_no_code(self):
        icmp = ec2.ICMP(
            "test",
            Code=-1
        )
        assert_raises(ValueError, icmp.JSONrepr)

    def test_icmp_invalid_no_type(self):
        icmp = ec2.ICMP(
            "test",
            Type=-1
        )
        assert_raises(ValueError, icmp.JSONrepr)

    def test_icmp_valid(self):
        data = {'Code': -1, 'Type': -1}
        icmp = ec2.ICMP(
            "test",
            Code=-1,
            Type=-1
        )
        assert_equals(self._data_for_resource(icmp), data)

    def test_port_range_invalid_no_from(self):
        pr = ec2.PortRange(
            "test",
            To=80
        )
        assert_raises(ValueError, pr.JSONrepr)

    def test_port_range_invalid_no_to(self):
        pr = ec2.PortRange(
            "test",
            From=80
        )
        assert_raises(ValueError, pr.JSONrepr)

    def test_port_range_valid(self):
        data = {'From': 80, 'To': 80}
        pr = ec2.PortRange(
            "test",
            From=80,
            To=80,
        )
        assert_equals(self._data_for_resource(pr), data)

    def test_network_acl_entry_invalid_icmp(self):
        nae = ec2.NetworkAclEntry(
            "test",
            CidrBlock='1.2.3.0/24',
            Egress=False,
            NetworkAclId='testme123',
            PortRange=ec2.PortRange(From=1, To=2),
            Protocol=1,
            RuleAction='allow',
            RuleNumber=1
        )
        assert_raises(ValueError, nae.JSONrepr)

    def test_network_acl_entry_invalid_tcp(self):
        nae = ec2.NetworkAclEntry(
            "test",
            CidrBlock='1.2.3.0/24',
            Egress=False,
            NetworkAclId='testme123',
            Icmp=ec2.ICMP(Code=-1, Type=-1),
            Protocol=6,
            RuleAction='allow',
            RuleNumber=1
        )
        assert_raises(ValueError, nae.JSONrepr)

    def test_network_acl_entry_invalid_udp(self):
        nae = ec2.NetworkAclEntry(
            "test",
            CidrBlock='1.2.3.0/24',
            Egress=False,
            NetworkAclId='testme123',
            Icmp=ec2.ICMP(Code=-1, Type=-1),
            Protocol=17,
            RuleAction='allow',
            RuleNumber=1
        )
        assert_raises(ValueError, nae.JSONrepr)

    def test_network_acl_entry_valid_icmp(self):
        t = DataTemplate()
        data = {
            "Resources": {
                "test": {
                    "Properties": {
                        "CidrBlock": "1.2.3.0/24",
                        "Egress": "false",
                        "Icmp": {
                            "Code": -1,
                            "Type": -1
                        },
                        "NetworkAclId": "testme123",
                        "Protocol": 1,
                        "RuleAction": "allow",
                        "RuleNumber": 1
                    },
                    "Type": "AWS::EC2::NetworkAclEntry"
                }
            }
        }

        t.add_resource(ec2.NetworkAclEntry(
            "test",
            CidrBlock='1.2.3.0/24',
            Egress=False,
            NetworkAclId='testme123',
            Protocol=1,
            Icmp=ec2.ICMP(Code=-1, Type=-1),
            RuleAction='allow',
            RuleNumber=1
        ))
        assert_equals(json.loads(t.to_json()), data)

    def test_network_acl_entry_valid_tcp(self):
        t = DataTemplate()
        data = {
            "Resources": {
                "test": {
                    "Properties": {
                        "CidrBlock": "1.2.3.0/24",
                        "Egress": "false",
                        "PortRange": {
                            "From": 1,
                            "To": 2
                        },
                        "NetworkAclId": "testme123",
                        "Protocol": 6,
                        "RuleAction": "allow",
                        "RuleNumber": 1
                    },
                    "Type": "AWS::EC2::NetworkAclEntry"
                }
            }
        }

        t.add_resource(ec2.NetworkAclEntry(
            "test",
            CidrBlock='1.2.3.0/24',
            Egress=False,
            NetworkAclId='testme123',
            Protocol=6,
            PortRange=ec2.PortRange(From=1, To=2),
            RuleAction='allow',
            RuleNumber=1
        ))
        assert_equals(json.loads(t.to_json()), data)

    def test_network_acl_entry_valid_udp(self):
        t = DataTemplate()
        data = {
            "Resources": {
                "test": {
                    "Properties": {
                        "CidrBlock": "1.2.3.0/24",
                        "Egress": "false",
                        "PortRange": {
                            "From": 1,
                            "To": 2
                        },
                        "NetworkAclId": "testme123",
                        "Protocol": 17,
                        "RuleAction": "allow",
                        "RuleNumber": 1
                    },
                    "Type": "AWS::EC2::NetworkAclEntry"
                }
            }
        }

        t.add_resource(ec2.NetworkAclEntry(
            "test",
            CidrBlock='1.2.3.0/24',
            Egress=False,
            NetworkAclId='testme123',
            PortRange=ec2.PortRange(From=1, To=2),
            Protocol=17,
            RuleAction='allow',
            RuleNumber=1
        ))
        assert_equals(json.loads(t.to_json()), data)

    def test_network_interface_invalid(self):
        ni = ec2.NetworkInterface(
            "test",
            PrivateIpAddress='1.2.3.4'
        )
        assert_raises(ValueError, ni.JSONrepr)

    def test_network_interface_valid(self):
        data = {
            'Properties': {
                'PrivateIpAddress': '1.2.3.4',
                'SubnetId': 'testme-123'
            },
            'Type': 'AWS::EC2::NetworkInterface'
        }
        ni = ec2.NetworkInterface(
            "test",
            PrivateIpAddress='1.2.3.4',
            SubnetId='testme-123'
        )
        assert_equals(self._data_for_resource(ni), data)

    def test_network_interface_attachment_invalid(self):
        nia = ec2.NetworkInterfaceAttachment(
            "test",
            InstanceId='testme-123',
            DeviceIndex='0'
        )
        assert_raises(ValueError, nia.JSONrepr)

    def test_network_interface_attachment_valid(self):
        data = {
            'Properties': {
                'DeviceIndex': '0',
                'InstanceId': 'testme-123',
                'NetworkInterfaceId': 'testme-456'
            },
            'Type': 'AWS::EC2::NetworkInterfaceAttachment'
        }
        nia = ec2.NetworkInterfaceAttachment(
            "test",
            InstanceId='testme-123',
            NetworkInterfaceId='testme-456',
            DeviceIndex='0'
        )
        assert_equals(self._data_for_resource(nia), data)

    def test_route_invalid_no_dest(self):
        r = ec2.Route(
            "test",
            DestinationCidrBlock='1.2.3.0/24',
            RouteTableId='testme-123'
        )
        assert_raises(ValueError, r.JSONrepr)

    def test_route_invalid_double_dest(self):
        r = ec2.Route(
            "test",
            DestinationCidrBlock='1.2.3.0/24',
            RouteTableId='testme-123',
            GatewayId='testme-124',
            InstanceId='testme-125'
        )
        assert_raises(ValueError, r.JSONrepr)

    def test_route_valid_gateway(self):
        data = {
            'Properties': {
                'DestinationCidrBlock': '1.2.3.0/24',
                'GatewayId': 'testme-124',
                'RouteTableId': 'testme-123'
            },
            'Type': 'AWS::EC2::Route'
        }
        r = ec2.Route(
            "test",
            DestinationCidrBlock='1.2.3.0/24',
            RouteTableId='testme-123',
            GatewayId='testme-124',
        )
        assert_equals(self._data_for_resource(r), data)

    def test_route_valid_instance(self):
        data = {
            'Properties': {
                'DestinationCidrBlock': '1.2.3.0/24',
                'InstanceId': 'testme-125',
                'RouteTableId': 'testme-123'
            },
            'Type': 'AWS::EC2::Route'
        }
        r = ec2.Route(
            "test",
            DestinationCidrBlock='1.2.3.0/24',
            RouteTableId='testme-123',
            InstanceId='testme-125',
        )
        assert_equals(self._data_for_resource(r), data)

    def test_route_valid_nic(self):
        data = {
            'Properties': {
                'DestinationCidrBlock': '1.2.3.0/24',
                'NetworkInterfaceId': 'testme-126',
                'RouteTableId': 'testme-123'
            },
            'Type': 'AWS::EC2::Route'
        }
        r = ec2.Route(
            "test",
            DestinationCidrBlock='1.2.3.0/24',
            RouteTableId='testme-123',
            NetworkInterfaceId='testme-126',
        )
        assert_equals(self._data_for_resource(r), data)

    def test_route_table_invalid(self):
        rt = ec2.RouteTable(
            "test"
        )
        assert_raises(ValueError, rt.JSONrepr)

    def test_route_table_valid(self):
        data = {
            'Properties': {
                'VpcId': 'testme-123'
            },
            'Type': 'AWS::EC2::RouteTable'
        }
        rt = ec2.RouteTable(
            "test",
            VpcId='testme-123'
        )
        assert_equals(self._data_for_resource(rt), data)

    def test_security_group_egress_invalid_no_dest(self):
        sge = ec2.SecurityGroupEgress(
            "test",
            GroupId='testme-123',
            IpProtocol='6',
            FromPort=80,
            ToPort=80,
        )
        assert_raises(ValueError, sge.JSONrepr)

    def test_security_group_egress_invalid_two_dests(self):
        sge = ec2.SecurityGroupEgress(
            "test",
            CidrIp='10.1.2.0/24',
            DestinationSecurityGroupId='testsg-123',
            GroupId='testme-123',
            IpProtocol='6',
            FromPort=80,
            ToPort=80,
        )
        assert_raises(ValueError, sge.JSONrepr)

    def test_security_group_egress_valid_cidr(self):
        data = {
            'Properties': {
                'CidrIp': '10.1.2.0/24',
                'FromPort': 80,
                'GroupId': 'testme-123',
                'IpProtocol': '6',
                'ToPort': 80
            },
            'Type': 'AWS::EC2::SecurityGroupEgress'
        }
        sge = ec2.SecurityGroupEgress(
            "test",
            CidrIp='10.1.2.0/24',
            GroupId='testme-123',
            IpProtocol='6',
            FromPort=80,
            ToPort=80,
        )
        assert_equals(self._data_for_resource(sge), data)

    def test_security_group_egress_valid_sg(self):
        data = {
            'Properties': {
                'DestinationSecurityGroupId': 'testsg-123',
                'FromPort': 80,
                'GroupId': 'testme-123',
                'IpProtocol': '6',
                'ToPort': 80
            },
            'Type': 'AWS::EC2::SecurityGroupEgress'
        }
        sge = ec2.SecurityGroupEgress(
            "test",
            DestinationSecurityGroupId='testsg-123',
            GroupId='testme-123',
            IpProtocol='6',
            FromPort=80,
            ToPort=80,
        )
        assert_equals(self._data_for_resource(sge), data)

    def test_security_group_ingress_invalid_two_groups(self):
        sgi = ec2.SecurityGroupIngress(
            "test",
            CidrIp='10.1.2.0/24',
            GroupId='testme-123',
            GroupName='MySG',
            IpProtocol='6',
            FromPort=80,
            ToPort=80,
        )
        assert_raises(ValueError, sgi.JSONrepr)

    def test_security_group_ingress_invalid_two_source_groups(self):
        sgi = ec2.SecurityGroupIngress(
            "test",
            GroupName='MySG',
            SourceSecurityGroupName='YourSG',
            SourceSecurityGroupId='testme-123',
            IpProtocol='6',
            FromPort=80,
            ToPort=80,
        )
        assert_raises(ValueError, sgi.JSONrepr)

    def test_security_group_ingress_invalid_two_sources(self):
        sgi = ec2.SecurityGroupIngress(
            "test",
            CidrIp='10.1.2.0/24',
            GroupName='MySG',
            SourceSecurityGroupId='testme-123',
            IpProtocol='6',
            FromPort=80,
            ToPort=80,
        )
        assert_raises(ValueError, sgi.JSONrepr)

    def test_security_group_ingress_valid_gname_source_group(self):
        data = {
            'Properties': {
                'FromPort': 80,
                'GroupName': 'MySG',
                'IpProtocol': '6',
                'SourceSecurityGroupId': 'testme-123',
                'ToPort': 80
            },
            'Type': 'AWS::EC2::SecurityGroupIngress'
        }

        sgi = ec2.SecurityGroupIngress(
            "test",
            GroupName='MySG',
            SourceSecurityGroupId='testme-123',
            IpProtocol='6',
            FromPort=80,
            ToPort=80,
        )
        assert_equals(self._data_for_resource(sgi), data)

    def test_security_group_ingress_valid_gid_source_group(self):
        data = {
            'Properties': {
                'FromPort': 80,
                'GroupId': 'testsg-123',
                'IpProtocol': '6',
                'SourceSecurityGroupId': 'testme-123',
                'ToPort': 80
            },
            'Type': 'AWS::EC2::SecurityGroupIngress'
        }

        sgi = ec2.SecurityGroupIngress(
            "test",
            GroupId='testsg-123',
            SourceSecurityGroupId='testme-123',
            IpProtocol='6',
            FromPort=80,
            ToPort=80,
        )
        assert_equals(self._data_for_resource(sgi), data)

    def test_security_group_ingress_valid_gname_source_cidr(self):
        data = {
            'Properties': {
                'FromPort': 80,
                'GroupName': 'MySG',
                'IpProtocol': '6',
                'CidrIp': '1.2.3.0/24',
                'ToPort': 80
            },
            'Type': 'AWS::EC2::SecurityGroupIngress'
        }

        sgi = ec2.SecurityGroupIngress(
            "test",
            GroupName='MySG',
            CidrIp='1.2.3.0/24',
            IpProtocol='6',
            FromPort=80,
            ToPort=80,
        )
        assert_equals(self._data_for_resource(sgi), data)

#    def test_SecurityGroupRule_invalid(self):
#        pass
#
#    def test_SecurityGroupRule_valid(self):
#        pass
#
#    def test_SecurityGroup_invalid(self):
#        pass
#
#    def test_SecurityGroup_valid(self):
#        pass
#
#    def test_Subnet_invalid(self):
#        pass
#
#    def test_Subnet_valid(self):
#        pass
#
#    def test_SubnetNetworkAclAssociation_invalid(self):
#        pass
#
#    def test_SubnetNetworkAclAssociation_valid(self):
#        pass
#
#    def test_SubnetRouteTableAssociation_invalid(self):
#        pass
#
#    def test_SubnetRouteTableAssociation_valid(self):
#        pass
#
#    def test_Volume_invalid(self):
#        pass
#
#    def test_Volume_valid(self):
#        pass
#
#    def test_VolumeAttachment_invalid(self):
#        pass
#
#    def test_VolumeAttachment_valid(self):
#        pass
#
#    def test_VPC_invalid(self):
#        pass
#
#    def test_VPC_valid(self):
#        pass
#
#    def test_VPCDHCPOptionsAssociation_invalid(self):
#        pass
#
#    def test_VPCDHCPOptionsAssociation_valid(self):
#        pass
#
#    def test_VPCGatewayAttachment_invalid(self):
#        pass
#
#    def test_VPCGatewayAttachment_valid(self):
#        pass
#
#    def test_VPNConnection_invalid(self):
#        pass
#
#    def test_VPNConnection_valid(self):
#        pass
#
#    def test_VPNConnectionRoute_invalid(self):
#        pass
#
#    def test_VPNConnectionRoute_valid(self):
#        pass
#
#    def test_VPNGateway_invalid(self):
#        pass
#
#    def test_VPNGateway_valid(self):
#        pass
#
#    def test_VPNGatewayRoutePropagation_invalid(self):
#        pass
#
#    def test_VPNGatewayRoutePropagation_valid(self):
#        pass
