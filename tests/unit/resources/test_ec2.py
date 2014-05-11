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

from pmcf.data.template import DataTemplate
from pmcf.exceptions import PropertyExeption
from pmcf.resources import ec2


class TestEc2Resource(object):

    def _data_for_resource(self, data):
        t = DataTemplate()
        t.add_resource(data)
        return json.loads(t.to_json())['Resources']['test']

    def test_tag_valid(self):
        data = {'Key': 'foo', 'Value': 'bar'}
        tag = ec2.Tag(
            key='foo',
            value='bar'
        )
        assert_equals(tag.JSONrepr(), data)

    def test_customer_gateway_invalid(self):
        cust_gw = ec2.CustomerGateway('test')
        assert_raises(PropertyExeption, cust_gw.JSONrepr)

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
        assert_raises(PropertyExeption, dhcp_opts.JSONrepr)

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
        assert_raises(PropertyExeption, eipa.JSONrepr)

    def test_eip_association_invalid_no_instance(self):
        eipa = ec2.EIPAssociation(
            "test",
            EIP="testme-123"
        )
        assert_raises(PropertyExeption, eipa.JSONrepr)

    def test_eip_association_invalid_no_allocation_id(self):
        eipa = ec2.EIPAssociation(
            "test",
            EIP="testme-123",
            NetworkInterfaceId="test-345"
        )
        assert_raises(PropertyExeption, eipa.JSONrepr)

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
        assert_raises(PropertyExeption, ebsbd.JSONrepr)

    def test_ebs_block_device_invalid_io1_invalid_iops(self):
        ebsbd = ec2.EBSBlockDevice(
            "test",
            VolumeType="io1",
            Iops=2100,
        )
        assert_raises(PropertyExeption, ebsbd.JSONrepr)

    def test_ebs_block_device_invalid_standard_invalid_iops(self):
        ebsbd = ec2.EBSBlockDevice(
            "test",
            VolumeType="standard",
            Iops=200,
        )
        assert_raises(PropertyExeption, ebsbd.JSONrepr)

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
        assert_raises(PropertyExeption, ebsbdm.JSONrepr)

    def test_block_device_mapping_invalid_conflicting_type(self):
        ebsbdm = ec2.BlockDeviceMapping(
            "test",
            Ebs=ec2.EBSBlockDevice("test", VolumeSize=50),
            VirtualName="ephemeral1"
        )
        assert_raises(PropertyExeption, ebsbdm.JSONrepr)

    def test_block_device_mapping_invalid_no_devicename_ebs(self):
        ebsbdm = ec2.BlockDeviceMapping(
            "test",
            Ebs=ec2.EBSBlockDevice("test", VolumeSize=50),
        )
        assert_raises(PropertyExeption, ebsbdm.JSONrepr)

    def test_block_device_mapping_invalid_no_devicename_ephemeral(self):
        ebsbdm = ec2.BlockDeviceMapping(
            "test",
            VirtualName="ephemeral1"
        )
        assert_raises(PropertyExeption, ebsbdm.JSONrepr)

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
        assert_raises(PropertyExeption, mp.JSONrepr)

    def test_mount_point_invalid_no_deviceid(self):
        mp = ec2.MountPoint(
            VolumeId="1atestme",
        )
        assert_raises(PropertyExeption, mp.JSONrepr)

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
        assert_raises(PropertyExeption, pips.JSONrepr)

    def test_private_ipaddress_specification_invalid_no_primary(self):
        pips = ec2.PrivateIpAddressSpecification(
            PrivateIpAddress='1.2.3.4',
        )
        assert_raises(PropertyExeption, pips.JSONrepr)

    def test_private_ipaddress_specification_valid(self):
        data = {'Primary': 'true', 'PrivateIpAddress': '1.2.3.4'}
        pips = ec2.PrivateIpAddressSpecification(
            "test",
            PrivateIpAddress='1.2.3.4',
            Primary=True,
        )
        assert_equals(self._data_for_resource(pips), data)

    def test_network_interface_property_invalid_no_index(self):
        nip = ec2.NetworkInterfaceProperty(
            "test"
        )
        assert_raises(PropertyExeption, nip.JSONrepr)

    def test_network_interface_property_invalid_no_subnet_or_int(self):
        nip = ec2.NetworkInterfaceProperty(
            DeviceIndex='1',
        )
        assert_raises(PropertyExeption, nip.JSONrepr)

    def test_network_interface_property_invalid_both_subnet_and_int(self):
        nip = ec2.NetworkInterfaceProperty(
            NetworkInterfaceId='testme-123',
            DeviceIndex='1',
            SubnetId='testme-456'
        )
        assert_raises(PropertyExeption, nip.JSONrepr)

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

    def test_instance_invalid_no_image(self):
        i = ec2.Instance(
            "test",
        )
        assert_raises(PropertyExeption, i.JSONrepr)

    def test_instance_invalid(self):
        pass

    def test_instance_invalid_bad_tenancy(self):
        i = ec2.Instance(
            "test",
            ImageId='testme-123',
            Tenancy='stromble'
        )
        assert_raises(PropertyExeption, i.JSONrepr)

    def test_instance_invalid_interfaces_and_secgroups(self):
        nip = ec2.NetworkInterfaceProperty(
            "test",
            NetworkInterfaceId='testme-123',
            DeviceIndex='1',
        )

        i = ec2.Instance(
            "test",
            ImageId='testme-123',
            NetworkInterfaces=[nip],
            SecurityGroupIds=['testsg-123']
        )
        assert_raises(PropertyExeption, i.JSONrepr)

    def test_instance_invalid_interfaces_and_subnet(self):
        nip = ec2.NetworkInterfaceProperty(
            "test",
            NetworkInterfaceId='testme-123',
            DeviceIndex='1',
        )

        i = ec2.Instance(
            "test",
            ImageId='testme-123',
            NetworkInterfaces=[nip],
            SubnetId='testsn-123'
        )
        assert_raises(PropertyExeption, i.JSONrepr)

    def test_instance_valid_tenancy(self):
        data = {
            'Properties': {
                'ImageId': 'testme-123',
                'Tenancy': 'default'
            },
            'Type': u'AWS::EC2::Instance'
        }
        i = ec2.Instance(
            "test",
            ImageId='testme-123',
            Tenancy='default'
        )
        assert_equals(self._data_for_resource(i), data)

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
        assert_raises(PropertyExeption, na.JSONrepr)

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
        assert_raises(PropertyExeption, icmp.JSONrepr)

    def test_icmp_invalid_no_type(self):
        icmp = ec2.ICMP(
            "test",
            Type=-1
        )
        assert_raises(PropertyExeption, icmp.JSONrepr)

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
        assert_raises(PropertyExeption, pr.JSONrepr)

    def test_port_range_invalid_no_to(self):
        pr = ec2.PortRange(
            "test",
            From=80
        )
        assert_raises(PropertyExeption, pr.JSONrepr)

    def test_port_range_valid(self):
        data = {'From': 80, 'To': 80}
        pr = ec2.PortRange(
            "test",
            From=80,
            To=80,
        )
        assert_equals(self._data_for_resource(pr), data)

    def test_network_acl_entry_invalid_no_cidr(self):
        nae = ec2.NetworkAclEntry(
            "test",
            Egress=False,
            NetworkAclId='testme123',
            PortRange=ec2.PortRange(From=1, To=2),
            Protocol=1,
            RuleAction='allow',
            RuleNumber=1
        )
        assert_raises(PropertyExeption, nae.JSONrepr)

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
        assert_raises(PropertyExeption, nae.JSONrepr)

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
        assert_raises(PropertyExeption, nae.JSONrepr)

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
        assert_raises(PropertyExeption, nae.JSONrepr)

    def test_network_acl_entry_valid_icmp(self):
        data = {
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

        nae = ec2.NetworkAclEntry(
            "test",
            CidrBlock='1.2.3.0/24',
            Egress=False,
            NetworkAclId='testme123',
            Protocol=1,
            Icmp=ec2.ICMP(Code=-1, Type=-1),
            RuleAction='allow',
            RuleNumber=1
        )
        assert_equals(self._data_for_resource(nae), data)

    def test_network_acl_entry_valid_tcp(self):
        data = {
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

        nae = ec2.NetworkAclEntry(
            "test",
            CidrBlock='1.2.3.0/24',
            Egress=False,
            NetworkAclId='testme123',
            Protocol=6,
            PortRange=ec2.PortRange(From=1, To=2),
            RuleAction='allow',
            RuleNumber=1
        )
        assert_equals(self._data_for_resource(nae), data)

    def test_network_acl_entry_valid_udp(self):
        data = {
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

        nae = ec2.NetworkAclEntry(
            "test",
            CidrBlock='1.2.3.0/24',
            Egress=False,
            NetworkAclId='testme123',
            PortRange=ec2.PortRange(From=1, To=2),
            Protocol=17,
            RuleAction='allow',
            RuleNumber=1
        )
        assert_equals(self._data_for_resource(nae), data)

    def test_network_interface_invalid(self):
        ni = ec2.NetworkInterface(
            "test",
            PrivateIpAddress='1.2.3.4'
        )
        assert_raises(PropertyExeption, ni.JSONrepr)

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
        assert_raises(PropertyExeption, nia.JSONrepr)

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

    def test_route_invalid_no_table(self):
        r = ec2.Route(
            "test",
            DestinationCidrBlock='1.2.3.0/24',
        )
        assert_raises(PropertyExeption, r.JSONrepr)

    def test_route_invalid_no_dest(self):
        r = ec2.Route(
            "test",
            DestinationCidrBlock='1.2.3.0/24',
            RouteTableId='testme-123'
        )
        assert_raises(PropertyExeption, r.JSONrepr)

    def test_route_invalid_double_dest(self):
        r = ec2.Route(
            "test",
            DestinationCidrBlock='1.2.3.0/24',
            RouteTableId='testme-123',
            GatewayId='testme-124',
            InstanceId='testme-125'
        )
        assert_raises(PropertyExeption, r.JSONrepr)

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
        assert_raises(PropertyExeption, rt.JSONrepr)

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

    def test_security_group_egress_invalid_no_proto(self):
        sge = ec2.SecurityGroupEgress(
            "test",
            GroupId='testme-123',
            FromPort=80,
            ToPort=80,
        )
        assert_raises(PropertyExeption, sge.JSONrepr)

    def test_security_group_egress_invalid_no_dest(self):
        sge = ec2.SecurityGroupEgress(
            "test",
            GroupId='testme-123',
            IpProtocol='6',
            FromPort=80,
            ToPort=80,
        )
        assert_raises(PropertyExeption, sge.JSONrepr)

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
        assert_raises(PropertyExeption, sge.JSONrepr)

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

    def test_security_group_ingress_invalid_no_proto(self):
        sgi = ec2.SecurityGroupIngress(
            "test",
            CidrIp='10.1.2.0/24',
            GroupId='testme-123',
            GroupName='MySG',
            FromPort=80,
            ToPort=80,
        )
        assert_raises(PropertyExeption, sgi.JSONrepr)

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
        assert_raises(PropertyExeption, sgi.JSONrepr)

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
        assert_raises(PropertyExeption, sgi.JSONrepr)

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
        assert_raises(PropertyExeption, sgi.JSONrepr)

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

    def test_security_group_rule_invalid_no_proto(self):
        sgr = ec2.SecurityGroupRule(
            "test",
            CidrIp='10.1.2.0/24',
            FromPort=80,
            ToPort=80,
        )
        assert_raises(PropertyExeption, sgr.JSONrepr)

    def test_security_group_rule_invalid_cidr_and_sgid(self):
        sgr = ec2.SecurityGroupRule(
            "test",
            CidrIp='10.1.2.0/24',
            FromPort=80,
            ToPort=80,
            IpProtocol='6',
            SourceSecurityGroupId='testme-123',
        )
        assert_raises(PropertyExeption, sgr.JSONrepr)

    def test_security_group_rule_invalid_cidr_and_sgname(self):
        sgr = ec2.SecurityGroupRule(
            "test",
            CidrIp='10.1.2.0/24',
            FromPort=80,
            ToPort=80,
            IpProtocol='6',
            SourceSecurityGroupName='MySG',
        )
        assert_raises(PropertyExeption, sgr.JSONrepr)

    def test_security_group_rule_invalid_sgname_and_sgid(self):
        sgr = ec2.SecurityGroupRule(
            "test",
            FromPort=80,
            ToPort=80,
            IpProtocol='6',
            SourceSecurityGroupName='MySG',
            SourceSecurityGroupId='MySG',
        )
        assert_raises(PropertyExeption, sgr.JSONrepr)

    def test_security_group_rule_valid_sgname(self):
        data = {
            'FromPort': 80,
            'IpProtocol': '6',
            'SourceSecurityGroupName': 'MySG',
            'ToPort': 80
        }
        sgr = ec2.SecurityGroupRule(
            "test",
            FromPort=80,
            ToPort=80,
            IpProtocol='6',
            SourceSecurityGroupName='MySG',
        )
        assert_equals(self._data_for_resource(sgr), data)

    def test_security_group_rule_valid_sgid(self):
        data = {
            'FromPort': 80,
            'IpProtocol': '6',
            'SourceSecurityGroupId': 'testme-123',
            'ToPort': 80
        }
        sgr = ec2.SecurityGroupRule(
            "test",
            FromPort=80,
            ToPort=80,
            IpProtocol='6',
            SourceSecurityGroupId='testme-123',
        )
        assert_equals(self._data_for_resource(sgr), data)

    def test_security_group_rule_valid_cidr(self):
        data = {
            'FromPort': 80,
            'IpProtocol': '6',
            'CidrIp': '10.1.2.0/24',
            'ToPort': 80
        }
        sgr = ec2.SecurityGroupRule(
            "test",
            FromPort=80,
            ToPort=80,
            IpProtocol='6',
            CidrIp='10.1.2.0/24',
        )
        assert_equals(self._data_for_resource(sgr), data)

    def test_security_group_invalid(self):
        sg = ec2.SecurityGroup(
            "test",
        )
        assert_raises(PropertyExeption, sg.JSONrepr)

    def test_security_group_valid(self):
        data = {
            'Properties': {
                'GroupDescription': 'test'
            },
            'Type': 'AWS::EC2::SecurityGroup'
        }
        sg = ec2.SecurityGroup(
            "test",
            GroupDescription='test'
        )
        assert_equals(self._data_for_resource(sg), data)

    def test_subnet_invalid_no_vpcid(self):
        s = ec2.Subnet(
            "test",
            CidrBlock='10.0.0.0/24'
        )
        assert_raises(PropertyExeption, s.JSONrepr)

    def test_subnet_invalid_no_cidr(self):
        s = ec2.Subnet(
            "test",
            VpcId='testme-123'
        )
        assert_raises(PropertyExeption, s.JSONrepr)

    def test_subnet_invalid(self):
        data = {
            'Properties': {
                'CidrBlock': '10.0.0.0/24',
                'VpcId': 'testme-123'
            },
            'Type': u'AWS::EC2::Subnet'
        }
        s = ec2.Subnet(
            "test",
            CidrBlock='10.0.0.0/24',
            VpcId='testme-123'
        )
        assert_equals(self._data_for_resource(s), data)

    def test_subnet_network_acl_association_invalid_no_subnet(self):
        snaa = ec2.SubnetNetworkAclAssociation(
            "test",
            NetworkAclId="testme-123"
        )
        assert_raises(PropertyExeption, snaa.JSONrepr)

    def test_subnet_network_acl_association_invalid_no_network(self):
        snaa = ec2.SubnetNetworkAclAssociation(
            "test",
            SubnetId="testme-456",
        )
        assert_raises(PropertyExeption, snaa.JSONrepr)

    def test_subnet_network_acl_association_valid(self):
        data = {
            'Properties': {
                'NetworkAclId': 'testme-123',
                'SubnetId': 'testme-456'
            },
            'Type': 'AWS::EC2::SubnetNetworkAclAssociation'
        }
        snaa = ec2.SubnetNetworkAclAssociation(
            "test",
            SubnetId="testme-456",
            NetworkAclId="testme-123"
        )
        assert_equals(self._data_for_resource(snaa), data)

    def test_subnet_route_table_association_invalid_no_table(self):
        srta = ec2.SubnetRouteTableAssociation(
            "test",
            SubnetId='testme-123'
        )
        assert_raises(PropertyExeption, srta.JSONrepr)

    def test_subnet_route_table_association_invalid_no_subnet(self):
        srta = ec2.SubnetRouteTableAssociation(
            "test",
            RouteTableId='testme-123'
        )
        assert_raises(PropertyExeption, srta.JSONrepr)

    def test_subnet_route_table_association_valid(self):
        data = {
            'Properties': {
                'RouteTableId': 'testrt-123',
                'SubnetId': 'testsi-123'
            },
            'Type': 'AWS::EC2::SubnetRouteTableAssociation'
        }
        srta = ec2.SubnetRouteTableAssociation(
            "test",
            SubnetId='testsi-123',
            RouteTableId='testrt-123'
        )
        assert_equals(self._data_for_resource(srta), data)

    def test_volume_invalid_no_az(self):
        v = ec2.Volume(
            "test",
            Size='10'
        )
        assert_raises(PropertyExeption, v.JSONrepr)

    def test_volume_invalid_iops_and_standard(self):
        v = ec2.Volume(
            "test",
            AvailabilityZone='eu-west1c',
            Size='10',
            VolumeType='standard',
            Iops=2000,
        )
        assert_raises(PropertyExeption, v.JSONrepr)

    def test_volume_invalid_too_many_iops(self):
        v = ec2.Volume(
            "test",
            AvailabilityZone='eu-west1c',
            Size='10',
            VolumeType='io1',
            Iops=5000,
        )
        assert_raises(PropertyExeption, v.JSONrepr)

    def test_volume_invalid_not_enough_iops(self):
        v = ec2.Volume(
            "test",
            AvailabilityZone='eu-west1c',
            Size='10',
            VolumeType='io1',
            Iops=50,
        )
        assert_raises(PropertyExeption, v.JSONrepr)

    def test_volume_invalid_size_and_snapshot(self):
        v = ec2.Volume(
            "test",
            AvailabilityZone='eu-west1c',
            Size='10',
            SnapshotId='testsn-123',
        )
        assert_raises(PropertyExeption, v.JSONrepr)

    def test_volume_invalid_iops_for_size(self):
        v = ec2.Volume(
            "test",
            AvailabilityZone='eu-west1c',
            Size='10',
            Iops=1000,
            VolumeType='io1'
        )
        assert_raises(PropertyExeption, v.JSONrepr)

    def test_volume_valid_iops(self):
        data = {
            'Properties': {
                'AvailabilityZone': 'eu-west1c',
                'Iops': 1000,
                'Size': '100',
                'VolumeType': 'io1'
            },
            'Type': 'AWS::EC2::Volume'
        }
        v = ec2.Volume(
            "test",
            AvailabilityZone='eu-west1c',
            Size='100',
            Iops=1000,
            VolumeType='io1'
        )
        assert_equals(self._data_for_resource(v), data)

    def test_volume_valid_snapshot(self):
        data = {
            'Properties': {
                'AvailabilityZone': 'eu-west1c',
                'SnapshotId': 'testsn-123',
                'VolumeType': 'standard'
            },
            'Type': 'AWS::EC2::Volume'
        }
        v = ec2.Volume(
            "test",
            AvailabilityZone='eu-west1c',
            SnapshotId='testsn-123'
        )
        assert_equals(self._data_for_resource(v), data)

    def test_volume_valid_standard(self):
        data = {
            'Properties': {
                'AvailabilityZone': 'eu-west1c',
                'Size': '100',
                'VolumeType': 'standard'
            },
            'Type': 'AWS::EC2::Volume'
        }
        v = ec2.Volume(
            "test",
            AvailabilityZone='eu-west1c',
            Size='100'
        )
        assert_equals(self._data_for_resource(v), data)

    def test_volume_attachment_invalid_no_device(self):
        va = ec2.VolumeAttachment(
            "test",
            InstanceId='testme-123',
            VolumeId='testv-123'
        )
        assert_raises(PropertyExeption, va.JSONrepr)

    def test_volume_attachment_invalid_no_instance(self):
        va = ec2.VolumeAttachment(
            "test",
            Device='/dev/sdd',
            VolumeId='testv-123'
        )
        assert_raises(PropertyExeption, va.JSONrepr)

    def test_volume_attachment_invalid_no_volume(self):
        va = ec2.VolumeAttachment(
            "test",
            Device='/dev/sdd',
            InstanceId='testme-123',
        )
        assert_raises(PropertyExeption, va.JSONrepr)

    def test_volume_attachment_valid(self):
        data = {
            'Properties': {
                'Device': '/dev/sdd',
                'InstanceId': 'testme-123',
                'VolumeId': 'testv-123'
            },
            'Type': 'AWS::EC2::VolumeAttachment'
        }
        va = ec2.VolumeAttachment(
            "test",
            Device='/dev/sdd',
            InstanceId='testme-123',
            VolumeId='testv-123'
        )
        assert_equals(self._data_for_resource(va), data)

    def test_vpc_invalid_no_cidr(self):
        vpc = ec2.VPC(
            "test",
        )
        assert_raises(PropertyExeption, vpc.JSONrepr)

    def test_vpc_invalid_hostname_no_dns(self):
        vpc = ec2.VPC(
            "test",
            CidrBlock='10.0.0.0/16',
            EnableDnsHostnames=True,
        )
        assert_raises(PropertyExeption, vpc.JSONrepr)

    def test_vpc_invalid_instance_tenancy(self):
        vpc = ec2.VPC(
            "test",
            CidrBlock='10.0.0.0/16',
            InstanceTenancy='wibble',
        )
        assert_raises(PropertyExeption, vpc.JSONrepr)

    def test_vpc_valid_tenancy_default(self):
        data = {
            'Properties': {
                'CidrBlock': '10.0.0.0/16',
                'InstanceTenancy': 'default'
            },
            'Type': 'AWS::EC2::VPC'
        }
        vpc = ec2.VPC(
            "test",
            CidrBlock='10.0.0.0/16',
            InstanceTenancy='default',
        )
        assert_equals(self._data_for_resource(vpc), data)

    def test_vpc_valid_tenancy_dedicated(self):
        data = {
            'Properties': {
                'CidrBlock': '10.0.0.0/16',
                'InstanceTenancy': 'dedicated'
            },
            'Type': 'AWS::EC2::VPC'
        }
        vpc = ec2.VPC(
            "test",
            CidrBlock='10.0.0.0/16',
            InstanceTenancy='dedicated',
        )
        assert_equals(self._data_for_resource(vpc), data)

    def test_vpc_valid_tenancy_dnshostnames(self):
        data = {
            'Properties': {
                'CidrBlock': '10.0.0.0/16',
                'EnableDnsHostnames': 'true',
                'EnableDnsSupport': 'true'
            },
            'Type': 'AWS::EC2::VPC'
        }
        vpc = ec2.VPC(
            "test",
            CidrBlock='10.0.0.0/16',
            EnableDnsSupport=True,
            EnableDnsHostnames=True,
        )
        assert_equals(self._data_for_resource(vpc), data)

    def test_vpc_dhcp_options_association_invalid_no_option(self):
        vdoa = ec2.VPCDHCPOptionsAssociation(
            "test",
            VpcId='testvpc-123'
        )
        assert_raises(PropertyExeption, vdoa.JSONrepr)

    def test_vpc_dhcp_options_association_invalid_no_vpc(self):
        vdoa = ec2.VPCDHCPOptionsAssociation(
            "test",
            DhcpOptionsId='testdo-123',
        )
        assert_raises(PropertyExeption, vdoa.JSONrepr)

    def test_vpc_dhcp_options_association_valid(self):
        data = {
            'Properties': {
                'DhcpOptionsId': 'testdo-123',
                'VpcId': 'testvpc-123'
            },
            'Type': 'AWS::EC2::VPCDHCPOptionsAssociation'
        }
        vdoa = ec2.VPCDHCPOptionsAssociation(
            "test",
            DhcpOptionsId='testdo-123',
            VpcId='testvpc-123'
        )
        assert_equals(self._data_for_resource(vdoa), data)

    def test_vpc_gateway_attachment_invalid_no_gateway(self):
        vga = ec2.VPCGatewayAttachment(
            "test",
            VpcId='testvpc-123',
        )
        assert_raises(PropertyExeption, vga.JSONrepr)

    def test_vpc_gateway_attachment_invalid_no_vpc(self):
        vga = ec2.VPCGatewayAttachment(
            "test",
            InternetGatewayId='testig-123',
        )
        assert_raises(PropertyExeption, vga.JSONrepr)

    def test_vpc_gateway_attachment_invalid_two_gateway(self):
        vga = ec2.VPCGatewayAttachment(
            "test",
            InternetGatewayId='testig-123',
            VpcId='testvpc-123',
            VpnGatewayId='testvpn-123',
        )
        assert_raises(PropertyExeption, vga.JSONrepr)

    def test_vpc_gateway_attachment_valid_gw(self):
        data = {
            'Properties': {
                'VpcId': 'testvpc-123',
                'InternetGatewayId': 'testig-123',
            },
            'Type': 'AWS::EC2::VPCGatewayAttachment'
        }
        vga = ec2.VPCGatewayAttachment(
            "test",
            InternetGatewayId='testig-123',
            VpcId='testvpc-123',
        )
        assert_equals(self._data_for_resource(vga), data)

    def test_vpc_gateway_attachment_valid_vpn(self):
        data = {
            'Properties': {
                'VpcId': 'testvpc-123',
                'VpnGatewayId': 'testvpn-123'
            },
            'Type': 'AWS::EC2::VPCGatewayAttachment'
        }
        vga = ec2.VPCGatewayAttachment(
            "test",
            VpcId='testvpc-123',
            VpnGatewayId='testvpn-123',
        )
        assert_equals(self._data_for_resource(vga), data)

    def test_vpnconnection_invalid_no_cust_gw(self):
        vpnc = ec2.VPNConnection(
            "test",
            Type='ipsec.1',
            VpnGatewayId='testvpngi-123'
        )
        assert_raises(PropertyExeption, vpnc.JSONrepr)

    def test_vpnconnection_invalid_no_type(self):
        vpnc = ec2.VPNConnection(
            "test",
            CustomerGatewayId='testcgi-123',
            VpnGatewayId='testvpngi-123'
        )
        assert_raises(PropertyExeption, vpnc.JSONrepr)

    def test_vpnconnection_invalid_no_gw(self):
        vpnc = ec2.VPNConnection(
            "test",
            Type='ipsec.1',
            CustomerGatewayId='testcgi-123',
        )
        assert_raises(PropertyExeption, vpnc.JSONrepr)

    def test_vpnconnection_valid(self):
        data = {
            'Properties': {
                'CustomerGatewayId': 'testcgi-123',
                'Type': 'ipsec.1',
                'VpnGatewayId': 'testvpngi-123'
            },
            'Type': 'AWS::EC2::VPNConnection'
        }
        vpnc = ec2.VPNConnection(
            "test",
            Type='ipsec.1',
            CustomerGatewayId='testcgi-123',
            VpnGatewayId='testvpngi-123'
        )
        assert_equals(self._data_for_resource(vpnc), data)

    def test_vpnconnectionroute_invalid_no_dest(self):
        vpncr = ec2.VPNConnectionRoute(
            "test",
            VpnConnectionId='testvpnc-123'
        )
        assert_raises(PropertyExeption, vpncr.JSONrepr)

    def test_vpnconnectionroute_invalid_no_vpncid(self):
        vpncr = ec2.VPNConnectionRoute(
            "test",
            DestinationCidrBlock='10.2.3.0/24',
        )
        assert_raises(PropertyExeption, vpncr.JSONrepr)

    def test_vpnconnectionroute_valid(self):
        data = {
            'Properties': {
                'DestinationCidrBlock': '10.2.3.0/24',
                'VpnConnectionId': 'testvpnc-123'
            },
            'Type': 'AWS::EC2::VPNConnectionRoute'
        }
        vpncr = ec2.VPNConnectionRoute(
            "test",
            DestinationCidrBlock='10.2.3.0/24',
            VpnConnectionId='testvpnc-123'
        )
        assert_equals(self._data_for_resource(vpncr), data)

    def test_vpn_gateway_invalid_no_type(self):
        vpng = ec2.VPNGateway(
            "test",
        )
        assert_raises(PropertyExeption, vpng.JSONrepr)

    def test_vpn_gateway_invalid_bad_type(self):
        vpng = ec2.VPNGateway(
            "test",
            Type='openvpn'
        )
        assert_raises(PropertyExeption, vpng.JSONrepr)

    def test_vpn_gateway_valid(self):
        data = {
            'Properties': {
                'Type': 'ipsec.1'
            },
            'Type': 'AWS::EC2::VPNGateway'
        }
        vpng = ec2.VPNGateway(
            "test",
            Type='ipsec.1'
        )
        assert_equals(self._data_for_resource(vpng), data)

    def test_vpn_gateway_route_propagation_invalid_no_route(self):
        vpngrp = ec2.VPNGatewayRoutePropagation(
            "test",
            VpnGatewayId='testvpng-123'
        )
        assert_raises(PropertyExeption, vpngrp.JSONrepr)

    def test_vpn_gateway_route_propagation_invalid_no_vpc(self):
        vpngrp = ec2.VPNGatewayRoutePropagation(
            "test",
            RouteTableIds=['testrt-123'],
        )
        assert_raises(PropertyExeption, vpngrp.JSONrepr)

    def test_vpn_gateway_route_propagation_valid(self):
        data = {
            'Properties': {
                'RouteTableIds': ['testrt-123'],
                'VpnGatewayId': u'testvpng-123'
            },
            'Type': 'AWS::EC2::VPNGatewayRoutePropagation'
        }
        vpngrp = ec2.VPNGatewayRoutePropagation(
            "test",
            RouteTableIds=['testrt-123'],
            VpnGatewayId='testvpng-123'
        )
        assert_equals(self._data_for_resource(vpngrp), data)
