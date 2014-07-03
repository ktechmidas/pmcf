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

from pmcf.exceptions import PropertyException
from pmcf.resources.aws import route53

from tests.unit.resources import TestResource


class TestRoute53Resource(TestResource):

    def test_alias_target_valid(self):
        data = {
            'HostedZoneId': 'example.com',
            'DNSName': 'test.example.com',
        }
        at = route53.AliasTarget(
            'example.com',
            'test.example.com',
        )
        assert_equals(at.JSONrepr(), data)

    def test_record_set_type_valid_alias_target(self):
        data = {
            'Properties': {
                'AliasTarget': {
                    'DNSName': 'test.example.com',
                    'HostedZoneId': 'example.com'
                },
                'Comment': 'test',
                'HostedZoneName': 'example.com',
                'Name': 'bar.example.com',
                'Type': 'A'
            },
            'Type': 'AWS::Route53::RecordSet'
        }
        rs = route53.RecordSetType(
            'test',
            AliasTarget=route53.AliasTarget(
                'example.com',
                'test.example.com',
            ),
            Comment='test',
            HostedZoneName='example.com',
            Name='bar.example.com',
            Type='A'
        )
        assert_equals(self._data_for_resource(rs), data)

    def test_record_set_type_valid_resource_records(self):
        data = {
            'Properties': {
                'Comment': 'test',
                'HostedZoneName': 'example.com',
                'Name': 'bar.example.com',
                'ResourceRecords': ['1.2.3.4'],
                'TTL': 300,
                'Type': u'A'
            },
            'Type': 'AWS::Route53::RecordSet'
        }
        rs = route53.RecordSetType(
            'test',
            Comment='test',
            HostedZoneName='example.com',
            Name='bar.example.com',
            ResourceRecords=['1.2.3.4'],
            TTL=300,
            Type='A'
        )
        assert_equals(self._data_for_resource(rs), data)

    def test_record_set_type_invalid_no_name(self):
        rs = route53.RecordSetType(
            'test',
            Comment='test',
            HostedZoneName='example.com',
            ResourceRecords=['1.2.3.4'],
            TTL=300,
            Type='A'
        )
        assert_raises(PropertyException, rs.JSONrepr)

    def test_record_set_type_invalid_resource_records_and_target_alias(self):
        rs = route53.RecordSetType(
            'test',
            Comment='test',
            HostedZoneName='example.com',
            Name='bar.example.com',
            AliasTarget=route53.AliasTarget(
                'example.com',
                'test.example.com',
            ),
            ResourceRecords=['1.2.3.4'],
            TTL=300,
            Type='A'
        )
        assert_raises(PropertyException, rs.JSONrepr)

    def test_record_set_type_invalid_ttl_no_resource_records(self):
        rs = route53.RecordSetType(
            'test',
            Comment='test',
            HostedZoneName='example.com',
            Name='bar.example.com',
            TTL=300,
            Type='A'
        )
        assert_raises(PropertyException, rs.JSONrepr)

    def test_record_set_type_invalid_setid_no_resource_records(self):
        rs = route53.RecordSetType(
            'test',
            Comment='test',
            HostedZoneName='example.com',
            Name='bar.example.com',
            SetIdentifier='blah blah',
            Type='A'
        )
        assert_raises(PropertyException, rs.JSONrepr)

    def test_record_set_type_invalid_resource_records_no_setid_or_ttl(self):
        rs = route53.RecordSetType(
            'test',
            Comment='test',
            HostedZoneName='example.com',
            Name='bar.example.com',
            ResourceRecords=['1.2.3.4'],
            Type='A'
        )
        assert_raises(PropertyException, rs.JSONrepr)

    def test_record_set_valid_alias_target(self):
        data = {
            'AliasTarget': {
                'DNSName': 'test.example.com',
                'HostedZoneId': 'example.com'
            },
            'Comment': 'test',
            'HostedZoneName': 'example.com',
            'Name': 'bar.example.com',
            'Type': 'A'
        }
        rs = route53.RecordSet(
            'test',
            AliasTarget=route53.AliasTarget(
                'example.com',
                'test.example.com',
            ),
            Comment='test',
            HostedZoneName='example.com',
            Name='bar.example.com',
            Type='A'
        )
        assert_equals(self._data_for_resource(rs), data)

    def test_record_set_valid_resource_records(self):
        data = {
            'Comment': 'test',
            'HostedZoneName': 'example.com',
            'Name': 'bar.example.com',
            'ResourceRecords': ['1.2.3.4'],
            'TTL': 300,
            'Type': u'A'
        }
        rs = route53.RecordSet(
            'test',
            Comment='test',
            HostedZoneName='example.com',
            Name='bar.example.com',
            ResourceRecords=['1.2.3.4'],
            TTL=300,
            Type='A'
        )
        assert_equals(self._data_for_resource(rs), data)

    def test_record_set_invalid_no_name(self):
        rs = route53.RecordSet(
            'test',
            Comment='test',
            HostedZoneName='example.com',
            ResourceRecords=['1.2.3.4'],
            TTL=300,
            Type='A'
        )
        assert_raises(PropertyException, rs.JSONrepr)

    def test_record_set_invalid_resource_records_and_target_alias(self):
        rs = route53.RecordSet(
            'test',
            Comment='test',
            HostedZoneName='example.com',
            Name='bar.example.com',
            AliasTarget=route53.AliasTarget(
                'example.com',
                'test.example.com',
            ),
            ResourceRecords=['1.2.3.4'],
            TTL=300,
            Type='A'
        )
        assert_raises(PropertyException, rs.JSONrepr)

    def test_record_set_invalid_ttl_no_resource_records(self):
        rs = route53.RecordSet(
            'test',
            Comment='test',
            HostedZoneName='example.com',
            Name='bar.example.com',
            TTL=300,
            Type='A'
        )
        assert_raises(PropertyException, rs.JSONrepr)

    def test_record_set_invalid_setid_no_resource_records(self):
        rs = route53.RecordSet(
            'test',
            Comment='test',
            HostedZoneName='example.com',
            Name='bar.example.com',
            SetIdentifier='blah blah',
            Type='A'
        )
        assert_raises(PropertyException, rs.JSONrepr)

    def test_record_set_invalid_resource_records_no_setid_or_ttl(self):
        rs = route53.RecordSet(
            'test',
            Comment='test',
            HostedZoneName='example.com',
            Name='bar.example.com',
            ResourceRecords=['1.2.3.4'],
            Type='A'
        )
        assert_raises(PropertyException, rs.JSONrepr)

    def test_record_set_group_valid_zone_id(self):
        data = {
            'Properties': {
                'Comment': 'test',
                'HostedZoneId': 'test-123',
                'RecordSets': []
            },
            'Type': 'AWS::Route53::RecordSetGroup'
        }
        rsg = route53.RecordSetGroup(
            'test',
            HostedZoneId='test-123',
            RecordSets=[],
            Comment='test',
        )
        assert_equals(self._data_for_resource(rsg), data)

    def test_record_set_group_valid_zone_name(self):
        data = {
            'Properties': {
                'Comment': 'test',
                'HostedZoneName': 'test.example.com',
                'RecordSets': []
            },
            'Type': 'AWS::Route53::RecordSetGroup'
        }
        rsg = route53.RecordSetGroup(
            'test',
            HostedZoneName='test.example.com',
            RecordSets=[],
            Comment='test',
        )
        assert_equals(self._data_for_resource(rsg), data)

    def test_record_set_group_invalid_zone_name_and_id(self):
        rsg = route53.RecordSetGroup(
            'test',
            HostedZoneId='test-123',
            HostedZoneName='test.example.com',
            RecordSets=[],
            Comment='test',
        )
        assert_raises(PropertyException, rsg.JSONrepr)

    def test_record_set_group_invalid_no_zone_name_or_id(self):
        rsg = route53.RecordSetGroup(
            'test',
            RecordSets=[],
            Comment='test',
        )
        assert_raises(PropertyException, rsg.JSONrepr)
