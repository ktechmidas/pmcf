# Copyright (c) 2015 Piksel
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

from pmcf.exceptions import PropertyException
from pmcf.resources.aws import elasticache

from tests.unit.resources import TestResource


class TestECResource(TestResource):

    def test_cache_cluster_invalid_bad_name(self):
        assert_raises(PropertyException,
                      elasticache.CacheCluster,
                      'test-test mctest')

    def test_cache_cluster_invalid_no_engine(self):
        ec = elasticache.CacheCluster(
            'test',
            CacheNodeType='cache.m1.small',
            CacheParameterGroupName='pg-1234',
            CacheSubnetGroupName='sgn-12345',
            ClusterName='test',
            VpcSecurityGroupIds=['sg-1234']
        )
        assert_raises(PropertyException, ec.JSONrepr)

    def test_cache_cluster_valid(self):
        data = {
            'Properties': {
                'CacheNodeType': 'cache.m1.small',
                'CacheParameterGroupName': 'pg-1234',
                'CacheSubnetGroupName': 'sgn-12345',
                'ClusterName': 'test',
                'Engine': 'redis',
                'VpcSecurityGroupIds': ['sg-1234']
            },
            'Type': 'AWS::ElastiCache::CacheCluster'
        }

        ec = elasticache.CacheCluster(
            'test',
            CacheNodeType='cache.m1.small',
            CacheParameterGroupName='pg-1234',
            CacheSubnetGroupName='sgn-12345',
            ClusterName='test',
            Engine='redis',
            VpcSecurityGroupIds=['sg-1234']
        )
        assert_equals(self._data_for_resource(ec), data)

    def test_parameter_group_invalid_bad_name(self):
        assert_raises(PropertyException,
                      elasticache.ParameterGroup,
                      'test-test mctest')

    def test_parameter_group_invalid_no_family(self):
        ec = elasticache.ParameterGroup(
            'test',
            Description='test thingy',
            Properties={'a': '1'}
        )
        assert_raises(PropertyException, ec.JSONrepr)

    def test_parameter_group_invalid_no_description(self):
        ec = elasticache.ParameterGroup(
            'test',
            CacheParameterGroupFamily='Redis2.8',
            Properties={'a': '1'}
        )
        assert_raises(PropertyException, ec.JSONrepr)

    def test_parameter_group_invalid_no_properties(self):
        ec = elasticache.ParameterGroup(
            'test',
            CacheParameterGroupFamily='Redis2.8',
            Description='test thingy',
        )
        assert_raises(PropertyException, ec.JSONrepr)

    def test_parameter_group_valid(self):
        data = {
            'Properties': {
                'CacheParameterGroupFamily': 'Redis2.8',
                'Description': 'test thingy',
                'Properties': {'a': '1'}
            },
            'Type': 'AWS::ElastiCache::ParameterGroup'
        }

        ec = elasticache.ParameterGroup(
            'test',
            CacheParameterGroupFamily='Redis2.8',
            Description='test thingy',
            Properties={'a': '1'}
        )
        assert_equals(self._data_for_resource(ec), data)

    def test_security_group_invalid_bad_name(self):
        assert_raises(PropertyException,
                      elasticache.SecurityGroup,
                      'test-test mctest')

    def test_security_group_invalid_no_description(self):
        ec = elasticache.SecurityGroup(
            'test',
        )
        assert_raises(PropertyException, ec.JSONrepr)

    def test_security_group_valid(self):
        data = {
            'Properties': {
                'Description': 'test',
            },
            'Type': 'AWS::ElastiCache::SecurityGroup'
        }
        ec = elasticache.SecurityGroup(
            'test',
            Description='test',
        )
        assert_equals(self._data_for_resource(ec), data)

    def test_security_group_ingress_invalid_bad_name(self):
        assert_raises(PropertyException,
                      elasticache.SecurityGroupIngress,
                      'test-test mctest')

    def test_security_group_ingress_invalid_no_cache_secgroup_name(self):
        ec = elasticache.SecurityGroupIngress(
            'test',
            EC2SecurityGroupName='sg-1234',
            EC2SecurityGroupOwnerId='sg-1235',
        )
        assert_raises(PropertyException, ec.JSONrepr)

    def test_security_group_ingress_invalid_no_ec2_secgroup_name(self):
        ec = elasticache.SecurityGroupIngress(
            'test',
            CacheSecurityGroupName='test',
            EC2SecurityGroupOwnerId='sg-1235',
        )
        assert_raises(PropertyException, ec.JSONrepr)

    def test_security_group_ingress_valid(self):
        data = {
            'Properties': {
                'CacheSecurityGroupName': 'test',
                'EC2SecurityGroupName': 'sg-1234',
                'EC2SecurityGroupOwnerId': 'sg-1235',
            },
            'Type': 'AWS::ElastiCache::SecurityGroupIngress'
        }

        ec = elasticache.SecurityGroupIngress(
            'test',
            CacheSecurityGroupName='test',
            EC2SecurityGroupName='sg-1234',
            EC2SecurityGroupOwnerId='sg-1235',
        )

        assert_equals(self._data_for_resource(ec), data)

    def test_subnet_group_invalid_bad_name(self):
        assert_raises(PropertyException,
                      elasticache.SubnetGroup,
                      'test-test mctest')

    def test_subnet_group_invalid_no_description(self):
        ec = elasticache.SubnetGroup(
            'test',
            SubnetIds=['sn-1234'],
        )
        assert_raises(PropertyException, ec.JSONrepr)

    def test_subnet_group_invalid_no_subnetids(self):
        ec = elasticache.SubnetGroup(
            'test',
            Description='test',
        )
        assert_raises(PropertyException, ec.JSONrepr)

    def test_subnet_group_valid(self):
        data = {
            'Properties': {
                'Description': 'test',
                'SubnetIds': ['sn-1234'],
            },
            'Type': 'AWS::ElastiCache::SubnetGroup'
        }

        ec = elasticache.SubnetGroup(
            'test',
            Description='test',
            SubnetIds=['sn-1234'],
        )

        assert_equals(self._data_for_resource(ec), data)
