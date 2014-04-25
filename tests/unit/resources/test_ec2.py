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

from nose.tools import assert_equals, assert_raises

from pmcf.resources import ec2


class TestEc2Resource(object):

    def test_tag(self):
        data = {'Key': 'foo', 'Value': 'bar'}
        tag = ec2.Tag(key='foo', value='bar')
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
        assert_equals(cust_gw.JSONrepr(), data)

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
        assert_equals(dhcp_opts.JSONrepr(), data)

    def test_dhcp_options_validate(self):
        dhcp_opts = ec2.DHCPOptions(
            "test",
            DomainName="example.com"
        )
        dhcp_opts.validate()

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
        assert_equals(eip.JSONrepr(), data)

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
        assert_equals(eipa.JSONrepr(), data)

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
        assert_equals(eipa.JSONrepr(), data)

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
        assert_equals(ebsbd.JSONrepr(), data)

    def test_ebs_block_device_valid_standard(self):
        data = {'VolumeType': 'standard'}
        ebsbd = ec2.EBSBlockDevice(
            "test",
        )
        assert_equals(ebsbd.JSONrepr(), data)

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
        assert_equals(ebsbdm.JSONrepr(), data)

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
            VolumeId="1atestme",
            Device="/dev/sda"
        )
        assert_equals(mp.JSONrepr(), data)

#    def test_PrivateIpAddressSpecification_invalid(self):
#        pass
#
#    def test_PrivateIpAddressSpecification_valid(self):
#        pass
#
#    def test_NetworkInterfaceProperty_invalid(self):
#        pass
#
#    def test_NetworkInterfaceProperty_valid(self):
#        pass
#
#    def test_Instance_invalid(self):
#        pass
#
#    def test_Instance_valid(self):
#        pass
#
#    def test_InternetGateway_invalid(self):
#        pass
#
#    def test_InternetGateway_valid(self):
#        pass
#
#    def test_NetworkAcl_invalid(self):
#        pass
#
#    def test_NetworkAcl_valid(self):
#        pass
#
#    def test_ICMP_invalid(self):
#        pass
#
#    def test_ICMP_valid(self):
#        pass
#
#    def test_PortRange_invalid(self):
#        pass
#
#    def test_PortRange_valid(self):
#        pass
#
#    def test_NetworkAclEntry_invalid(self):
#        pass
#
#    def test_NetworkAclEntry_valid(self):
#        pass
#
#    def test_NetworkInterface_invalid(self):
#        pass
#
#    def test_NetworkInterface_valid(self):
#        pass
#
#    def test_NetworkInterfaceAttachment_invalid(self):
#        pass
#
#    def test_NetworkInterfaceAttachment_valid(self):
#        pass
#
#    def test_Route_invalid(self):
#        pass
#
#    def test_Route_valid(self):
#        pass
#
#    def test_RouteTable_invalid(self):
#        pass
#
#    def test_RouteTable_valid(self):
#        pass
#
#    def test_SecurityGroupEgress_invalid(self):
#        pass
#
#    def test_SecurityGroupEgress_valid(self):
#        pass
#
#    def test_SecurityGroupIngress_invalid(self):
#        pass
#
#    def test_SecurityGroupIngress_valid(self):
#        pass
#
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
