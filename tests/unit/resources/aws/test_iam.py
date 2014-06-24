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
from pmcf.resources.aws import iam

from tests.unit.resources import TestResource


class TestIAMResource(TestResource):

    def test_access_key_valid(self):
        data = {
            'Properties': {
                'UserName': 'Fred',
                'Status': 'Active'
            },
            'Type': u'AWS::IAM::AccessKey'
        }
        ak = iam.AccessKey(
            'test',
            UserName='Fred',
            Status='Active'
        )
        assert_equals(self._data_for_resource(ak), data)

    def test_access_key_invalid_no_username(self):
        ak = iam.AccessKey(
            'test'
        )
        assert_raises(PropertyException, ak.JSONrepr)

    def test_access_key_invalid_bad_status(self):
        ak = iam.AccessKey(
            'test',
            UserName='Fred',
            Status='wrong'
        )
        assert_raises(PropertyException, ak.JSONrepr)

    def test_group_valid(self):
        data = {
            'Type': u'AWS::IAM::Group'
        }
        g = iam.Group(
            'test'
        )
        assert_equals(self._data_for_resource(g), data)

    def test_group_valid_path(self):
        data = {
            'Properties': {
                'Path': '/groups/blah/'
            },
            'Type': u'AWS::IAM::Group'
        }
        g = iam.Group(
            'test',
            Path='/groups/blah/'
        )
        assert_equals(self._data_for_resource(g), data)

    def test_group_invalid_bad_path_start(self):
        g = iam.Group(
            'test',
            Path='groups/blah/'
        )
        assert_raises(PropertyException, g.JSONrepr)

    def test_group_invalid_bad_path_end(self):
        g = iam.Group(
            'test',
            Path='/groups/blah'
        )
        assert_raises(PropertyException, g.JSONrepr)

    def test_instance_profile_valid(self):
        data = {
            'Properties': {
                'Path': '/',
                'Roles': ['a', 'b']
            },
            'Type': u'AWS::IAM::InstanceProfile'
        }
        ip = iam.InstanceProfile(
            'test',
            Path='/',
            Roles=['a', 'b']
        )
        assert_equals(self._data_for_resource(ip), data)

    def test_instance_profile_invalid_bad_path_start(self):
        ip = iam.InstanceProfile(
            'test',
            Path='foo/bar/',
            Roles=['a', 'b']
        )
        assert_raises(PropertyException, ip.JSONrepr)

    def test_instance_profile_invalid_bad_path_end(self):
        ip = iam.InstanceProfile(
            'test',
            Path='/foo/bar',
            Roles=['a', 'b']
        )
        assert_raises(PropertyException, ip.JSONrepr)

    def test_instance_profile_invalid_no_path(self):
        ip = iam.InstanceProfile(
            'test',
            Roles=['a', 'b']
        )
        assert_raises(PropertyException, ip.JSONrepr)

    def test_instance_profile_invalid_no_roles(self):
        ip = iam.InstanceProfile(
            'test',
            Path='/'
        )
        assert_raises(PropertyException, ip.JSONrepr)

    def test_policy_type_valid(self):
        data = {
            'Properties': {
                'PolicyDocument': {'a': 'b'},
                'PolicyName': 'test'
            },
            'Type': u'AWS::IAM::Policy'
        }
        pt = iam.PolicyType(
            'test',
            PolicyDocument={'a': 'b'},
            PolicyName='test'
        )
        assert_equals(self._data_for_resource(pt), data)

    def test_policy_type_invalid_no_document(self):
        pt = iam.PolicyType(
            'test',
            PolicyName='test'
        )
        assert_raises(PropertyException, pt.JSONrepr)

    def test_policy_type_invalid_no_name(self):
        pt = iam.PolicyType(
            'test',
            PolicyDocument={'a': 'b'}
        )
        assert_raises(PropertyException, pt.JSONrepr)

    def test_policy_valid(self):
        data = {
            'PolicyDocument': {'a': 'b'},
            'PolicyName': 'test'
        }
        pt = iam.Policy(
            'test',
            PolicyDocument={'a': 'b'},
            PolicyName='test'
        )
        assert_equals(self._data_for_resource(pt), data)

    def test_policy_invalid_no_document(self):
        pt = iam.Policy(
            'test',
            PolicyName='test'
        )
        assert_raises(PropertyException, pt.JSONrepr)

    def test_policy_invalid_no_name(self):
        pt = iam.PolicyType(
            'test',
            PolicyDocument={'a': 'b'}
        )
        assert_raises(PropertyException, pt.JSONrepr)

    def test_role_valid(self):
        data = {
            'Properties': {
                'AssumeRolePolicyDocument': {'a': 'b'},
                'Path': '/'
            },
            'Type': u'AWS::IAM::Role'
        }
        r = iam.Role(
            'test',
            AssumeRolePolicyDocument={'a': 'b'},
            Path='/'
        )
        assert_equals(self._data_for_resource(r), data)

    def test_role_invalid_no_document(self):
        r = iam.Role(
            'test',
            Path='/'
        )
        assert_raises(PropertyException, r.JSONrepr)

    def test_role_invalid_bad_path_start(self):
        r = iam.Role(
            'test',
            Path='foo/bar/',
            AssumeRolePolicyDocument={'a': 'b'},
        )
        assert_raises(PropertyException, r.JSONrepr)

    def test_role_invalid_bad_path_end(self):
        r = iam.Role(
            'test',
            Path='/foo/bar',
            AssumeRolePolicyDocument={'a': 'b'},
        )
        assert_raises(PropertyException, r.JSONrepr)

    def test_role_invalid_no_path(self):
        r = iam.Role(
            'test',
            AssumeRolePolicyDocument={'a': 'b'},
        )
        assert_raises(PropertyException, r.JSONrepr)

    def test_user_valid(self):
        data = {
            'Properties': {
                'Path': '/'
            },
            'Type': u'AWS::IAM::User'
        }
        u = iam.User(
            'test',
            Path='/'
        )
        assert_equals(self._data_for_resource(u), data)

    def test_user_invalid_bad_path_start(self):
        r = iam.User(
            'test',
            Path='foo/bar/',
        )
        assert_raises(PropertyException, r.JSONrepr)

    def test_user_invalid_bad_path_end(self):
        r = iam.User(
            'test',
            Path='/foo/bar',
        )
        assert_raises(PropertyException, r.JSONrepr)

    def test_user_to_group_addition_valid(self):
        data = {
            'Properties': {
                'GroupName': 'test',
                'Users': ['test']
            },
            'Type': u'AWS::IAM::UserToGroupAddition'
        }
        utga = iam.UserToGroupAddition(
            'test',
            GroupName='test',
            Users=['test']
        )
        assert_equals(self._data_for_resource(utga), data)

    def test_user_to_group_addition_invalid_no_group(self):
        utga = iam.UserToGroupAddition(
            'test',
            Users=['test']
        )
        assert_raises(PropertyException, utga.JSONrepr)

    def test_user_to_group_addition_invalid_no_user(self):
        utga = iam.UserToGroupAddition(
            'test',
            GroupName='test',
        )
        assert_raises(PropertyException, utga.JSONrepr)
