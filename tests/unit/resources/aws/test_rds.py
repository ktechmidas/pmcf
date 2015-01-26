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
from troposphere import Ref

from pmcf.exceptions import PropertyException
from pmcf.resources.aws import rds

from tests.unit.resources import TestResource


class TestRDSResource(TestResource):

    def test_db_instance_invalid_no_allocated_storage(self):
        dbi = rds.DBInstance(
            'test',
            Iops=1000,
            DBInstanceClass='test',
            Engine='test',
            MasterUsername='test',
            MasterUserPassword='test',
        )
        assert_raises(PropertyException, dbi.JSONrepr)

    def test_db_instance_invalid_bad_iops(self):
        dbi = rds.DBInstance(
            'test',
            AllocatedStorage='100',
            Iops=1152,
            DBInstanceClass='test',
            Engine='test',
            MasterUsername='test',
            MasterUserPassword='test',
        )
        assert_raises(PropertyException, dbi.JSONrepr)

    def test_db_instance_invalid_storage(self):
        dbi = rds.DBInstance(
            'test',
            AllocatedStorage='150',
            Iops=1000,
            DBInstanceClass='test',
            Engine='test',
            MasterUsername='test',
            MasterUserPassword='test',
        )
        assert_raises(PropertyException, dbi.JSONrepr)

    def test_db_instance_invalid_two_secgroups(self):
        dbi = rds.DBInstance(
            'test',
            AllocatedStorage='100',
            Iops=1000,
            DBInstanceClass='test',
            Engine='test',
            MasterUsername='test',
            MasterUserPassword='test',
            DBSecurityGroups=['default'],
            VPCSecurityGroups=[Ref('foo')],
        )
        assert_raises(PropertyException, dbi.JSONrepr)

    def test_db_instance_invalid_multiaz_and_az(self):
        dbi = rds.DBInstance(
            'test',
            AllocatedStorage='100',
            AvailabilityZone='a',
            Iops=1000,
            DBInstanceClass='MySQL',
            Engine='MySQL',
            MasterUsername='test',
            MasterUserPassword='test',
            MultiAZ=True,
        )
        assert_raises(PropertyException, dbi.JSONrepr)

    def test_db_instance_valid(self):
        data = {
            'Properties': {
                'AllocatedStorage': '100',
                'DBInstanceClass': 'MySQL',
                'Engine': 'MySQL',
                'Iops': 1000,
                'MasterUserPassword': 'test',
                'MasterUsername': 'test'
            },
            'Type': 'AWS::RDS::DBInstance'
        }
        dbi = rds.DBInstance(
            'test',
            AllocatedStorage='100',
            Iops=1000,
            DBInstanceClass='MySQL',
            Engine='MySQL',
            MasterUsername='test',
            MasterUserPassword='test',
        )
        assert_equals(self._data_for_resource(dbi), data)

    def test_db_parameter_group_invalid_params(self):
        dbpg = {
            "Description": 'test',
            "Parameters": {'foo': 'bar'},
            "Womble": 'test',
        }
        assert_raises(PropertyException, rds.DBParameterGroup, "test", **dbpg)

    def test_db_parameter_group_invalid_missing_family(self):
        dbpg = rds.DBParameterGroup(
            'test',
            Description='test',
            Parameters={'foo': 'bar'},
        )
        assert_raises(PropertyException, dbpg.JSONrepr)

    def test_db_parameter_group_valid(self):
        data = {
            'Properties': {
                'Description': 'test',
                'Family': 'test',
                'Parameters': {
                    'foo': 'bar'
                }
            },
            'Type': 'AWS::RDS::DBParameterGroup'
        }
        dbpg = rds.DBParameterGroup(
            'test',
            Description='test',
            Family='test',
            Parameters={'foo': 'bar'},
        )
        assert_equals(self._data_for_resource(dbpg), data)

    def test_db_subnet_invalid_no_description(self):
        dbsg = rds.DBSubnetGroup(
            'test',
            SubnetIds=['testme-123'],
        )
        assert_raises(PropertyException, dbsg.JSONrepr)

    def test_db_subnet_invalid_no_subnets(self):
        dbsg = rds.DBSubnetGroup(
            'test',
            DBSubnetGroupDescription='test',
        )
        assert_raises(PropertyException, dbsg.JSONrepr)

    def test_db_subnet_valid(self):
        data = {
            'Properties': {
                'DBSubnetGroupDescription': 'test',
                'SubnetIds': ['testme-123'],
            },
            'Type': 'AWS::RDS::DBSubnetGroup'
        }
        dbsg = rds.DBSubnetGroup(
            'test',
            DBSubnetGroupDescription='test',
            SubnetIds=['testme-123'],
        )
        assert_equals(self._data_for_resource(dbsg), data)

    def test_rds_security_group_invalid_secgroup_name_and_id(self):
        rdssg = rds.RDSSecurityGroup(
            'test',
            EC2SecurityGroupId='testsg-123',
            EC2SecurityGroupName='testsg'
        )
        assert_raises(PropertyException, rdssg.JSONrepr)

    def test_rds_security_group_invalid_secgroup_name_and_cidr(self):
        rdssg = rds.RDSSecurityGroup(
            'test',
            CIDRIP='0.0.0.0/0',
            EC2SecurityGroupName='testsg'
        )
        assert_raises(PropertyException, rdssg.JSONrepr)

    def test_rds_security_group_invalid_secgroup_id_and_cidr(self):
        rdssg = rds.RDSSecurityGroup(
            'test',
            EC2SecurityGroupId='testsg-123',
            CIDRIP='0.0.0.0/0'
        )
        assert_raises(PropertyException, rdssg.JSONrepr)

    def test_rds_security_group_valid_secgroup_id(self):
        data = {'EC2SecurityGroupId': 'testsg-123'}
        rdssg = rds.RDSSecurityGroup(
            'test',
            EC2SecurityGroupId='testsg-123'
        )
        assert_equals(self._data_for_resource(rdssg), data)

    def test_rds_security_group_valid_cidr(self):
        data = {'CIDRIP': '0.0.0.0/0'}
        rdssg = rds.RDSSecurityGroup(
            'test',
            CIDRIP='0.0.0.0/0'
        )
        assert_equals(self._data_for_resource(rdssg), data)

    def test_db_security_group_invalid_no_description(self):
        dbsg = rds.DBSecurityGroup(
            'test',
            EC2VpcId='testvpc-123',
            DBSecurityGroupIngress=[
                rds.RDSSecurityGroup(
                    'test',
                    CIDRIP='0.0.0.0/0'
                )
            ],
        )
        assert_raises(PropertyException, dbsg.JSONrepr)

    def test_db_security_group_invalid_no_rules(self):
        dbsg = rds.DBSecurityGroup(
            'test',
            EC2VpcId='testvpc-123',
            GroupDescription='test security group'
        )
        assert_raises(PropertyException, dbsg.JSONrepr)

    def test_db_security_group_valid(self):
        data = {
            'Properties': {
                'DBSecurityGroupIngress': [
                    {'CIDRIP': '0.0.0.0/0'}
                ],
                'EC2VpcId': 'testvpc-123',
                'GroupDescription': 'test security group'
            },
            'Type': 'AWS::RDS::DBSecurityGroup'
        }
        dbsg = rds.DBSecurityGroup(
            'test',
            EC2VpcId='testvpc-123',
            DBSecurityGroupIngress=[
                rds.RDSSecurityGroup(
                    'test',
                    CIDRIP='0.0.0.0/0'
                )
            ],
            GroupDescription='test security group'
        )
        assert_equals(self._data_for_resource(dbsg), data)

    def test_db_security_group_ingress_invalid_secgroup_name_and_id(self):
        dbsgi = rds.DBSecurityGroupIngress(
            'test',
            DBSecurityGroupName='testdbsg-123',
            EC2SecurityGroupName='testsg',
            EC2SecurityGroupId='testsg-123',
        )
        assert_raises(PropertyException, dbsgi.JSONrepr)

    def test_db_security_group_ingress_invalid_secgroup_name_and_cidr(self):
        dbsgi = rds.DBSecurityGroupIngress(
            'test',
            DBSecurityGroupName='testdbsg-123',
            CIDRIP='0.0.0.0/0',
            EC2SecurityGroupName='testsg',
        )
        assert_raises(PropertyException, dbsgi.JSONrepr)

    def test_db_security_group_ingress_invalid_secgroup_id_and_cidr(self):
        dbsgi = rds.DBSecurityGroupIngress(
            'test',
            DBSecurityGroupName='testdbsg-123',
            CIDRIP='0.0.0.0/0',
            EC2SecurityGroupId='testsg-123'
        )
        assert_raises(PropertyException, dbsgi.JSONrepr)

    def test_db_security_group_ingress_invalid_no_secgroup(self):
        dbsgi = rds.DBSecurityGroupIngress(
            'test',
            EC2SecurityGroupId='testsg-123'
        )
        assert_raises(PropertyException, dbsgi.JSONrepr)

    def test_db_security_group_ingress_valid_secgroup_id(self):
        data = {
            'Properties': {
                'EC2SecurityGroupId': 'testsg-123',
                'DBSecurityGroupName': 'testdbsg-123'
            },
            'Type': 'AWS::RDS::DBSecurityGroupIngress'
        }

        dbsgi = rds.DBSecurityGroupIngress(
            'test',
            DBSecurityGroupName='testdbsg-123',
            EC2SecurityGroupId='testsg-123'
        )
        assert_equals(self._data_for_resource(dbsgi), data)

    def test_db_security_group_ingress_valid_cidr(self):
        data = {
            'Properties': {
                'CIDRIP': '0.0.0.0/0',
                'DBSecurityGroupName': 'testdbsg-123'
            },
            'Type': 'AWS::RDS::DBSecurityGroupIngress'
        }

        dbsgi = rds.DBSecurityGroupIngress(
            'test',
            DBSecurityGroupName='testdbsg-123',
            CIDRIP='0.0.0.0/0'
        )
        assert_equals(self._data_for_resource(dbsgi), data)

    def test_db_instance_bad_name(self):
        assert_raises(PropertyException, rds.DBInstance, 'bad-name')

    def test_db_parameter_group_bad_name(self):
        assert_raises(PropertyException, rds.DBParameterGroup, 'bad-name')

    def test_db_subnet_group_bad_name(self):
        assert_raises(PropertyException, rds.DBSubnetGroup, 'bad-name')

    def test_rds_security_group_bad_name(self):
        assert_raises(PropertyException, rds.RDSSecurityGroup, 'bad-name')

    def test_db_security_group_bad_name(self):
        assert_raises(PropertyException, rds.DBSecurityGroup, 'bad-name')

    def test_db_security_group_ingress_bad_name(self):
        assert_raises(
            PropertyException,
            rds.DBSecurityGroupIngress, 'bad-name')
